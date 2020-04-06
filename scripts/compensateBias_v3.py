#!/usr/bin/env python3

import os
import sys
import json
#path conf will be 
with open("../common/conf_path.json") as j_conf:
    path_conf = json.load(j_conf)

for p in path_conf["appends"]:
    sys.path.append(p)

from copy import deepcopy

import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms

from quantization import PostTrainLinearQuantizer, LinearQuantMode

import distiller
import distiller.models.cifar10 as models
import models.cifar10.vgg_cifar as vgg
from common.nnTools import get_all_preds, get_layersName_list
from common.mask_util import MaskType, stringMask_to_list, _make_mask, MaskTable, guided_MaskTable_creator , set_specific_layers
from common.hw_lib import printer_2s

import shutil

#dump_name should be something that ALL the dumping file have
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
                cont = el[0:len(el)-5] #drops extension
                l = cont.split("_")[1] #drops reference string
                os.rename(out_path+el,out_path+new_name+"_{}".format(l)+".dump")

def balanceNetwork(ref_model,child_model,test_set,batch_size=50,device='cpu'):
    
    os.mkdir(path_conf["dumps"])
    
    #tell libraries to save activations 
    with open("./save_act","w") as validity_act:
        pass
    
    #fetching correction batch
    data_loader= torch.utils.data.DataLoader(
    test_set
    ,shuffle=False
    ,batch_size=batch_size)
    batch = next(iter(data_loader))
    image, label = batch

    #obtaining activations from models
    pred_ref = ref_model(image)
    save_dump(path_conf["dumps"],path_conf["ref_dumps_file"].split("_")[0],path_conf["ref_dumps"])
    pred_child = child_model(image)
    save_dump(path_conf["dumps"],path_conf["ref_dumps_file"].split("_")[0],path_conf["mask_dumps"],new_name="child")
    i=0 #needed for the scaling factor
    for layer_name, layer in child_model.named_modules(): #for every module
        if isinstance(layer, (nn.Conv2d, nn.Conv3d, nn.Linear)): # if it is an instance
            #retriving scale factor
            with open(path_conf["dumps"]+path_conf["sf_dump_file"],"r") as in_pointer:
                for k in range(i+1): #need to fetch how many scale factors as layer we are in
                    sf = float(in_pointer.readline())
            lc = layer_name.split(".")
            o_layer_name=".".join(lc[:-1])
            ref     = torch.load(path_conf["ref_dumps"]+path_conf["ref_dumps_file"].format(o_layer_name), map_location=device) 
            child   = torch.load(path_conf["mask_dumps"]+path_conf["mask_dumps_file"].format(o_layer_name), map_location=device)
            if isinstance(layer,nn.Conv2d):  #case of convolutional layers 
                for j in range(ref.size(1)): #for every element of the bias=num_output_channels
                    r = ref[:,j,:,:] #for every image of the batch, select j output fmap 
                    c = child[:,j,:,:]
                    #average but without square ---> to try that distance
                    d = torch.sum(r-c)/ref.size(0)/ref.size(2)/ref.size(3)#*((r==0).sum()) #perform the distance
                    layer.bias[j] = layer.bias[j] + d
            if isinstance(layer,nn.Linear): #case of fully connected layers
                for j in range(ref.size(1)): #numbers_of_class=10
                    r = ref[:,j]
                    c = child[:,j]
                    d = torch.sum(r-c)/ref.size(0)
                    layer.bias[j] = layer.bias[j] + d
            #upload distiller backup
            if len(lc)-1==1:              #case of layer name composed by one word
                getattr(child_model,lc[0]).base_b_q = (layer.bias/sf)-getattr(child_model,lc[0]).b_zero_point
            if len(lc)-1==2:               #case of layer name composed by two words
                getattr(getattr(child_model,lc[0]),lc[1]).base_b_q = (layer.bias/sf)-getattr(getattr(child_model,lc[0]),lc[1]).b_zero_point #this works only for vgg
            if len(lc)-1==3:               #case of layer name composed by three words
                getattr(getattr(getattr(child_model,lc[0]),lc[1]),lc[2]).base_b_q = (layer.bias/sf)-getattr(getattr(getattr(child_model,lc[0]),lc[1]),lc[2]).b_zero_point #this works only for vgg
            #getting again activation from layer
            os.remove(path_conf["dumps"]+path_conf["sf_dump_file"]) #removing the scaling factor that will be produced
            pred_child = child_model(image) #getting new activation values
            save_dump(path_conf["dumps"],path_conf["ref_dumps_file"].split("_")[0],path_conf["mask_dumps"],new_name="child")
            i+=1
    #cleaning activation
    os.remove("./save_act")
    shutil.rmtree(path_conf["dumps"])

device = 'cpu'
#device = 'cuda:1'
bits = 8 
aw_bits = 8
acc_bits = 32

transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
])

dataset = "CIFAR10"
test_set = torchvision.datasets.CIFAR10( #we are fetching our datasets
    root=path_conf["datasets"]+dataset
    ,train=False  #where data will be located
    ,download=True              #download if is not present offline(run only the first time)
    ,transform=transform_test
)

#setting up the model
network_name = "vgg11bn"
accuracy = "9240"
dummy_input = (torch.ones([1,3,32,32]))

#loading reference model to be copied
ref_network = vgg.vgg11_bn_cifar("")
ref_network = ref_network.eval()
checkpoint = torch.load(path_conf["checkpoint"]+path_conf["ba_checkpoint_file"].format(model=network_name,dataset=dataset,accuracy=accuracy), map_location=device)
ref_network.load_state_dict(checkpoint['model_state_dict'])

#quantizing reference model
ref_mask_table=MaskTable(LinearQuantMode.ASYMMETRIC_UNSIGNED, MaskType.ARC, ref_network, [], False)
ref_quantized = PostTrainLinearQuantizer( deepcopy(ref_network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                    mode=LinearQuantMode.ASYMMETRIC_UNSIGNED, mask_table=ref_mask_table,
                                    scale_approx_mult_bits=bits)
ref_quantized.prepare_model(dummy_input)
ref_quantized.model.eval()

child_mask_table=MaskTable(LinearQuantMode.ASYMMETRIC_UNSIGNED, MaskType.ARC, ref_network, [2,1,0] , False)
#loading child model
quantized_child = PostTrainLinearQuantizer( deepcopy(ref_network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                    mode=LinearQuantMode.ASYMMETRIC_UNSIGNED, mask_table=child_mask_table,
                                    scale_approx_mult_bits=bits)
quantized_child.prepare_model(dummy_input)
quantized_child.model.eval()

#compensating the model
balanceNetwork(ref_quantized.model,
            quantized_child.model,
            test_set,
            batch_size=10,
            device=device)