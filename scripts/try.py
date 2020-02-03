#!/usr/bin/env python3

import sys
import os
sys.path.append("../common")
import torch 
from nnTools import getSparsity
 
dump_path="./data/ref_act"

dirlist=os.listdir(dump_path)
dirlist.sort()
for e in dirlist:
    t = torch.load(dump_path+"/"+e,map_location="cpu")
    print(t)
    exit()
    print(getSparsity(t))