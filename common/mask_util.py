#!/usr/bin/env python3

from enum import Enum
import torch
import torch.nn as nn
from common.nnTools import get_layersName_list

import os
import shutil
import random as rand
from collections import namedtuple, OrderedDict
import json


mc_file_string="{}: {}\t{}\n" #for .mc files

#list of all masking algorithms aveilable
class MaskType(Enum):
    SIMPLE_MASK = 1
    ARC = 2

"""basic class for containing informations"""
#TODO far diventare MaskInfo la classe che esprime le informazioni di una singola maschera applicata a una 
#       determintata rete o LAYER

class MaskInfo():
    def __init__(   self, w_bits, quant_mode, mask_type,
                            mask, correctRange):
    
        self.w_bits = w_bits
        self.quant_mode = quant_mode
        self.mask_type = mask_type
        #for analysis purposis mask can be a string, for simulation it MUST be the list of masked bit!
        self.mask = mask 
        self.correctRange = correctRange


"""namedtuple for describing the exact operation that must be performed layer-wise"""
LayerAttributes = namedtuple("LayerAttributes",['mask','correctRange'])

"""namedtuple for describing how a mask behaves in a layer"""
MaskLayerProperty = namedtuple("MaskLayerProperty",['correctRange','accuracy'])

"""support class for collecting statistics belonging to masks"""
class MaskStat(MaskInfo):
    def __init__(self, w_bits, quant_mode, mask_type,
                        mask, correctRange,
                        correct_preds,
                        layer,
                        performance_class=None):
        super(MaskStat, self).__init__( w_bits,
                                        quant_mode,
                                        mask_type,
                                        mask,
                                        correctRange)
        self.correct_preds = correct_preds
        self.performance_class = performance_class
        self.layer = layer
    
    def set_performance_class(self, pc):
        self.performance_class=pc 

"""Class used for correct handling network and masking"""
class MaskTable(MaskInfo):
    def __init__(self, w_bits, quant_mode, mask_type, model, 
                        mask=None, correctRange=None, 
                        mask_dict=None,mask_file=None):
        super(MaskTable, self).__init__(w_bits, 
                                        quant_mode,
                                        mask_type,
                                        mask,
                                        correctRange)
        self.model_class = model.__class__.__name__
        self.Table = {}
        self.create_table(model)
        if mask_dict:
            self.fill_table(mask_dict)
        elif isinstance(mask, list):                                                                                      
            self.set_default_mask(mask,correctRange)
        elif mask_file:                                                                                   
            self.fill_table_from_file(mask_file) 

    """create_table(self,model)
    DESCRIPTION
        Builts the structure of the table with the information for masking the network passed as model
    INPUT
        Needs as inputs:
        model: instance of the network that wants to be handled"""
    def create_table(self,model):
        layers_name_list = get_layersName_list(model)
        for layer_name in layers_name_list:
            self.Table[layer_name] = LayerAttributes(mask=[] , correctRange=False)

    def fill_table_from_file(self,file_path):
        #temp_dic is just a way to control that all the keys are congruent
        temp_dic = maskFile_to_dict(file_path)
        for key in self.Table.keys():
            self.Table[key]=temp_dic[key]

    def fill_table(self,mask_dict):
        for key in self.Table.keys():
            self.Table[key]=mask_dict[key]

    def set_default_mask(self,mask,correctRange):
        for layer_name in self.Table.keys():
            self.Table[layer_name] = LayerAttributes(mask=mask , correctRange=correctRange)

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

"""saveLayerAccuracyTable_toFile(layer_table,fname)
    DESCRIPTION
        Saves 'layer_table' in 'fname'.
        layer table must be of type: 
        DICTIONARY, where 
            keys are string name of layer
            values are DICTIONARIES, where:
                keys are string name of mask (00001000) where 1s are bit to be masked
                values are object of type MaskLayerProperty 
    INPUT
        Needs as inputs:
        layer_table: filled layer table
        fname: file name with all characterization
    OUTPUT
        no return"""
def saveLayerAccuracyTable_toFile(layer_table,fname):
    with open(fname,"w") as out_pointer:
        for layer in layer_table.keys():
            out_pointer.write("{}\n".format(layer))
            for mask in layer_table[layer].keys():
                out_pointer.write("Mask:{}\tRangeCorrect:{}\tAccuracy:{}\n".format(mask,layer_table[layer][mask].rangeCorrect,layer_table[layer][mask].accuracy))

