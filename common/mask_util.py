#!/usr/bin/env python3

from enum import Enum
import torch

class MaskType(Enum):
     MASK = 1
     ROUND_DOWN = 2
     MINIMUM_DISTANCE = 3

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
        if (num>(2**(dynamic-1)-1)) or (num<(-2**(dynamic-1))): 
            return False
    else:
        if (num>2**(dynamic)-1):
            return False
    return True

"""_stringMask_to_list(stringMask)

 DESCRIPTION
    Converts a string indicating which bits have to be masked to a list of same bit positions.
    e.g. "00100100" (MSB first) becomes bit_to_mask=[5,2]
 INPUT
    Needs as inputs:
       stringMask:  string of bit, MSB first, where '1' indicates which bit has to be masked
 OUTPUT
    bit to mask: list of positions of bit that have to be masked. MSB first."""
def _stringMask_to_list(stringMask):
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
def _elm_mask_round_up(element, bit_to_mask, dynamic, signed):
    mask = 2**bit_to_mask[0] -1
    element.sub_(element & mask)
    element.add_(2**bit_to_mask[0])
    #negative numbers never overflow
    if ~num_in_range(element.data,dynamic,signed):
        mask=_make_mask(bit_to_mask)
        element=((2**(dynamic-int(signed))-1) & mask) #this line assignes the maximum allowd positive value masked


def get_masked_param(quant_param, bit_to_mask, mask_type=MaskType.MASK, dynamic=0 , signed=None):
    #quant_param pre processing
    temp_param=quant_param.clone().flatten().to(torch.int)
    if mask_type==MaskType.MASK:
        mask=_make_mask(bit_to_mask)
        for element in temp_param:
            element&=mask
    elif mask_type==MaskType.ROUND_DOWN:
        for element in temp_param:
            toMask = element & (1<<bit_to_mask[0])
            if toMask:
                _elm_mask_round_down(element, bit_to_mask)
    elif mask_type==MaskType.MINIMUM_DISTANCE:
        if dynamic==0 or signed==None:
            raise ValueError("For Minimum Distance masking policy 'dynamic' and 'signed' parameters must be specified.\n Got: DYNAMIC={}\tSIGNED{}\n".format(dynamic,signed))
        for element in temp_param:
            toMask = element & (1<<bit_to_mask[0])
            if toMask:
                toSum = element & (1<<(bit_to_mask[0]-1))
                if toSum:
                    _elm_mask_round_up(element, bit_to_mask, dynamic, signed)
                else:
                    _elm_mask_round_down(element, bit_to_mask)
    return temp_param.view(quant_parameter.size()).to(quant_parameter.dtype)