#!/usr/bin/env python3

from enum import Enum
import torch

class MaskType(Enum):
     SIMPLE_MASK = 1
     ROUND_DOWN = 2
     ROUND_UP = 3
     MINIMUM_DISTANCE = 4

"""num_in_range(num, dynamic, signed)

 DESCRIPTION
    Tells if 'num' is in the range [-2^(d-1),2^(d-1)-1] if signed
                                   [0, 2^(d)-1] if unsigned
 INPUT
    Needs as inputs:
       num:        value to be checked.
       dynamic:    amount of lines.
       signed:     if value has to be considered signed (True) or unsigned (False).
 OUTPUT
    True for value belongs to range, False if it doesn't."""

def num_in_range(num, dynamic, signed):
    if signed:
        if (int(num)>(2**(dynamic-1)-1)) or (int(num)<(-2**(dynamic-1))): 
            return False
    else:
        if (int(num)>2**(dynamic)-1):
            return False
    return True

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
def _elm_mask_round_down(element, bit_to_mask):
    mask = 2**(bit_to_mask[0]+1) - 1
    element.sub_(element & mask)
    mask=_make_mask(bit_to_mask[1:])
    element.add_((2**bit_to_mask[0] - 1) & mask)

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
def _elm_mask_round_up(element, bit_to_mask, original_bit_mask, dynamic, signed):
    mask = 2**bit_to_mask[0] -1
    element.sub_(element & mask)
    element.add_(2**bit_to_mask[0])

    #negative numbers never overflow
    if (not num_in_range(element.data,dynamic,signed)):
        element.zero_()
        mask=_make_mask(original_bit_mask)
        element.add_((2**(dynamic-int(signed))-1) & mask) #this line assignes the maximum allowd positive value masked

def mask_param(quant_param, bit_to_mask, mask_type=MaskType.SIMPLE_MASK, dynamic=0 , signed=None):
    if bit_to_mask==[]:
        return quant_param
    shape = quant_param.size()
    ty = quant_param.dtype
    quant_param = quant_param.flatten().to(torch.int)
    if mask_type==MaskType.SIMPLE_MASK:
        mask=_make_mask(bit_to_mask)
        for element in quant_param:
            element.data&=mask
    elif mask_type==MaskType.ROUND_DOWN:
        for element in quant_param:
            done=False
            while ((bit_to_mask) and (not done)):
                toMask = element & (1<<bit_to_mask[0])
                if toMask:
                    _elm_mask_round_down(element, bit_to_mask)
                    done=True
                bit_to_mask.pop(0)
    elif mask_type==MaskType.MINIMUM_DISTANCE:
        if dynamic==0 or signed==None:
            raise ValueError("For Minimum Distance masking policy 'dynamic' and 'signed' parameters must be specified.\n Got: DYNAMIC={}\tSIGNED{}\n".format(dynamic,signed))
        for element in quant_param:
            done=False
            original_bit_mask=bit_to_mask.copy()
            recheck=False
            while ((bit_to_mask) and (not done)):
                toMask = element & (1<<bit_to_mask[0])
                if toMask:
                    done=True
                    if bit_to_mask[0]==0:
                        mask=1
                        element&=(~mask)
                    else:
                        toSum = int(bool(element & (1<<(bit_to_mask[0]-1))))
                        if toSum:
                            recheck=True
                            _elm_mask_round_up(element, bit_to_mask, original_bit_mask, dynamic, signed)
                        else:
                            _elm_mask_round_down(element, bit_to_mask)
                bit_to_mask.pop(0)
            if (recheck):
                done=False
                while ((original_bit_mask) and (not done)): #needed in case summing up we make mistakes!
                    toMask = element & (1<<original_bit_mask[0])
                    if toMask:
                        _elm_mask_round_down(element, original_bit_mask)
                        done=True
                    original_bit_mask.pop(0)
    elif mask_type==MaskType.ROUND_UP:
        if dynamic==0 or signed==None:
            raise ValueError("For Minimum Distance masking policy 'dynamic' and 'signed' parameters must be specified.\n Got: DYNAMIC={}\tSIGNED{}\n".format(dynamic,signed))
        for element in quant_param:
            done=False
            original_bit_mask=bit_to_mask.copy()
            recheck=False
            while ((bit_to_mask) and (not done)):
                toMask = element & (1<<bit_to_mask[0])
                if toMask:
                    done=True
                    recheck=True
                    _elm_mask_round_up(element, bit_to_mask, original_bit_mask, dynamic, signed)
                bit_to_mask.pop(0)
            if (recheck):
                done=False
                while ((original_bit_mask) and (not done)): #needed in case summing up we make mistakes!
                    toMask = element & (1<<original_bit_mask[0])
                    if toMask:
                        _elm_mask_round_down(element, original_bit_mask)
                        done=True
                    original_bit_mask.pop(0)
    quant_param = quant_param.view(shape).to(ty)
    return quant_param

def mask_param_adv(quant_param, bit_to_mask, mask_type=MaskType.SIMPLE_MASK, dynamic=0 , signed=None):
    if bit_to_mask==[]:
        return quant_param
    ty=quant_param.dtype
    quant_param = quant_param.to(torch.int)
    if mask_type==MaskType.SIMPLE_MASK:
        mask=_make_mask(bit_to_mask)
        quant_param = quant_param & mask
    quant_param = quant_param.to(ty)
    return quant_param