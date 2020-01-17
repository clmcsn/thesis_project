#!/usr/bin/env python3

import os
import pathlib
import sys
sys.path.append("../")

tomask = False

if tomask:
    path = "../../distiller_mod_v2"
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
from common.mask_util import MaskType, stringMask_to_list, _make_mask
from common.hw_lib import printer_2s

device = 'cuda:1' if torch.cuda.is_available() else 'cpu'

batch_size = 50
bits = 8 #data bits
aw_bits = 8
acc_bits = 32

rep_string = "QuantMode: {}\t MaskMode: {}\t Mask: {}\t RangeCorrection:{}\t Correct: {}\t Accuracy: {}\n"

network_name = "resnet32"
checkpoint_path = "../models/checkpoints/ref_models/"
checkpoint_name = "{}_CIFAR10_bestAccuracy.tar".format(network_name)

network = models.resnet_cifar.resnet32_cifar()
network = network.to(device) 
checkpoint = torch.load(checkpoint_path+checkpoint_name, map_location=device)
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

test_preds = get_all_preds(network, data_loader,device=device)
preds_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(train_set.targets)).sum().item()

print(preds_correct)