#!/usr/bin/env python3

import os
import pathlib
import sys
sys.path.append("../")
sys.path.append("../../distiller_mod_v3")

from copy import deepcopy

import torch
import torchvision
import torchvision.transforms as transforms

import distiller
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode
import distiller.utils
import distiller.models.cifar10 as models

import models.cifar10.LeNet as LeNet
from common.nnTools import get_all_preds, get_layersName_list, make_weightDistr_comparHistgram
from common.mask_util import MaskType, stringMask_to_list, _make_mask, MaskTable, guided_MaskTable_creator , set_specific_layers
from common.hw_lib import printer_2s


device='cuda:1'
batch_size=50
bits=8 #data bits
aw_bits=8
acc_bits=32
rep_string="QuantMode: {}\t MaskMode: {}\t Mask: {}\t RangeCorrection:{}\t Correct: {}\t Accuracy: {}\n"


def bit_string_inverter(string):
    new=""
    for i in string:
        if i=="0":
            new+="1"
        else:
            new+="0"
    return new

def make_path(quant_mode,mask_mode,mask,correctRange):
    qm=str(quant_mode)
    qm=qm.split(".")[1]
    mm=str(mask_mode)
    mm=mm.split(".")[1]
    return "/".join([qm,mm,mask,str(correctRange)])

network_name = "vgg11"
checkpoint_path = "../models/checkpoints/"
checkpoint_name = "{}_CIFAR10_bestAccuracy_9148.pt".format(network_name)
#checkpoint_name = "{}_CIFAR10_bestAccuracy_9358.pt".format(network_name)
mask_perLayer_config_file = "../models/mask_config/{}_end.mc".format(network_name)
#dont_touch=["fc","conv1"]
dont_touch=["features0","classifier"]

network = models.vgg_cifar.vgg11_cifar()
network = network.to("cpu")
network = network.eval() 
checkpoint = torch.load(checkpoint_path+checkpoint_name, map_location="cpu")
network.load_state_dict(checkpoint['model_state_dict'])

transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

train_set = torchvision.datasets.CIFAR10( #we are fetching our datasets
    root='../../data/CIFAR10'
    ,train=False  #where data will be located
    ,download=True              #download if is not present offline(run only the first time)
    ,transform=transform_test
)

data_loader= torch.utils.data.DataLoader(
    train_set
    ,shuffle=False
    ,batch_size=batch_size)

quant_mode_list = [LinearQuantMode.ASYMMETRIC_UNSIGNED]
mask_mode_list = [MaskType.SIMPLE_MASK,MaskType.ROUND_DOWN,MaskType.ROUND_UP,MaskType.MOD_ROUND_UP,MaskType.MINIMUM_DISTANCE]
dummy_input = (torch.zeros([1,3,32,32]))

test_preds = get_all_preds(network, data_loader)
ref_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets)).sum().item()

with open("../reports/data_{}_CIFAR10_postTrainMasking_firstLastLayerUnmasked.txt".format(network_name),"w") as log_pointer:
    log_pointer.write("Reference accuracy = {}\n".format(ref_correct))
    for quant_mode in quant_mode_list:
        signed= quant_mode != LinearQuantMode.ASYMMETRIC_UNSIGNED
        if signed:
            start_string = 2**(bits-1)
        else:
            start_string = 1
        #quantizer_ref = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
        #                                                    mode=quant_mode,scale_approx_mult_bits=bits)
        #quantizer_ref.prepare_model(dummy_input)
        for mask_mode in mask_mode_list:
            for i in range(start_string,2**bits): #all possible mask
                mask = printer_2s(i,bits)
                mask = bit_string_inverter(mask)
                ones = mask.count("1")
                if(ones<=bits-4 and ones!=0):
                    #instance the quantized
                    for j in range(2):
                        correct=bool(j)
                        guided_MaskTable_creator(network,mask_perLayer_config_file, stringMask_to_list(mask), gui=False)
                        set_specific_layers(dont_touch,mask_perLayer_config_file)
                        mask_table=MaskTable(quant_mode, mask_mode, stringMask_to_list(mask), correct, network,)
                        quantizer = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                                            mode=quant_mode, mask_table=mask_table,
                                                            scale_approx_mult_bits=bits)
                        quantizer.model.to(device)
                        quantizer.prepare_model(dummy_input)
                        quantizer.model.eval()

                        """for layer in get_layersName_list(network):
                            path=make_path(quant_mode,mask_mode,mask,j)
                            pathlib.Path("../reports/weightDistribution_customLeNet_analysis1/"+path).mkdir(parents=True, exist_ok=True)
                            make_weightDistr_comparHistgram(getattr(quantizer_ref.model,layer).wrapped_module.weight,
                                                            getattr(quantizer.model,layer).wrapped_module.weight,
                                                            name=layer,
                                                            save=True,
                                                            path="../reports/weightDistribution_customLeNet_analysis1/"+path)"""
                        test_preds = get_all_preds(quantizer.model, data_loader,device=device)
                        preds_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets).to(device)).sum().item()
                        accuracy =  preds_correct/len(train_set)
                        log_pointer.write(rep_string.format(quant_mode,mask_mode,mask,correct,preds_correct,accuracy))
                        print(rep_string.format(quant_mode,mask_mode,mask,correct,preds_correct,accuracy))
                        del quantizer
                        del mask_table
        #del quantizer_ref            
