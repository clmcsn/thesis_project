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
from distiller.quantization.q_utils import linear_dequantize, linear_quantize_clamp

import models.cifar10.vgg_cifar as vgg
from common.nnTools import get_all_preds, get_layersName_list, make_weightDistr_comparHistgram
from common.mask_util import MaskType, stringMask_to_list, _make_mask, MaskTable, guided_MaskTable_creator , set_specific_layers
from common.hw_lib import printer_2s

from copy import deepcopy

import shutil

def save_dump(in_path,dump_name,out_path,new_name=None):
    dirlist=os.listdir(in_path)
    to_move=[]
    for el in dirlist:
        if dump_name in el:
            to_move+=[el]
    try:
        os.mkdir(out_path)
    except FileExistsError:
        pass
    for el in to_move:
        shutil.move(os.path.join(in_path,el),os.path.join(out_path,el))
    if new_name:
        dirlist=os.listdir(out_path)
        for el in dirlist:
            if dump_name in el:
                cont = el.split(".")[0] #funziona se non ci sono altri punti
                num = cont[len(cont)-1]
                os.rename(out_path+"/"+el,out_path+"/"+new_name+"_{}".format(num)+".dump")

#setting up target hardware for simulations + running
device = 'cpu'      #for local
#device = 'cuda:1'  #for lopo
bits = 8 
aw_bits = 8
acc_bits = 32

#fetching dataset
batch_size=100
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

#here only one image is going to be used
batch = next(iter(data_loader))
image, label = batch

#setting up the model
network_name = "vgg11"
checkpoint_path = "../models/checkpoints/"
checkpoint_name = "{}_CIFAR10_bestAccuracy_9240.pt".format(network_name)
dummy_input = (torch.ones([1,3,32,32]))

#loading reference model
ref_network = vgg.vgg11_bn_cifar("./data/ref_model")
checkpoint = torch.load(checkpoint_path+checkpoint_name, map_location=device)
ref_network.load_state_dict(checkpoint['model_state_dict'])


#print(getattr(ref_network.features,"0").bias.data)

