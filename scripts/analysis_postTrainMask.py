#!/usr/bin/env python3

import sys
sys.path.append("../")
sys.path.append("../../distiller_modified")

from copy import deepcopy

import torch
import torchvision
import torchvision.transforms as transforms

import distiller
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode
import distiller.utils

import models.cifar10.LeNet as LeNet
from common.nnTools import get_all_preds
from common.mask_util import MaskType, stringMask_to_list, _make_mask
from common.hw_lib import printer_2s


device='cpu'
batch_size=50
bits=8 #data bits
aw_bits=8
acc_bits=32
rep_string="QuantMode: {}\t MaskMode: {}\t Mask: {}\t Correct: {}\t Accuracy: {}\n"


def bit_string_inverter(string):
    new=""
    for i in string:
        if i=="0":
            new+="1"
        else:
            new+="0"
    return new

network = LeNet.LeNet()
network = network.to(device)
checkpoint = torch.load('../models/checkpoints/LeNet_CIFAR10_epoch100.tar', map_location=device)
network.load_state_dict(checkpoint['model_state_dict'])

train_set = torchvision.datasets.CIFAR10( #we are fetching our datasets
    root='../../data/CIFAR10'
    ,train=False  #where data will be located
    ,download=True              #download if is not present offline(run only the first time)
    ,transform=transforms.Compose([ #transformation of data to tensor
        transforms.ToTensor()
    ])
)

data_loader= torch.utils.data.DataLoader(
    train_set
    ,batch_size=batch_size)

quant_mode_list = [LinearQuantMode.SYMMETRIC,LinearQuantMode.ASYMMETRIC_UNSIGNED,LinearQuantMode.ASYMMETRIC_SIGNED]
mask_mode_list = [MaskType.SIMPLE_MASK,MaskType.ROUND_DOWN,MaskType.ROUND_UP,MaskType.MOD_ROUND_UP,MaskType.MINIMUM_DISTANCE]
dummy_input = (torch.zeros([1,3,32,32]))

with open("../reports/analysis_postTrainMasking.txt","w") as log_pointer:
    for quant_mode in quant_mode_list:
        signed= quant_mode != LinearQuantMode.ASYMMETRIC_UNSIGNED
        if signed:
            start_string = 2**(bits-1)
        else:
            start_string = 1
        for mask_mode in mask_mode_list:
            for i in range(start_string,2**bits): #all possible mask
                mask = printer_2s(i,bits)
                mask = bit_string_inverter(mask)
                ones = mask.count("1")
                if(ones<=bits-3):
                    #instance the quantized
                    quantizer = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                                            mode=quant_mode,mask=mask_mode, maskList=stringMask_to_list(mask),
                                                            scale_approx_mult_bits=bits)
                    quantizer.prepare_model(dummy_input)
                    quantizer.model.eval()
                    test_preds = get_all_preds(quantizer.model, data_loader)
                    preds_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets)).sum().item()
                    accuracy =  preds_correct/len(train_set)
                    log_pointer.write(rep_string.format(quant_mode,mask_mode,mask,preds_correct,accuracy))
                    del quantizer