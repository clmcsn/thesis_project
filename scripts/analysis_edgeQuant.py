#!/usr/bin/env python3

import os
import pathlib
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

device='cpu'
batch_size=50
bits=8
acc_bits=32
rep_string="QuantMode: {}\tQuantBits: {}\t Correct: {}\t Accuracy: {}\n"

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

dummy_input = (torch.zeros([1,3,32,32]))

quant_mode_list = [LinearQuantMode.SYMMETRIC,LinearQuantMode.ASYMMETRIC_UNSIGNED,LinearQuantMode.ASYMMETRIC_SIGNED]

with open("../reports/analysisCustomLeNet_postTrainQuantizing.txt","w") as log_pointer:
    for quant_mode in quant_mode_list:
        for qw_bits in range(4,bits):
            quantizer = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=bits, bits_parameters=qw_bits, bits_accum=acc_bits,
                                                            mode=quant_mode,scale_approx_mult_bits=bits)
            quantizer.prepare_model(dummy_input)
            quantizer.model.eval()
            test_preds = get_all_preds(quantizer.model, data_loader,device=device)
            preds_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets)).sum().item()
            accuracy =  preds_correct/len(train_set)
            log_pointer.write(rep_string.format(quant_mode,qw_bits,preds_correct,accuracy))
            del quantizer