#!/usr/bin/env python3

from enum import Enum
import torch

class MaskType(Enum):
     MASK = 1
     ROUND_DOWN = 2
     MINIMUM_DISTANCE = 3

def _stringMask_to_list(stringMask):
    bit_to_mask=[]
    for i, char in enumerate(stringMask):
        if char=='1':
            bit_to_mask+=[i]
    return bit_to_mask

def _make_mask(bit_to_mask):
    mask=0
    for bit in bit_to_mask:
        mask+=(1<<bit)
    mask=~mask
    return mask


def get_masked_param(quant_param, bit_to_mask, mask_type=MaskType.MASK ,dynamic=0):

    #quant_param pre processing
    btm=bit_to_mask.copy()
    fake_param=quant_param.clone().detach().flatten().to(torch.int)
    if mask_type==MaskType.MASK:
        mask=_make_mask(bit_to_mask)
        for element in fake_param:
            element&=mask
    elif mask_type==MaskType.ROUND_DOWN:
        

    return fake_param.view(quant_parameter.size()).to(quant_parameter.dtype)