#!/usr/bin/env python3

import os
import pathlib
import sys
sys.path.append("../")

tomask = True

if tomask:
    path = "../../distiller_mod_v3"
else:
    path = "../../distiller"

sys.path.append(path)

from copy import deepcopy
import torch
import torchvision
import torchvision.transforms as transforms

import distiller
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode
import distiller.utils
import distiller.models.cifar10 as models

from common.nnTools import get_all_preds, get_layersName_list, make_weightDistr_comparHistgram
from common.mask_util import MaskTable, MaskType, stringMask_to_list, _make_mask, guided_MaskTable_creator
from common.hw_lib import printer_2s

#device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
device = "cpu"
batch_size = 100
bits = 8 #data bits
aw_bits = 8
acc_bits = 32

rep_string = "QuantMode: {}\t MaskMode: {}\t Mask: {}\t RangeCorrection:{}\t Correct: {}\t Accuracy: {}\n"

network_name = "resnet32"
checkpoint_path = "../models/checkpoints/"
#checkpoint_name = "{}_CIFAR10_bestAccuracy_9148.pt".format(network_name)
checkpoint_name = "{}_CIFAR10_bestAccuracy_9358.pt".format(network_name)

network = models.resnet_cifar.resnet32_cifar()
network = network.to(device)
network = network.eval() 
checkpoint = torch.load(checkpoint_path+checkpoint_name, map_location=device)
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


test_preds = get_all_preds(network, data_loader,device=device)
ref_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets)).sum().item()
print(ref_correct)
mask_config_file="../models/mask_config/{}_end.mc".format(network_name)
guided_MaskTable_creator(network, mask_config_file,std_mask="00000010")
mask_table=MaskTable(distiller.quantization.LinearQuantMode.SYMMETRIC, MaskType.ROUND_UP, [], False, network, mask_file=mask_config_file)
quant_net = PostTrainLinearQuantizer(   network, bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                                            mode=LinearQuantMode.ASYMMETRIC_UNSIGNED,
                                                            mask_table= mask_table, 
                                                            scale_approx_mult_bits=bits)
"""quant_net = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                                            mode=LinearQuantMode.ASYMMETRIC_UNSIGNED,
                                                            mask=MaskType.MOD_ROUND_UP, 
                                                            maskList=[1],
                                                            correctRange=False, scale_approx_mult_bits=bits)"""
dummy_input = (torch.zeros([1,3,32,32]))
quant_net.prepare_model(dummy_input)
quant_net.model.eval()
test_preds = get_all_preds(quant_net.model, data_loader,device=device)
preds_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets)).sum().item()
print(preds_correct)
