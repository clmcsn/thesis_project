#!/usr/bin/env python3

import os
import sys
sys.path.append("../")
sys.path.append("../../distiller_mod_v4")

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

def remove_dump(path,dump_name):
    dirlist=os.listdir(path)
    for el in dirlist:
        if dump_name in el:
            os.remove(path+"/"+dump_name)

def balanceNetwork(ref_model,child_model,test_set,batch_size=50,device='cpu'):
    sf_dump_file = "./data/scale_factor.dump"
    activation_ref   = "./data/ref_act/ref_model_{}.dump"
    activation_child1 = "./data/child1_act/child_model1_{}.dump"
    
    #fetching correction batch
    data_loader= torch.utils.data.DataLoader(
    test_set
    ,shuffle=False
    ,batch_size=batch_size)

    batch = next(iter(data_loader))
    image, label = batch

    #obtaining activations from models
    pred_ref = ref_quantized.model(image)
    save_dump("./data","ref_model","./data/ref_act")
    os.remove(sf_dump_file) #need to remove the file dump of scaling factors so there would be just one
    pred_child1 = quantized_child1.model(image)
    save_dump("./data","ref_model","./data/child1_act",new_name="child_model1")
    pred_child2 = quantized_child2.model(image)
    #correcting loop
    i=0 #need for knowing which layer we are in
    for layer_name, layer in child_model.named_modules():
        if isinstance(layer, (nn.Conv2d, nn.Conv3d, nn.Linear)):
            layer_coord = layer_name.split(".")
            #retriving scale factor
            with open(sf_dump_file,"r") as in_pointer:
                for k in range(i+1): #need to fetch how many scale factors as layer we are in
                    sf = float(in_pointer.readline())
            try:
                #fetching activations
                print(activation_ref)
                ref = torch.load(activation_ref.format(i), map_location=device) 
                child = torch.load(activation_child1.format(i), map_location=device)
                for j in range(ref.size(1)): #for every element of the bias=num_output_channels
                    r = ref[:,j,:,:] #for every image of the batch, select j output fmap 
                    c = child[:,j,:,:]
                    print(c.size())
                    print(c)
                    exit()
                    d = torch.sum(r-c)#/ref.size(0) #perform the distance
                    layer.bias[j] = layer.bias[j] + d
                #upload distiller backup
                getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).base_b_q = (layer.bias/sf)-getattr(getattr(quantized_child1.model,layer_coord[0]),layer_coord[1]).b_zero_point
            except FileNotFoundError: #case for output probabilities
                for j in range(10): #numbers_of_class=10
                    d = torch.sum(pred_ref[:,j]-pred_child1[:,j])#/pred_ref.size(0)
                    layer.bias[j] = layer.bias[j] + d
                getattr(quantized_child1.model,layer_coord[0]).base_b_q = (layer.bias/sf)-getattr(quantized_child1.model,layer_coord[0]).b_zero_point
            #getting again activation from layer
            os.remove("./data/scale_factor.dump") #removing the dumping factor
            pred_child1 = child_model(image) #getting new activation values
            save_dump("./data","ref_model","./data/child1_act",new_name="child_model1")
            i+=1
device = 'cpu'
#device = 'cuda:1'
bits = 8 
aw_bits = 8
acc_bits = 32

transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

test_set = torchvision.datasets.CIFAR10( #we are fetching our datasets
    root='../../data/CIFAR10'
    ,train=False  #where data will be located
    ,download=True              #download if is not present offline(run only the first time)
    ,transform=transform_test
)

#setting up the model
network_name = "vgg11"
checkpoint_path = "../models/checkpoints/"
checkpoint_name = "{}_CIFAR10_bestAccuracy_9240.pt".format(network_name)
dummy_input = (torch.ones([1,3,32,32]))

#loading reference model
ref_network = vgg.vgg11_bn_cifar("./data/ref_model")
checkpoint = torch.load(checkpoint_path+checkpoint_name, map_location=device)
ref_network.load_state_dict(checkpoint['model_state_dict'])

#apply quantization
ref_mask_table=MaskTable(LinearQuantMode.ASYMMETRIC_UNSIGNED, MaskType.MINIMUM_DISTANCE, [] , False, ref_network)
ref_quantized = PostTrainLinearQuantizer( deepcopy(ref_network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                    mode=LinearQuantMode.ASYMMETRIC_UNSIGNED, mask_table=ref_mask_table,
                                    scale_approx_mult_bits=bits)
ref_quantized.prepare_model(dummy_input)
ref_quantized.model.eval()

child_mask_table=MaskTable(LinearQuantMode.ASYMMETRIC_UNSIGNED, MaskType.MINIMUM_DISTANCE, [3,2,1,0] , True, ref_network)
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

#balanceNetwork(ref_model,child_model,test_set,batch_size=50,device='cpu'):
balanceNetwork(ref_quantized.model,
                quantized_child1.model,
                test_set,
                batch_size=1,
                device=device)

batch_size=50
#fetching batches for inference
data_loader= torch.utils.data.DataLoader(
test_set
,shuffle=False
,batch_size=batch_size)

"""ref_preds = get_all_preds(ref_quantized.model, data_loader,device=device)
ref_correct = ref_preds.argmax(dim=1).eq(torch.LongTensor(test_set.targets)).sum().item()
print("Ref accuracy :{}".format(ref_correct))"""

bad_preds = get_all_preds(quantized_child2.model, data_loader,device=device)
bad_correct = bad_preds.argmax(dim=1).eq(torch.LongTensor(test_set.targets)).sum().item()
print("Bad accuracy :{}".format(bad_correct))

new_preds = get_all_preds(quantized_child1.model, data_loader,device=device)
new_correct = new_preds.argmax(dim=1).eq(torch.LongTensor(test_set.targets)).sum().item()
print("New accuracy :{}".format(new_correct))
