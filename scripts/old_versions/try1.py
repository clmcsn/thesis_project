#!/usr/bin/env python3

import os
import pathlib
import sys
sys.path.append("../")
sys.path.append("../../distiller_mod_v4")

from copy import deepcopy

import torch
import torchvision
import torchvision.transforms as transforms

import distiller
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode
import distiller.utils
import distiller.models.cifar10 as models


import models.cifar10.vgg_cifar as vgg 
from common.nnTools import get_all_preds

from common.nnTools import get_all_preds, get_layersName_list, make_weightDistr_comparHistgram
from common.mask_util import MaskType, stringMask_to_list, _make_mask, MaskTable, guided_MaskTable_creator , set_specific_layers, balanceNetwork
from common.hw_lib import printer_2s

device='cpu'
batch_size=100
bits=8
aw_bits=8
acc_bits=32
rep_string="QuantMode: {}\tQuantBits: {}\t Correct: {}\t Accuracy: {}\n"

network_name = "vgg11bn"
checkpoint_path = "../models/checkpoints/"
checkpoint_name = "{}_CIFAR10_bestAccuracy_9240.pt".format(network_name)
network = vgg.vgg11_bn_cifar("./data/ref_model")
network = network.to("cpu")
network = network.eval() 
checkpoint = torch.load(checkpoint_path+checkpoint_name, map_location="cpu")
network.load_state_dict(checkpoint['model_state_dict'])

dummy_input = (torch.zeros([1,3,32,32]))
#generate accuracy without masking first and last layer
maskConfig_path = "../models/mask_config/"
config_fname = "{}.mc".format(network_name)
mask = "00000111"
unmasked_layers = ["features.0","classifier"]
quant_mode = LinearQuantMode.ASYMMETRIC_UNSIGNED
mask_mode = MaskType.SIMPLE_MASK
guided_MaskTable_creator(network,maskConfig_path+config_fname, mask, gui=False)
set_specific_layers(unmasked_layers,maskConfig_path+config_fname)
mask_table = MaskTable(quant_mode, mask_mode, [] , False, network, mask_file=maskConfig_path+config_fname)
quantizer = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                    mode=quant_mode, mask_table=mask_table,
                                    scale_approx_mult_bits=bits)
quantizer.model.to(device)
quantizer.prepare_model(dummy_input)
quantizer.model.eval()