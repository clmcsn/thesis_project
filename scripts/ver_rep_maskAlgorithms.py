#!/usr/bin/env python3

import sys
sys.path.append("../")
from common.mask_util import mask_param, MaskType, stringMask_to_list
import torch

#########SETTINGS##########
m_type=[MaskType.SIMPLE_MASK,MaskType.ROUND_DOWN,MaskType.ROUND_UP,MaskType.MINIMUM_DISTANCE]
bits=8
signed=True

if signed:
    start_point=-2**(bits-1)
    end_point=2**(bits-1)
else:
    start_point=0
    end_point=2**(bits) 

ver=True
rep=True
def bit_string_inverter(string):
    new=""
    for i in string:
        if i=="0":
            new+="1"
        else:
            new+="0"
    return new
##########single try##############
"""
for i in range(start_point,end_point):
    t =torch.tensor([i], dtype=torch.int)
    mask="00110111"
    mask_t=MaskType.MINIMUM_DISTANCE
    mask_param(t
                ,stringMask_to_list(mask)
                ,mask_type = mask_t
                ,dynamic=bits
                ,signed=signed)
    print(i,"{0:b}".format(int(t)))
exit()"""
##################################
if ver:
    with open("../reports/mask_examples.txt","w") as out_log:    
        for mask_t in m_type:
            out_log.write("All combination for {} type.\n".format(mask_t))
            for i in range(2**(bits-1),2**bits):
                string="{0:b}".format(i)
                string = bit_string_inverter(string)
                ones=string.count("1")
                if(ones<=bits-3):
                    out_log.write("\tAll combination for {} mask.\n".format(string))
                    for i in range(start_point,end_point):
                        t = torch.tensor([i], dtype=torch.int)
                        mask_param(t
                                    ,stringMask_to_list(string)
                                    ,mask_type = mask_t
                                    ,dynamic=bits
                                    ,signed=signed)
                        out_log.write("\t\t{0} ---> {1}.\n".format(i,int(t)))

if rep:
    with open("../reports/mask_algorithm_eval.txt","w") as log_pointer:
        for mask_t in m_type:
            log_pointer.write("Report analysis for {} type.\n".format(mask_t))
            max_distance=0
            sum_dist=0
            sum_dist_abs=0
            norm_max_distance=0
            max_rel_distance=0
            sum_rel_dist=0
            mean_distance=0
            norm_mean_distance=0
            mean_rel_distance=0
            num=0
            for i in range(2**(bits-1),2**bits): #all possible masks
            #for i in range(2**(bits-1)+63,2**(bits-1)+64): #for a single case
                string="{0:b}".format(i)
                string = bit_string_inverter(string)
                ones=string.count("1")
                if(ones<=bits-3):
                    for i in range(start_point,end_point):
                        t = torch.tensor([i], dtype=torch.int)
                        mask_param(t
                                    ,stringMask_to_list(string)
                                    ,mask_type = mask_t
                                    ,dynamic=bits
                                    ,signed=signed)
                        el=int(t)
                        dist=el-i
                        if i!=0:
                            rel_dist=float(dist)/float(i)
                        else:
                            rel_dist=0
                        
                        if abs(dist)>abs(max_distance):
                            max_distance=dist
                        if abs(rel_dist)>abs(max_rel_distance):
                            max_rel_distance=rel_dist
                        num+=1
                        sum_dist+=dist
                        sum_dist_abs+=abs(dist)
                        sum_rel_dist+=rel_dist
            log_pointer.write("\tMax error distance=\t\t\t {}.\n".format(max_distance))
            log_pointer.write("\tNorm max error distance=\t {}.\n".format(max_distance/(end_point-1)))
            log_pointer.write("\tMax relative error distance= {}.\n".format(max_rel_distance))
            log_pointer.write("\tMean error distance=\t\t {}.\n".format(sum_dist/num))
            log_pointer.write("\tSum of error distance=\t\t {}.\n".format(sum_dist))
            log_pointer.write("\tSum of abs error distance=\t {}.\n".format(sum_dist_abs))
            log_pointer.write("\tNorm mean error distance=\t {}.\n".format(sum_dist/num/(end_point-1)))
            log_pointer.write("\tMean relative error distance={}.\n\n".format(sum_rel_dist/num))