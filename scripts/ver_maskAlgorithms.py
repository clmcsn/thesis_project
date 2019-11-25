#!/usr/bin/env python3

import sys
sys.path.append("../")
from common.mask_util import mask_param, MaskType, stringMask_to_list
import torch

#########SETTINGS##########
m_type=[MaskType.MINIMUM_DISTANCE]
bits=4
signed=True
ver=True

def bit_string_inverter(string):
    new=""
    for i in string:
        if i=="0":
            new+="1"
        else:
            new+="0"
    return new
if ver==True:
    with open("../reports/mask_examples.txt","w") as out_log:    
        for mask_t in m_type:
            out_log.write("All combination for {} type.\n".format(mask_t))
            for i in range(2**(bits-1),2**bits):
                string="{0:b}".format(i)
                string = bit_string_inverter(string)
                out_log.write("\tAll combination for {} mask.\n".format(string))
                for i in range(2**bits):
                    t = torch.tensor([i], dtype=torch.int)
                    mask_param(t
                                ,stringMask_to_list(string)
                                ,mask_type = mask_t
                                ,dynamic=4
                                ,signed=signed)
                    out_log.write("\t\t{0:b} ---> {1:b}.\n".format(i,int(t)))
                