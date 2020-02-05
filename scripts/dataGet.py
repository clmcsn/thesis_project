#!/usr/bin/env python3

import os
import sys
sys.path.append("../")

from copy import deepcopy

import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms

sys.path.append("../../distiller_mod_v4")
import distiller
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode
import distiller.utils

import models.cifar10.vgg_cifar as vgg
from common.nnTools import get_all_preds, get_layersName_list, make_weightDistr_comparHistgram
from common.mask_util import MaskType, stringMask_to_list, _make_mask, MaskTable, guided_MaskTable_creator , set_specific_layers, balanceNetwork
from common.hw_lib import printer_2s

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-s',type=str, help="To be used for single execution")
parser.add_argument('-q',type=str, help="To be used for single execution")
parser.parse_args()

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
                cont = el.split(".")[0] #funziona se non ci sono altri punti oltre a quelli della estensione!!!
                num = cont[len(cont)-1]
                os.rename(out_path+"/"+el,out_path+"/"+new_name+"_{}".format(num)+".dump")

def remove_dump(path,dump_name):
    dirlist=os.listdir(path)
    for el in dirlist:
        if dump_name in el:
            os.remove(path+"/"+dump_name)

device = 'cuda:1' if torch.cuda.is_available() else 'cpu'
#