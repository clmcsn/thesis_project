#!/usr/bin/env python3

from enum import Enum
import torch

class MaskType(Enum):
     SIMPLE_MASK = 1
     ROUND_DOWN = 2
     ROUND_UP = 3
     MOD_ROUND_UP = 4
     MINIMUM_DISTANCE = 5


"""stringMask_to_list(stringMask)

 DESCRIPTION
    Converts a string indicating which bits have to be masked to a list of same bit positions.
    e.g. "00100100" (MSB first) becomes bit_to_mask=[5,2]
 INPUT
    Needs as inputs:
       stringMask:  string of bit, MSB first, where '1' indicates which bit has to be masked
 OUTPUT
    bit to mask: list of positions of bit that have to be masked. MSB first."""
def stringMask_to_list(stringMask):
    bit_to_mask=[]
    for i, char in enumerate(stringMask[::-1]):
        if char=='1':
            bit_to_mask+=[i]
    bit_to_mask.reverse()
    return bit_to_mask

"""_make_mask(bit_to_mask)
 DESCRIPTION
    Makes a mask (int type) from bit_to_mask
    e.g. bit_to_mask=[5,2] (b8"00100100") --> ~(36)
 INPUT
    Needs as inputs:
       bit to mask: list of positions of bit that have to be masked. MSB first.
 OUTPUT
    mask to be used with & operator to an int element"""
def _make_mask(bit_to_mask):
    #works even if bit_to_mask is empty!!!(returns 111111111)
    mask=0
    for bit in bit_to_mask:
        mask+=(1<<bit)
    mask=~mask
    return mask

"""_elm_mask_round_down(element, bit_to_mask)
 DESCRIPTION
    Masks "element" according to "bit_to_mask" following the round down algorithm.
    Operations are done in place. 
 INPUT
    Needs as inputs:
        element:     torch.tensor conteining single dimension single element 
        bit to mask: list of positions of bit that have to be masked. MSB first.
 OUTPUT
    No outputs, operation done in place in element input parameter"""

"""_elm_mask_round_up(element, bit_to_mask)
 DESCRIPTION
    Masks "element" according to "bit_to_mask" following the round up algorithm.
    Operations are done in place. 
 INPUT
    Needs as inputs:
        element:     torch.tensor conteining single dimension single element 
        bit to mask: list of positions of bit that have to be masked. MSB first.
 OUTPUT
    No outputs, operation done in place in element input parameter"""

def _get_bool_tensor(quant_param, bit):
    fakeList = [bit]
    mask = ~_make_mask(fakeList)
    quasiAndTensor = quant_param & mask #quant_param.device should be equal to quasiAndTensor.device (THEY MUST BE!)
    boolTensor = quasiAndTensor.to(torch.bool) 
    return boolTensor

def _mask_bit_round_down(quant_param, bit, complete_mask):
    fakeList = [bit]
    mask = ~_make_mask(fakeList)
    quasiAndTensor = quant_param & mask #quant_param.device should be equal to quasiAndTensor.device (THEY MUST BE!)
    boolTensor = quasiAndTensor.to(torch.bool).to(torch.int) # creates a correspondent boolean mask
    andTensor = quasiAndTensor ^ torch.zeros(quant_param.size(),dtype=torch.int).fill_(~0).to(quant_param.device)
    orMask = (2**bit-1) & complete_mask #orMask already take care of future masking for less significant bit
    quasiOrTensor = torch.ones(quant_param.size(),dtype=torch.int).mul_(orMask).to(torch.int).to(quant_param.device)
    orTensor = quasiOrTensor * boolTensor
    quant_param = (quant_param & andTensor) | orTensor
    return quant_param

def _mask_bit_round_up(quant_param, bit, priority=True):
    fakeList = [bit]
    mask = ~_make_mask(fakeList)
    sumTensor = quant_param & mask #quant_param.device should be equal to quasiAndTensor.device (THEY MUST BE!)
    boolTensor = sumTensor.to(torch.bool).to(torch.int)
    if (not priority) and  not (bit==0):
        fakeList = [bit - 1] #previous one
        mask = ~_make_mask(fakeList)
        boolTensor2 = (quant_param & mask).to(torch.bool).to(torch.int)
        boolTensor = boolTensor * boolTensor2 
    notBoolTensor = boolTensor ^ 1 #elementwise invert operation
    andMask = ~(2**bit - 1)
    partialAndTensor1 = andMask * boolTensor
    partialAndTensor2 = -1 * notBoolTensor
    andTensor = partialAndTensor1 + partialAndTensor2
    quant_param = quant_param & andTensor 
    quant_param = quant_param + sumTensor
    return quant_param

def _sat_to_max(quant_param, max_int):
    boolTensor = torch.gt(quant_param,max_int).to(torch.int) 
    notBoolTensor = boolTensor ^ 1
    satTensor = max_int * boolTensor
    quant_param = (quant_param * notBoolTensor) + satTensor
    return quant_param

def mask_param(quant_param, bit_to_mask, mask_type=MaskType.SIMPLE_MASK, dynamic=0 , signed=None):
    if bit_to_mask==[]:
        return quant_param
    if (dynamic==0 or signed==None) and (mask_type==MaskType.ROUND_UP or mask_type==MaskType.MINIMUM_DISTANCE):
        error_string="For Minimum Distance masking policy 'dynamic' and 'signed' parameters must be specified. Got: DYNAMIC={}\tSIGNED{}\n".format(dynamic,signed)
        raise ValueError(error_string)
    ty=quant_param.dtype
    quant_param = quant_param.to(torch.int)
    if mask_type==MaskType.SIMPLE_MASK:
        mask=_make_mask(bit_to_mask)
        quant_param = quant_param & mask
    if mask_type==MaskType.ROUND_DOWN:
        complete_mask=_make_mask(bit_to_mask)
        for bit in bit_to_mask:
            quant_param = _mask_bit_round_down(quant_param, bit, complete_mask)
    if mask_type==MaskType.MOD_ROUND_UP:
        complete_mask=_make_mask(bit_to_mask)
        max_int = 2**(dynamic-int(signed))-1 & complete_mask
        #round up operations
        for bit in bit_to_mask:
            quant_param = _mask_bit_round_up(quant_param, bit)
        #round down correction
        for bit in bit_to_mask:
            quant_param = _mask_bit_round_down(quant_param, bit, complete_mask)
        #sat
        quant_param = _sat_to_max(quant_param,max_int)
    if mask_type==MaskType.ROUND_UP:
        complete_mask=_make_mask(bit_to_mask)
        max_int = 2**(dynamic-int(signed))-1 & complete_mask
        round_up_mask = bit_to_mask[::-1]
        #round up operations
        for bit in round_up_mask:
            quant_param = _mask_bit_round_up(quant_param, bit)
        #round down correction
        for bit in bit_to_mask:
            quant_param = _mask_bit_round_down(quant_param, bit, complete_mask)
        #sat
        quant_param = _sat_to_max(quant_param,max_int)
    if mask_type==MaskType.MINIMUM_DISTANCE:
        complete_mask=_make_mask(bit_to_mask)
        max_int = 2**(dynamic-int(signed))-1 & complete_mask
        #round up operations
        for bit in bit_to_mask:
            quant_param = _mask_bit_round_up(quant_param, bit, priority=False)
        #round down correction
        for bit in bit_to_mask:
            quant_param = _mask_bit_round_down(quant_param, bit, complete_mask)
        #sat
        quant_param = _sat_to_max(quant_param,max_int)
    quant_param = quant_param.to(ty)
    return quant_param