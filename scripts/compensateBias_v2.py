#!/usr/bin/env python3

import os
import sys
sys.path.append("../")
sys.path.append("../../distiller_mod_v5")

from copy import deepcopy

import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms

import distiller
import distiller.models.cifar10 as models
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode
import distiller.utils

import models.cifar10.vgg_cifar as vgg
from common.nnTools import get_all_preds, get_layersName_list, make_weightDistr_comparHistgram
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
                os.rename(out_path+"/"+el,out_path+"/"+new_name+"_{}".format(l)+".dump")

def remove_dump(path,dump_name):
    dirlist=os.listdir(path)
    for el in dirlist:
        if dump_name in el:
            os.remove(path+"/"+dump_name)

def balanceNetwork(ref_model,child_model,test_set,batch_size=50,device='cpu'):
    sf_dump_file = "./data/scale_factor.dump"
    activation_ref   = "./data/r_act/ref_{}.dump"
    activation_child = "./data/child_act/child_{}.dump"
    shutil.rmtree('./data/')
    os.mkdir('./data')
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
    save_dump("./data","ref","./data/r_act")
    #need to remove the file dump of scaling factors so there would be just one
    os.remove(sf_dump_file)
    pred_child = child_model(image)
    save_dump("./data","ref","./data/child_act",new_name="child")
    #correcting loop
    i=0 #needed for the scaling factor! 
    for layer_name, layer in child_model.named_modules():
        if isinstance(layer, (nn.Conv2d, nn.Conv3d, nn.Linear)):
            lc = layer_name.split(".") #it will be called as the dumping file + .wrapped_module
            #retriving scale factor
            with open(sf_dump_file,"r") as in_pointer:
                for k in range(i+1): #need to fetch how many scale factors as layer we are in
                    sf = float(in_pointer.readline())
            try:
                ref = torch.load(activation_ref.format(".".join((lc[0],lc[1]))), map_location=device) 
                child = torch.load(activation_child.format(".".join((lc[0],lc[1]))), map_location=device)
                for j in range(ref.size(1)): #for every element of the bias=num_output_channels
                    r = ref[:,j,:,:] #for every image of the batch, select j output fmap 
                    c = child[:,j,:,:]
                    #average but without square ---> to try that distance
                    d = torch.sum(r-c)/ref.size(0)/ref.size(2)/ref.size(3)#*((r==0).sum()) #perform the distance
                    layer.bias[j] = layer.bias[j] + d
                #upload distiller backup
                getattr(getattr(child_model,lc[0]),lc[1]).base_b_q = (layer.bias/sf)-getattr(getattr(child_model,lc[0]),lc[1]).b_zero_point #this works only for vgg
            except FileNotFoundError: #case for output probabilities
                ref = torch.load(activation_ref.format(lc[0]), map_location=device) 
                child = torch.load(activation_child.format(lc[0]), map_location=device)
                for j in range(10): #numbers_of_class=10
                    r = ref[:,j]
                    c = child[:,j]
                    d = torch.sum(r-c)/pred_ref.size(0)
                    layer.bias[j] = layer.bias[j] + d
                getattr(child_model,lc[0]).base_b_q = (layer.bias/sf)-getattr(child_model,lc[0]).b_zero_point
            #getting again activation from layer
            os.remove("./data/scale_factor.dump") #removing the scaling factor that will be produced
            pred_child = child_model(image) #getting new activation values
            save_dump("./data","ref","./data/child_act",new_name="child")
            i+=1
    os.remove("./save_act")

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
checkpoint_name = "{}_CIFAR10_bestAccuracy_9238.pt".format(network_name)
dummy_input = (torch.ones([1,3,32,32]))

#loading reference model
ref_network = models.vgg_cifar.vgg11_bn_cifar()
ref_network = ref_network.eval()
checkpoint = torch.load(checkpoint_path+checkpoint_name, map_location=device)
ref_network.load_state_dict(checkpoint['model_state_dict'])

#apply quantization
ref_mask_table=MaskTable(LinearQuantMode.ASYMMETRIC_UNSIGNED, MaskType.MINIMUM_DISTANCE, [] , False, ref_network)
ref_quantized = PostTrainLinearQuantizer( deepcopy(ref_network), bits_activations=aw_bits, bits_parameters=aw_bits, bits_accum=acc_bits,
                                    mode=LinearQuantMode.ASYMMETRIC_UNSIGNED, mask_table=ref_mask_table,
                                    scale_approx_mult_bits=bits)
ref_quantized.prepare_model(dummy_input)
ref_quantized.model.eval()

child_mask_table=MaskTable(LinearQuantMode.ASYMMETRIC_UNSIGNED, MaskType.MD_FAST, [4,2,1,0] , False, ref_network)
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
                batch_size=500,
                device=device)

batch_size=50
#fetching batches for inference
data_loader= torch.utils.data.DataLoader(
test_set
,shuffle=False
,batch_size=batch_size)

new_preds = get_all_preds(quantized_child1.model, data_loader,device=device)
new_correct = new_preds.argmax(dim=1).eq(torch.LongTensor(test_set.targets)).sum().item()
print("New accuracy 1:{}".format(new_correct))

balanceNetwork(ref_quantized.model,
                quantized_child1.model,
                test_set,
                batch_size=500,
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
print("New accuracy 2:{}".format(new_correct))
