#!/usr/bin/env python3

import torch
import sys
sys.path.append("../common")
sys.path.append("../")
from mask_util import _make_mask
import random as rand
from copy import deepcopy
bits=8
signed=True
bit_to_mask=[3]
#create param
quant_param=torch.ones(2**bits).to(torch.int)
for i in range(-2**(bits-1),2**(bits-1)):
    quant_param[i+128].mul_(i)
#print(quant_param)
#shape=quant_param.size()
#quant_param = quant_param.flatten()
mask=~_make_mask(bit_to_mask)
quant_param2=deepcopy(quant_param)
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
max_int = 2**(bits-int(signed))-1
overflow = (up_tensor>max_int).to(torch.int)

#retriving differences
diff_up = up_tensor - quant_param
diff_down = quant_param - down_tensor

#boolean tensors for substitution
up = (diff_up < diff_down).to(torch.int)*(overflow ^ 1) #here we force to zero those that overflows
down = (diff_down < diff_up).to(torch.int) | overflow

quant_param = up*up_tensor + quant_param*(up^1)
quant_param = down*down_tensor + quant_param*(down^1) 
print(quant_param)
for el in quant_param2:
    toMask = el & ~_make_mask(bit_to_mask)
    if toMask:
        upper=False
        downer=False
        fake=int(el)
        while (upper==False):
            fake+=1
            if (fake & ~_make_mask(bit_to_mask)==0):
                upper=fake
        fake=int(el)
        while (downer==False):
            fake-=1
            if (fake & ~_make_mask(bit_to_mask)==0):
                downer=fake
        du=upper-el
        dd=el-downer
        if (du > dd):
            el+=downer-el
        elif (dd > du):
            el+=upper-el
        else:
            if(rand.randint(0,99)%2):
                el+=downer-el
            else:
                el+=upper-el
        if (upper > (2**(bits-1)-1 & _make_mask(bit_to_mask))):
            el+=downer-el
print(quant_param2)
print(quant_param==quant_param2)