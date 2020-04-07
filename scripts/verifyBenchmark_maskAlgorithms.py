#!/usr/bin/env python3

import sys
sys.path.append("../")
from common.mask_util import mask_param, MaskType, stringMask_to_list, _make_mask
import torch
from common.hw_lib import printer_2s

#########SETTINGS##########
m_type=[MaskType.ARC] #[MaskType.SIMPLE_MASK,MaskType.ROUND_DOWN,MaskType.ROUND_UP,MaskType.MOD_ROUND_UP,MaskType.MINIMUM_DISTANCE]
bits=8
signed=True

if signed:
    start_point = -2**(bits-1)
    start_string = 2**(bits-1)
    end_point = 2**(bits-1)
else:
    start_point = 0
    start_string = 1
    end_point = 2**(bits)

#############WHAT TO DO#################                       
ver=True
rep=False
conf=False

def bit_string_inverter(string):
    new=""
    for i in string:
        if i=="0":
            new+="1"
        else:
            new+="0"
    return new
"""
#############SINGLE TRY#################
#t = torch.tensor([-124],dtype=torch.int)
t = torch.tensor(list(range(start_point,end_point)), dtype=torch.int)
mask_list = [3,2]
bits = 8
signed = True
mask_t = MaskType.MINIMUM_DISTANCE
t_m = mask_param( t
                    ,mask_list
                    ,mask_type = mask_t
                    ,dynamic=bits
                    ,signed=signed)
#print(t,t_m)
exit()
#"""
if ver:
    with open("../reports/mask_algorithm_rep2.txt","w") as out_rep:
        good=True    
        for mask_t in m_type:
            error_count=0
            for i in range(start_string,2**bits):
                string=printer_2s(i,8)
                string = bit_string_inverter(string)
                ones=string.count("1")
                if(ones<=bits-3):
                    all_value = list(range(start_point,end_point))
                    tensor_all_value = torch.tensor(all_value,dtype=torch.int)
                    tensor_all_value = mask_param(tensor_all_value
                                                        ,stringMask_to_list(string)
                                                        ,mask_type = mask_t
                                                        ,dynamic=bits
                                                        ,signed=signed)
                    mask = ~_make_mask(stringMask_to_list(string))
                    checkTensor= tensor_all_value & mask
                    res = torch.all(torch.eq(checkTensor.to(torch.float),torch.zeros(checkTensor.size())))
                    res2 = torch.all(torch.eq((tensor_all_value>end_point-1).to(torch.float),torch.zeros(checkTensor.size())))
                    if (not res or not res2):
                        out_rep.write("\nDIFFERENCE FOUND:\n")
                        out_rep.write("\tMASK:\n\t\t{}\n".format(string))
                        out_rep.write("\tMASK_TYPE:\n\t\t{}\n".format(mask_t))
                        out_rep.write("\tTENSORWISE:\n\t\t{}\n".format(compare_tensor))
                        error_count += 1
                        good=False
            if error_count:
                print("\t{} errors for mask:{}".format(error_count,mask_t))
        if good:
            print("All algorithms seem to mask properly! Let's go to the party")

if rep:
    with open("../reports/mask_algorithm_eval.txt","w") as log_pointer:
        for mask_t in m_type:
            log_pointer.write("Report analysis for {} type.\n".format(mask_t))
            max_distance=0
            max_expected=0
            max_had=0
            max_string=0
            sum_dist=0
            sum_dist_abs=0
            norm_max_distance=0
            max_rel_distance=0
            sum_rel_dist=0
            mean_distance=0
            norm_mean_distance=0
            mean_rel_distance=0
            num=0
            for i in range(start_string,2**bits): #all possible masks
            #for i in range(2**(bits-1)+63,2**(bits-1)+64): #for a single case
                string=printer_2s(i,8)
                string = bit_string_inverter(string)
                ones=string.count("1")
                if(ones<=bits-3):
                    all_value = list(range(start_point,end_point))
                    normTensor = torch.tensor(all_value,dtype=torch.int)
                    maskTensor = mask_param(normTensor
                                            ,stringMask_to_list(string)
                                            ,mask_type = mask_t
                                            ,dynamic=bits
                                            ,signed=signed)
                    for i,j in zip(normTensor,maskTensor):
                        wq=int(i)
                        wm=int(j)
                        dist=j-i
                        if i!=0:
                            rel_dist=float(dist)/float(i)
                        else:
                            rel_dist=0
                        if abs(dist)>abs(max_distance):
                            max_distance=dist
                            max_expected=i
                            max_had=j
                            max_string=string
                        if abs(rel_dist)>abs(max_rel_distance):
                            max_rel_distance=rel_dist
                        num+=1
                        sum_dist+=dist
                        sum_dist_abs+=abs(dist)
                        sum_rel_dist+=rel_dist
            log_pointer.write("\n")            
            log_pointer.write("\tMax error distance=\t\t\t {}.\n".format(max_distance))
            log_pointer.write("\tNorm max error distance=\t {}.\n".format(float(max_distance)/(end_point-1)))
            log_pointer.write("\tExpected= {}\t Had= {}\t Mask= {}.\n".format(max_expected,max_had,max_string))
            log_pointer.write("\n")
            log_pointer.write("\tMax relative error distance= {}.\n".format(max_rel_distance))
            log_pointer.write("\n")
            log_pointer.write("\tMean error distance=\t\t {}.\n".format(float(sum_dist)/num))
            log_pointer.write("\tNorm mean error distance=\t {}.\n".format(float(sum_dist)/num/(end_point-1)))
            log_pointer.write("\n")
            log_pointer.write("\tSum of error distance=\t\t {}.\n".format(sum_dist))
            log_pointer.write("\tSum of abs error distance=\t {}.\n".format(sum_dist_abs))
            log_pointer.write("\n")
            log_pointer.write("\tMean relative error distance={}.\n\n".format(sum_rel_dist/num))