#apply quantization
ref_mask_table=MaskTable(LinearQuantMode.ASYMMETRIC_UNSIGNED, MaskType.MINIMUM_DISTANCE, [] , False, ref_network)
ref_quantized = PostTrainLinearQuantizer( deepcopy(ref_network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                    mode=LinearQuantMode.ASYMMETRIC_UNSIGNED, mask_table=ref_mask_table,
                                    scale_approx_mult_bits=bits)
ref_quantized.prepare_model(dummy_input)
ref_quantized.model.eval()

child_mask_table=MaskTable(LinearQuantMode.ASYMMETRIC_UNSIGNED, MaskType.MINIMUM_DISTANCE, [2] , False, ref_network)
#loading child model
quantized_child1 = PostTrainLinearQuantizer( deepcopy(ref_network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                    mode=LinearQuantMode.ASYMMETRIC_UNSIGNED, mask_table=child_mask_table,
                                    scale_approx_mult_bits=bits)
quantized_child1.prepare_model(dummy_input)
quantized_child1.model.eval()
quantized_child2 = PostTrainLinearQuantizer( deepcopy(ref_network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                    mode=LinearQuantMode.ASYMMETRIC_UNSIGNED, mask_table=child_mask_table,
                                    scale_approx_mult_bits=bits)
quantized_child2.prepare_model(dummy_input)
quantized_child2.model.eval()

activation_ref   = "./data/ref_act/ref_model_{}.dump"
activation_child1 = "./data/child1_act/child_model1_{}.dump"
activation_child2 = "./data/child2_act/child_model2_{}.dump"

#print(getattr(ref_quantized.model.features,"0").wrapped_module.bias.data)

pred_ref = ref_quantized.model(image)
save_dump("./data","ref_model","./data/ref_act")
pred_child1 = quantized_child1.model(image)
os.remove("./data/scale_factor.dump")
save_dump("./data","ref_model","./data/child1_act",new_name="child_model1")
pred_child2 = quantized_child2.model(image)
save_dump("./data","ref_model","./data/child2_act",new_name="child_model2")
layer_coord = "features.5".split(".")

"""ref_act_lay1 = torch.load(activation_ref.format(1), map_location=device)
child_act_lay1 = torch.load(activation_child1.format(1), map_location=device)
child_act_lay2 = torch.load(activation_child2.format(1), map_location=device)
#print(getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).base_b_q)
for j in range(ref_act_lay1.size(1)):
    b = getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).wrapped_module.bias[j]
    r = ref_act_lay1[0][j][:][:]
    c = child_act_lay1[0][j][:][:]
    #d = torch.dist(r,c,2)
    d = torch.sum(r-c)#/ref_act_lay1.size(1)
    #d = 5
    #quantized_child1.model.features.0.wrapped_module.bias.data[j] = quantized_child1.model.feature.0.wrapped_module.bias.data[j] + d
    getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).wrapped_module.bias[j].add_(250*d)
#print(getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).base_b_q )
#print(getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).wrapped_module.bias.data)
with open("./data/scale_factor.dump","r") as in_pointer:
    sf = float(in_pointer.readline())
    sf = float(in_pointer.readline())
sf = torch.tensor([sf])
#print(getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).wrapped_module.bias.data)
#self.wrapped_module.bias/bias_requant_scale-self.b_zero_point
getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).base_b_q = getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).wrapped_module.bias.data/302-getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).b_zero_point
quantized_child1.model(image)
#print(getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).wrapped_module.bias.data)
save_dump("./data","ref_model","./data/child1_act",new_name="child_model1")
child_act_lay1 = torch.load(activation_child1.format(1), map_location=device)
d2=torch.dist(ref_act_lay1,child_act_lay2,2)
d1=torch.dist(ref_act_lay1,child_act_lay1,2)
d3=torch.dist(child_act_lay1,child_act_lay2,2)
print(d1)
print(d2)
print(d3)"""

sf_dump_file = "./data/scale_factor.dump"
i=0
for layer_name, layer in quantized_child1.model.named_modules():
    if isinstance(layer, (nn.Conv2d, nn.Conv3d, nn.Linear)):
        layer_coord = layer_name.split(".")
        #retriving scale factor
        with open(sf_dump_file,"r") as in_pointer:
            for k in range(i+1):
                sf = float(in_pointer.readline())
        try:
            ref = torch.load(activation_ref.format(i), map_location=device)
            child = torch.load(activation_child1.format(i), map_location=device)
            for j in range(ref.size(1)): #for every element of the bias=num_output_channels
                r = ref[:,j,:,:]
                c = child[:,j,:,:]
                d = torch.sum(r-c)
                #d = torch.dist(r,c,2)
                layer.bias[j] = layer.bias[j] + d
            #need to upload distiller backup
            getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).base_b_q = (layer.bias/sf)-getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).b_zero_point
        except FileNotFoundError: #case for output probabilities
            for j in range(10): #numbers_of_class=10
                d = torch.sum(pred_ref[:,j]-pred_child1[:,j])
                layer.bias[j] = layer.bias[j] + d
            #getattr(quantized_child1.model,layer_coord[0]).base_b_q = (layer.bias/sf)-getattr(quantized_child1.model,layer_coord[0]).b_zero_point
        #getting again activation from layer
        os.remove("./data/scale_factor.dump")
        pred_child1 = quantized_child1.model(image)
        save_dump("./data","ref_model","./data/child1_act",new_name="child_model1")
        i+=1
#print(pred_ref)
pred_child1 = quantized_child1.model(image)
#print(pred_child1)
#print(pred_child2)
correct_ref = pred_ref.argmax(dim=1).eq(label).sum().item()
correct_child1 = pred_child1.argmax(dim=1).eq(label).sum().item()
correct_child2 = pred_child2.argmax(dim=1).eq(label).sum().item()
print(correct_ref, correct_child1, correct_child2)