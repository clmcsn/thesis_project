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
from common.nnTools import get_all_preds, get_layersName_list, make_weightDistr_comparHistgram
from common.mask_util import MaskType, stringMask_to_list, _make_mask
from common.hw_lib import printer_2s


device='cpu'
batch_size=50
bits=8 #data bits
aw_bits=8
acc_bits=32

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
quantizer_ref = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                                            mode=LinearQuantMode.ASYMMETRIC_UNSIGNED,scale_approx_mult_bits=bits)
quantizer_ref.prepare_model(dummy_input)
quantizer_ref.model.eval()

quantizer = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                                            mode=LinearQuantMode.ASYMMETRIC_UNSIGNED,mask=MaskType.MINIMUM_DISTANCE, maskList=stringMask_to_list("00000011"),
                                                            correctRange=False, scale_approx_mult_bits=bits)
quantizer.prepare_model(dummy_input)
quantizer.model.eval()
                        
#test_preds = get_all_preds(quantizer.model, data_loader,device=device)
#test_refPreds = get_all_preds(quantizer_ref.model, data_loader,device=device)
#preds_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets)).sum().item()
#accuracy =  preds_correct/len(train_set)
                        
                        
for layer in get_layersName_list(network):
    path=layer
    pathlib.Path("../reports/debug/"+path).mkdir(parents=True, exist_ok=True)
    make_weightDistr_comparHistgram(getattr(quantizer_ref.model,layer).wrapped_module.weight,
                                    getattr(quantizer.model,layer).wrapped_module.weight,
                                    name=layer,
                                    save=True,
                                    path="../reports/debug/"+path)            
