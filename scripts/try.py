#!/usr/bin/env python3

import sys
sys.path.append("../")
sys.path.append("../../distiller_modified")

import torch

import distiller.models.cifar10.plain_cifar as pc
from common.nnTools import get_layersName_list, print_weight_dist

import models.cifar10.LeNet as LeNet

device="cpu"

network = LeNet.LeNet()
network = network.to(device)
checkpoint = torch.load('../models/checkpoints/LeNet_CIFAR10_epoch100.tar', map_location=device)
network.load_state_dict(checkpoint['model_state_dict'])

mod=pc.plain20_cifar_nobn()
l=get_layersName_list(mod)
i=0
for name, module in network.named_parameters():
    if i==2:
        print_weight_dist(module,"./",name="lay1")
        mod2=module
    i+=1

for name, module in network.named_parameters():
    print_weight_dist(module,"./",multiple=True, conf_layer=mod2, num_bins=100)
    exit()