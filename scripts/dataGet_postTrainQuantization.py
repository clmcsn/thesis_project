#!/usr/bin/env python3

import os
import pathlib
import sys
sys.path.append("../")
sys.path.append("../../distiller")

from copy import deepcopy

import torch
import torchvision
import torchvision.transforms as transforms

import distiller
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode
import distiller.utils
import distiller.models.cifar10 as models


import models.cifar10.LeNet as LeNet
from common.nnTools import get_all_preds

device='cuda:1'
batch_size=50
bits=8
acc_bits=32
rep_string="QuantMode: {}\tQuantBits: {}\t Correct: {}\t Accuracy: {}\n"

network_name = "resnet32"
checkpoint_path = "../models/checkpoints/"
checkpoint_name = "{}_CIFAR10_bestAccuracy_9358.pt".format(network_name)

network = models.resnet_cifar.resnet32_cifar()
network = network.to("cpu")
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
    ,transform = transform_test)

data_loader= torch.utils.data.DataLoader(
    train_set
    ,shuffle=False
    ,batch_size=batch_size)

test_preds = get_all_preds(network, data_loader,device=device)
ref_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets)).sum().item()

dummy_input = (torch.zeros([1,3,32,32]))
quant_mode_list = [LinearQuantMode.SYMMETRIC,LinearQuantMode.ASYMMETRIC_UNSIGNED,LinearQuantMode.ASYMMETRIC_SIGNED]

with open("../reports/data_resnet32_CIFAR10_postTrainQuantizing.txt","w") as log_pointer:
    log_pointer.write("Reference accuracy = {}\n".format(ref_correct))
    for quant_mode in quant_mode_list:
        for qw_bits in range(4,bits+1):
            quantizer = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=bits, bits_parameters=qw_bits, bits_accum=acc_bits,
                                                            mode=quant_mode,scale_approx_mult_bits=bits)
            quantizer.model.to(device)
            quantizer.prepare_model(dummy_input)
            quantizer.model.eval()
            test_preds = get_all_preds(quantizer.model, data_loader,device=device)
            preds_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets).to(device)).sum().item()
            accuracy =  preds_correct/len(train_set)
            log_pointer.write(rep_string.format(quant_mode,qw_bits,preds_correct,accuracy))
            del quantizer