"""loadLayerAccuracyTable_fromFile(fname)
    DESCRIPTION
        returns a layer table stored in 'fname'
    INPUT
        Needs as inputs:
        fname: file name with a valid layer table saved in it. Please check saveLoadTable for format
    OUTPUT
        returns the layer table loaded from file"""
def loadLayerAccuracyTable_fromFile(fname):
    table={}
    with open(fname,"r") as in_pointer:
        for line in in_pointer:
            data = line.split()
            if len(data)==1:
                l=data[0]
                table[l]=OrderedDict()
            else:
                m=data[0].split(":")[1]
                c=data[1].split(":")[1]
                a=data[2].split(":")[1]
                table[l][m]=MaskLayerProperty(c,a)
    return table

"""get_mask_hwCharact(fname)
    DESCRIPTION
        Out of a mask characterization file provides a dictionary with mask as key and performance as entry
        File must be of the following type:
            "mask   performance"
        masked bit may be indicated both with '0' or '1' but for correctly handling both these possibility
        first line must contain reference performance!
    INPUT
        Needs as inputs:
        fname: file name with all characterization
    OUTPUT
        dic: dictionary with all the entry
            MASKED BIT WILL BE INDICATED WITH '1'"""

def get_mask_hwCharact(fname):
    
    def invertString(string,toInvert):
        newString=""
        if toInvert:
            for c in string:
                if c=="1":
                    newString+="0"
                else:
                    newString+="1"
            return newString
        else:
            return string
    
    dic={}
    with open(fname,"r") as in_pointer:
        fst_line = in_pointer.readline()
        info = fst_line.split()
        if not(info[0] == len(info[0]) * info[0][0]):
            print("First string is not reference MAC characterization!")
            raise 
        if info[0][0]=="1":
            toInvert=True
        dic[invertString(info[0],toInvert)] = float(info[1])
        for line in in_pointer:
            info = line.split()
            dic[invertString(info[0],toInvert)] = float(info[1])
    return dic

"""compensateNetwork(ref_model,child_model,test_set,path_conf_file,batch_size=50,device='cpu')
    DESCRIPTION
        Given a reference quantized model this function compensates the neuron biases of a masked
        model. Activations differences are averaged for all output fmap + the batch size
    INPUT
        Needs as inputs:
        ref_model:      reference quantized model as example for output feature maps
        child_model:    the masked model that has to be compensated
        test_set:       test set where to extract the first batch of data
        path_conf_file: JSON file with all the configuration of relative paths
        batch_size:     size of the single batch for performing the compensation
        device:         device where to run the function
    OUTPUT
        Does not return any object. Compensation is performed in place"""

