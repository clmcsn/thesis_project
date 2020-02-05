#!/usr/bin/env python3

import sys
import os
sys.path.append("../common")
sys.path.append("../")
sys.path.append("../../distiller_mod_v4")
import torch 
import torchvision
import torchvision.transforms as transforms

from nnTools import getSparsity
import models.cifar10.vgg_cifar as vgg 


import distiller
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode, ClipMode
import distiller.utils

from common.mask_util import MaskType, stringMask_to_list, _make_mask, MaskTable, guided_MaskTable_creator , set_specific_layers
from common.hw_lib import printer_2s
 
dump_path="./data/dummy"

batch_size=1

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

batch = next(iter(data_loader))
image, label = batch

network = vgg.vgg11_bn_cifar(dump_path)
network_name = "vgg11bn"
checkpoint_path = "../models/checkpoints/"
checkpoint_name = "{}_CIFAR10_bestAccuracy_9240.pt".format(network_name)
checkpoint = torch.load(checkpoint_path+checkpoint_name, map_location="cpu")
network.load_state_dict(checkpoint['model_state_dict'])
ref_mask_table=MaskTable(LinearQuantMode.ASYMMETRIC_UNSIGNED, MaskType.MINIMUM_DISTANCE, [] , False, network)
bits = 8 
aw_bits = 8
acc_bits = 32
ref_quantized = PostTrainLinearQuantizer( network, bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                    mode=LinearQuantMode.ASYMMETRIC_SIGNED, mask_table=ref_mask_table,
                                    scale_approx_mult_bits=bits)
dummy_input = (torch.ones([1,3,32,32]))
ref_quantized.prepare_model(dummy_input)
ref_quantized.model.eval()
"""for name, e in network.named_modules():
    print(name, e)
exit()"""
pred = network(image)
dirlist=os.listdir("./data")

dirlist.sort()
for e in dirlist:
    if "dummy" in e:
        t = torch.load("./data"+"/"+e,map_location="cpu")
        print(t[:,1,:,:])
        print(getSparsity(t))
        print(t.size())
        exit()