#!/usr/bin/env python3

from enum import Enum
import torch

from common.nnTools import get_layersName_list

import os
import shutil

class MaskType(Enum):
     SIMPLE_MASK = 1
     ROUND_DOWN = 2
     ROUND_UP = 3
     MOD_ROUND_UP = 4
     MINIMUM_DISTANCE = 5
     MINIMUM_DISTANCE_2 = 6

class MaskInfo():
    def __init__(   self, quant_mode, mask_type,
                            mask, correctRange):
    
        self.quant_mode = quant_mode
        self.mask_type = mask_type
        #for analysis purposis mask can be a string, for simulation it MUST be the list of masked bit!
        self.mask = mask 
        self.correctRange = correctRange

class MaskStat(MaskInfo):
    def __init__(self, quant_mode, mask_type,
                        mask, correctRange,
                        correct_preds,  accuracy,
                        model_name):
        super(MaskStat, self).__init__( quant_mode,
                                        mask_type,
                                        mask,
                                        correctRange)
        self.correct_preds = correct_preds
        self.accuracy = accuracy
        self.model_name = model_name

class MaskTable(MaskInfo):
    def __init__(self, quant_mode, mask_type, 
                        mask, correctRange, 
                        model, mask_file=None):
        super(MaskTable, self).__init__( quant_mode,
                                        mask_type,
                                        mask,
                                        correctRange)
        self.model_class = model.__class__.__name__
        self.Table = {}
        self.create_table(model)
        if mask:
            self.set_default_mask(mask)
        if mask_file:
            self.fill_table(mask_file)

    def create_table(self,model):
        layers_name_list = get_layersName_list(model)
        for layer_name in layers_name_list:
            self.Table[layer_name] = []

    def fill_table(self,file_path):
        #temp_dic is just a way to control that all the keys are congruent
        temp_dic = maskFile_to_dict(file_path)
        for key in self.Table.keys():
            self.Table[key]=temp_dic[key]

    def set_default_mask(self,mask):
        for layer_name in self.Table.keys():
            self.Table[layer_name] = mask

    #mask must be the list
    def set_mask(self,layer_name,mask):
        if not layer_name in Table:
            raise ValueError(layer_name+'not found in'+self.model_class)
        self.Table[layer_name] = mask

    def set_mask_type(self,mask_type):
        if not isinstance(mask_type, MaskType):
            raise ValueError('Specify a correct mask type')
        self.mask_type = mask_type

    def get_layersName():
        return list(Table.keys())

    def clean_table(self):
        for layer in self.Table:
            self.Table[layer]=[]

"""guided_MaskTable_creator(network,std_mask,file_path,gui=True)

DESCRIPTION
    Provides a guided terminal per-layer masking file creation of the network given as input
INPUT
    Needs as inputs:
    network:    network which we would like to create the mask
    std_mask:   if we would like to give a std_mask pressing just 's' in the procedure. Giving a default even all zeros is strongly recommended
    file_path:  indicates where output file must be saved
    gui=True:   indicates if entry of table will be provided by hand or all will be assigned the default"""

def guided_MaskTable_creator(network,file_path,std_mask="00000000",gui=True):
    file_string="{}: {}\n"
    layers = get_layersName_list(network)
    print("Available layers:")
    for l in layers:
        print(l)
    with open(file_path,"w") as out_pointer:
        if gui==False:
            for lay in layers:
                out_pointer.write(file_string.format(lay,std_mask))
        else:
            for lay in layers:
                mask = input("Please insert a mask for layer {}: (s for standard)\n".format(lay))
                if mask=="s" or mask=="S":
                    out_pointer.write(file_string.format(lay,std_mask))
                else:
                    if len(mask)!=len(std_mask):
                        print("Mask must be of {} bits. If not what expected provide a different standard mask".format(len(std_mask)))
                        exit()
                    else:
                        out_pointer.write(file_string.format(lay,mask))


def set_specific_layers(layers,file_path,new_mask="00000000"):
    file_string="{}: {}\n"
    with open(file_path,"r") as in_pointer, open("temp","w") as out_pointer:
        for line in in_pointer:
            words = line.split()
            layer_name = words[0][0:len(words[0])-1]
            mask = words[1]
            if layer_name in layers:
                mask = new_mask
            out_pointer.write(file_string.format(layer_name,mask))
    os.remove(file_path)
    shutil.move("temp",file_path)

"""maskFile_to_dict(file_path

DESCRIPTION
    From file with the list of mask for each layer, this function provides a dictionary extracted from it
INPUT
    Needs as inputs:
    file_path:  file where to extract network description
OUTPUT
    dic:        dictionary with informations"""

def maskFile_to_dict(file_path):
    dic={}
    with open(file_path,"r") as in_pointer:
        for line in in_pointer:
            words=line.split()
            dic[words[0][0:len(words[0])-1]]=stringMask_to_list(words[1])
    return dic


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

def _mask_bit_round_down(quant_param, bit, complete_mask, priority=True):
    fakeList = [bit]
    mask = ~_make_mask(fakeList)
    quasiAndTensor = quant_param & mask #quant_param.device should be equal to quasiAndTensor.device (THEY MUST BE!)
    boolTensor = quasiAndTensor.to(torch.bool).to(torch.int) # creates a correspondent boolean mask
    andTensor = quasiAndTensor ^ torch.zeros(quant_param.size(),dtype=torch.int).fill_(~0).to(quant_param.device)
    if priority:
        orMask = (2**bit-1) & complete_mask #orMask already take care of future masking for less significant bit
    else:
        orMask = (2**bit-1)
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

def get_max_masked_val(num_bit, signed, bit_to_mask):
    mask = _make_mask(bit_to_mask)
    if signed:
        return ((2 ** (num_bit - 1)) - 1) & mask
    else:
        return ((2 ** num_bit) - 1) & mask

def mask_param(quant_param, bit_to_mask, mask_type=MaskType.SIMPLE_MASK, dynamic=0 , signed=None):
    if bit_to_mask==[]:
        return quant_param
    if (dynamic==0 or signed==None) and (mask_type==MaskType.ROUND_UP or mask_type==MaskType.MINIMUM_DISTANCE):
        error_string="For Minimum Distance masking policy 'dynamic' and 'signed' parameters must be specified. Got: DYNAMIC= {}  SIGNED= {}".format(dynamic,signed)
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
    if mask_type==MaskType.MINIMUM_DISTANCE_2: #with true round up algorithm
        complete_mask=_make_mask(bit_to_mask)
        max_int = 2**(dynamic-int(signed))-1 & complete_mask
        round_up_mask = bit_to_mask[::-1]
        #round up operations
        for bit in round_up_mask:
            quant_param = _mask_bit_round_up(quant_param, bit, priority=False)
            quant_param = _mask_bit_round_down(quant_param, bit, complete_mask, priority=True)
        #sat
        quant_param = _sat_to_max(quant_param,max_int)
    quant_param = quant_param.to(ty)
    return quant_param
