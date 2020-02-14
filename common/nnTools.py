#!/usr/bin/env python3
import torch
from torch import tensor
import matplotlib
import matplotlib.pyplot as plt
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from scipy.stats import skewnorm
from collections import OrderedDict
#cm = confusion matrix
#classes = classes that will be x and y axes
#
"""should be used as entry of a dictionary which key is the name of the layer"""
class layerStat():
    def __init__(   self,inChannels,outChannels,
                    inFmap_s,kernel_s=None,stride=None):
        self.inChannels = inChannels
        self.outChannels = outChannels
        self.inFmap_s = inFmap_s
        self.kernel_s = kernel_s
        self.stride = stride
    def get_numMult(self):
        if self.kernel_s:
            n = (self.kernel_s**2)*self.inChannels*((self.inFmap_s-self.kernel_s)/self.stride + 1)*self.outChannels
        else:
            n = self.inChannels*self.outChannels*self.inFmap_s
        return n 

class dumping_layer(nn.Module):

    def __init__(self,name):
        super(dumping_layer, self).__init__()
        self.name = name
    
    def forward(self,x):
        #torch.save(x,"{}.dump".format(self.name))
        return x

def get_network_mults(net_desc):
    mults=0
    for l in net_desc.values():
        mults+=l.get_numMult()
    return mults

"""get_layer_dict(fname)
    DESCRIPTION
        Out of a network description file provides a dictionary with layer names as key and layerStat object as entry
        File must be of the following type:
            "layer_name   
                ...stats
                ..."
        PLEASE USE TEMPLATES FOR WRITING NEW FILES
    INPUT
        Needs as inputs:
        fname: file name with complete network description
    OUTPUT
        dic: dictionary where key is the layer name while entry is layerStat object"""
def get_layer_dict(fname):
    dic=OrderedDict()
    with open(fname,"r") as in_pointer:
        first = True
        for line in in_pointer:
            if line[0].isspace(): #if it's a property
                fields = line.split(":")
                if "inChannels" in fields[0]:
                    inChannels = int(fields[1])
                elif "outChannels" in fields[0]:
                    outChannels = int(fields[1])
                elif "inFmap_s" in fields[0]:
                    inFmap_s = int(fields[1])
                elif "kernel_s" in fields[0]:
                    kernel_s = int(fields[1])
                elif "stride" in fields[0]:
                    stride = int(fields[1])
            else:
                if first:
                    first = False
                else:
                    dic[name] = layerStat(inChannels,outChannels,
                                            inFmap_s,kernel_s,stride)
                name = "".join(line.split()) #deletes all the spaces
                kernel_s = None
                stride = None
        dic[name] = layerStat(inChannels,outChannels,
                                            inFmap_s,kernel_s,stride)
    return dic

def getSparsity(tensor):
    shape=tensor.size()
    tensor = tensor.flatten()
    sparsity = float((tensor==0).sum())/int(tensor.size(0))
    return sparsity


def get_all_preds(model, loader, device="cpu"):
    all_preds = torch.tensor([]).to(device) #new pytorch sensor
    for batch in loader:
        images, labels = batch
        images = images.to(device)
        labels = labels.to(device)
        preds=model(images)
        all_preds = torch.cat(
            (all_preds, preds)
            ,dim=0)
    return all_preds

def get_layersName_list(model):
    l=[]
    for name, module in model.named_modules():
        if isinstance(module, (nn.Conv2d, nn.Conv3d, nn.Linear)):
            l+=[name]
    return l

"""test(model, data_loader)
    DESCRIPTION
        Provides correct prediction out of test set (data_loader) for the provided network 
    INPUT
        Needs as inputs:
        model: network to test
        data_loader: test set
        batch_size: how many sample must be classified at every cycle
        device: where test should run
    OUTPUT
        correct: how many correct prediction where produced"""
def test(model, test_set, batch_size=50, device="cpu"):
    data_loader= torch.utils.data.DataLoader(
                                                test_set
                                                ,shuffle=False
                                                ,batch_size=batch_size)
    preds = get_all_preds(model, data_loader,device=device)
    correct = preds.argmax(dim=1).eq(torch.LongTensor(test_set.targets).to(device)).sum().item()
    return correct
