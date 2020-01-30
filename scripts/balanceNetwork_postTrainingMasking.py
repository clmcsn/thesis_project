#!/usr/bin/env python3

import os
import sys
sys.path.append("../")
sys.path.append("../../distiller_mod_v3")

from copy import deepcopy

import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms

import distiller
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode
import distiller.utils

import models.cifar10.vgg_cifar as vgg
from common.nnTools import get_all_preds, get_layersName_list, make_weightDistr_comparHistgram
from common.mask_util import MaskType, stringMask_to_list, _make_mask, MaskTable, guided_MaskTable_creator , set_specific_layers
from common.hw_lib import printer_2s

device = 'cpu'
#device = 'cuda:1'
batch_size = 1
bits = 8 
aw_bits = 8
acc_bits = 32

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

network_name = "vgg11"
checkpoint_path = "../models/checkpoints/"
checkpoint_name = "{}_CIFAR10_bestAccuracy_9240.pt".format(network_name)
dummy_input = (torch.zeros([1,3,32,32]))

#loading reference model
network = vgg.vgg11_bn_cifar("./data/ref_model")
checkpoint = torch.load(checkpoint_path+checkpoint_name, map_location="cpu")
network.load_state_dict(checkpoint['model_state_dict'])

mask_table=MaskTable(LinearQuantMode.ASYMMETRIC_UNSIGNED, MaskType.MINIMUM_DISTANCE, [] , False, network)
quantizer = PostTrainLinearQuantizer( network, bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                    mode=LinearQuantMode.ASYMMETRIC_UNSIGNED, mask_table=mask_table,
                                    scale_approx_mult_bits=bits)

quantizer.model.to(device)
quantizer.prepare_model(dummy_input)
quantizer.model.eval()

#saving reference activation
pred_ref = quantizer.model(image)
del network
del quantizer
del mask_table

#loading model to be masked
network = vgg.vgg11_bn_cifar("./data/child_model")
network = network.eval() 
checkpoint = torch.load(checkpoint_path+checkpoint_name, map_location="cpu")
network.load_state_dict(checkpoint['model_state_dict'])

mask_table=MaskTable(LinearQuantMode.ASYMMETRIC_UNSIGNED, MaskType.MINIMUM_DISTANCE, [3] , False, network,)
quantizer = PostTrainLinearQuantizer( network, bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                    mode=LinearQuantMode.ASYMMETRIC_UNSIGNED, mask_table=mask_table,
                                    scale_approx_mult_bits=bits)

quantizer.model.to(device)
quantizer.prepare_model(dummy_input)
quantizer.model.eval()

#saving reference activation
pred_child = quantizer.model(image)

activation_ref   = "./data/ref_model_{}.dump"
activation_child = "./data/child_model_{}.dump"
i=0

print(pred_child)

for layer_name, layer in quantizer.model.named_modules():
    if isinstance(layer, (nn.Conv2d, nn.Conv3d, nn.Linear)):
        layer_coord = layer_name.split(".")
        try:
            ref = torch.load(activation_ref.format(i), map_location=device)
            child = torch.load(activation_child.format(i), map_location=device)
            for j in range(ref.size(1)):
                r = ref[0][j][:][:]
                c = child[0][j][:][:]
                #d = torch.dist(r,c,2)
                d = torch.sum(r-c)
                layer.bias[j] = layer.bias[j] + d
            #print(getattr(getattr(quantizer.model,layer_coord[0]),layer_coord[1]).wrapped_module.bias.data)
            getattr(getattr(quantizer.model,layer_coord[0]),layer_coord[1]).wrapped_module.bias.data = layer.bias.data
        except FileNotFoundError:
            for j in range(len(pred_ref)):
                d = torch.dist(pred_ref[j],pred_child[j],2)
                layer.bias[j] = layer.bias[j] + d
            getattr(quantizer.model,layer_coord[0]).wrapped_module.bias.data = layer.bias.data
        #saving reference activation
        pred_child = quantizer.model(image)
        i+=1
print(pred_ref)
pred_child = quantizer.model(image)
print(pred_child)