def compensateNetwork(ref_model,child_model,test_set,path_conf_file,batch_size=50,device='cpu'):

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
                    os.rename(out_path+el,out_path+new_name+"_{}".format(l)+".dump")
    
    with open(path_conf_file,"r") as j_conf:
        path_conf = json.load(j_conf)
    
    try:
        os.mkdir(path_conf["dumps"])
    except FileExistsError:
        shutil.rmtree(path_conf["dumps"])
        os.mkdir(path_conf["dumps"]) 
    
    #tell libraries to save activations 
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
    save_dump(path_conf["dumps"],path_conf["ref_dumps_file"].split("_")[0],path_conf["ref_dumps"])
    pred_child = child_model(image)
    save_dump(path_conf["dumps"],path_conf["ref_dumps_file"].split("_")[0],path_conf["mask_dumps"],new_name="child")
    i=0 #needed for the scaling factor
    for layer_name, layer in child_model.named_modules(): #for every module
        if isinstance(layer, (nn.Conv2d, nn.Conv3d, nn.Linear)): # if it is an instance
            #retriving scale factor
            with open(path_conf["dumps"]+path_conf["sf_dump_file"],"r") as in_pointer:
                for k in range(i+1): #need to fetch how many scale factors as layer we are in
                    sf = float(in_pointer.readline())
            lc = layer_name.split(".")
            o_layer_name=".".join(lc[:-1])
            ref     = torch.load(path_conf["ref_dumps"]+path_conf["ref_dumps_file"].format(o_layer_name), map_location=device) 
            child   = torch.load(path_conf["mask_dumps"]+path_conf["mask_dumps_file"].format(o_layer_name), map_location=device)
            if isinstance(layer,nn.Conv2d):  #case of convolutional layers 
                for j in range(ref.size(1)): #for every element of the bias=num_output_channels
                    r = ref[:,j,:,:] #for every image of the batch, select j output fmap 
                    c = child[:,j,:,:]
                    #average but without square ---> to try that distance
                    d = torch.sum(r-c)/ref.size(0)/ref.size(2)/ref.size(3)#*((r==0).sum()) #perform the distance
                    layer.bias[j] = layer.bias[j] + d
            if isinstance(layer,nn.Linear): #case of fully connected layers
                for j in range(ref.size(1)): #numbers_of_class=10
                    r = ref[:,j]
                    c = child[:,j]
                    d = torch.sum(r-c)/ref.size(0)
                    layer.bias[j] = layer.bias[j] + d
            #upload distiller backup
            if len(lc)-1==1:              #case of layer name composed by one word
                getattr(child_model,lc[0]).base_b_q = (layer.bias/sf)-getattr(child_model,lc[0]).b_zero_point
            if len(lc)-1==2:               #case of layer name composed by two words
                getattr(getattr(child_model,lc[0]),lc[1]).base_b_q = (layer.bias/sf)-getattr(getattr(child_model,lc[0]),lc[1]).b_zero_point #this works only for vgg
            if len(lc)-1==3:               #case of layer name composed by three words
                getattr(getattr(getattr(child_model,lc[0]),lc[1]),lc[2]).base_b_q = (layer.bias/sf)-getattr(getattr(getattr(child_model,lc[0]),lc[1]),lc[2]).b_zero_point #this works only for vgg
            #getting again activation from layer
            os.remove(path_conf["dumps"]+path_conf["sf_dump_file"]) #removing the scaling factor that will be produced
            pred_child = child_model(image) #getting new activation values
            save_dump(path_conf["dumps"],path_conf["ref_dumps_file"].split("_")[0],path_conf["mask_dumps"],new_name="child")
            i+=1
    #cleaning activation
    os.remove("./save_act")
    shutil.rmtree(path_conf["dumps"])

"""guided_MaskTable_creator(network,std_mask,file_path,gui=True)

DESCRIPTION
    Provides a guided terminal per-layer masking file creation of the network given as input
INPUT
    Needs as inputs:
    network:    network which we would like to create the mask
    std_mask:   if we would like to give a std_mask pressing just 's' in the procedure. Giving a default even all zeros is strongly recommended
    file_path:  indicates where output file must be saved
    gui=True:   indicates if entry of table will be provided by hand or all will be assigned the default"""

def guided_MaskTable_creator(network,file_path,std_mask="00000000",correctRange=False,gui=True):
    layers = get_layersName_list(network)
    with open(file_path,"w") as out_pointer:
        if gui==False:
            for lay in layers:
                out_pointer.write(mc_file_string.format(lay,std_mask,int(correctRange)))
        else:
            print("Available layers:")
            for l in layers:
                print(l)
            for lay in layers:
                mask = input("Please insert a mask for layer {}: (s for standard)\n".format(lay))
                if mask=="s" or mask=="S":
                    out_pointer.write(mc_file_string.format(lay,std_mask,int(correctRange)))
                else:
                    if len(mask)!=len(std_mask):
                        print("Mask must be of {} bits. If not what expected provide a different standard mask".format(len(std_mask)))
                        exit()
                    else:
                        out_pointer.write(mc_file_string.format(lay,mask,int(correctRange)))


def set_specific_layers(layers,file_path,new_mask="00000000"):
    with open(file_path,"r") as in_pointer, open("temp","w") as out_pointer:
        for line in in_pointer:
            words = line.split()
            layer_name = words[0][0:len(words[0])-1] #needed for deleating "at the end"
            mask = words[1]
            rangeCorrect=words[2]
            if layer_name in layers:
                mask = new_mask
            out_pointer.write(mc_file_string.format(layer_name,mask,rangeCorrect))
    os.remove(file_path)
    shutil.move("temp",file_path)

"""maskFile_to_dict(file_path)

DESCRIPTION
    From file with the list of mask for each layer, this function provides a dictionary extracted from it
INPUT
    Needs as inputs:
    file_path:  file where to extract network description
OUTPUT
    dic:        dictionary with informations. (mask as a list)"""

def maskFile_to_dict(file_path):
    dic={}
    with open(file_path,"r") as in_pointer:
        for line in in_pointer:
            words=line.split()
            dic[words[0][0:len(words[0])-1]]=LayerAttributes(mask=stringMask_to_list(words[1]) , correctRange=bool(int(words[2])))
    return dic

"""saveLayerAttributesDictionary_toFile(file_path)

DESCRIPTION
    File name where we want to save the LayerAtributes dictionary. 
    It's the inverse operation of 'maskFile_to_dict'
INPUT
    Needs as inputs:
    file_path:  file where to save network description
OUTPUT
    no output"""
def saveLayerAttributesDictionary_toFile(dic,file_path):
    with open(file_path,"w") as out_pointer:
        for l in dic.keys():
            out_pointer.write(mc_file_string.format(l,dic[l].mask,int(dic[l].correctRange)))


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

def evaluate_mask(n_bit,signed=True,mask_type=MaskType.SIMPLE_MASK,mask=[]):
    #generate limits
    if signed:
        start_point = -2**(n_bit-1)
        end_point = 2**(n_bit-1)
    else:
        start_point = 0
        end_point = 2**(n_bit)    
    #generate tensor
    t = torch.ones(2**n_bit)
    for i in range(start_point,end_point):
        t[i].mul_(i)
    
    tm = mask_param(t,mask,mask_type,n_bit,signed)
    d= torch.dist(t,tm,2)
    return d

def get_max_masked_val(num_bit, signed, bit_to_mask):
    mask = _make_mask(bit_to_mask)
    if signed:
        return ((2 ** (num_bit - 1)) - 1) & mask
    else:
        return ((2 ** num_bit) - 1) & mask

def mask_param(quant_param, bit_to_mask, mask_type=MaskType.SIMPLE_MASK, dynamic=0 , signed=None):
    if bit_to_mask==[]:
        return quant_param
    if (dynamic==0 or signed==None) and (mask_type==ARC):
        error_string="For Minimum Distance masking policy 'dynamic' and 'signed' parameters must be specified. Got: DYNAMIC= {}  SIGNED= {}".format(dynamic,signed)
        raise ValueError(error_string)
    ty=quant_param.dtype
    quant_param = quant_param.to(torch.int)
    if mask_type==MaskType.SIMPLE_MASK:
        mask=_make_mask(bit_to_mask)
        quant_param = quant_param & mask
    elif mask_type==MaskType.ARC:
        mask=~_make_mask(bit_to_mask)
        #generate up_tensor
        boolTensor=(quant_param & mask).to(torch.bool).to(torch.int)
        up_tensor=quant_param + boolTensor
        while (boolTensor.sum()):
            boolTensor=(up_tensor & mask).to(torch.bool).to(torch.int)
            up_tensor += boolTensor

        #generate down_tensor
        boolTensor=(quant_param & mask).to(torch.bool).to(torch.int)
        down_tensor=quant_param - boolTensor
        while (boolTensor.sum()):
            boolTensor=(down_tensor & mask).to(torch.bool).to(torch.int)
            down_tensor -= boolTensor

        #exclude overflow numbers
        max_int = 2**(dynamic-int(signed))-1
        overflow = (up_tensor>max_int).to(torch.int)

        #retriving differences
        diff_up = up_tensor - quant_param
        diff_down = quant_param - down_tensor

        #boolean tensors for substitution
        up = (diff_up < diff_down).to(torch.int)*(overflow ^ 1) #here we force to zero those that overflows
        down = (diff_down < diff_up).to(torch.int) | overflow

        #we need to detect those parameters that are equal and randomly assign to one or the other tensor
        random = torch.ones(quant_param.size()).random_(-100,100).to(torch.int) #-100 compreso, 100 non compreso -> in such a way is balanced!
        random = random + (random == 0).to(torch.int) #converts 0s in 1s
        equal = (diff_up == diff_down).to(torch.int) * random
        up_e = (equal > 0).to(torch.int)*(overflow ^ 1)
        down_e = (equal < 0).to(torch.int)

        quant_param = up_e*up_tensor + quant_param*(up_e^1)
        quant_param = down_e*down_tensor + quant_param*(down_e^1)
        quant_param = up*up_tensor + quant_param*(up^1)
        quant_param = down*down_tensor + quant_param*(down^1)
    quant_param = quant_param.to(ty)
    return quant_param
