#!/usr/bin/env python3

import torch
import sys
sys.path.append("../common")
sys.path.append("../")
from mask_util import _make_mask
import random as rand
from copy import deepcopy
bits=8
bit_to_mask=[3] 
quant_param=torch.ones(2**bits).to(torch.int)
for i in range(-2**(bits-1),2**(bits-1)):
    quant_param[i+128].mul_(i)
#shape=quant_param.size()
#quant_param = quant_param.flatten()
for el in quant_param:
    toMask = el & ~_make_mask(bit_to_mask)
    if toMask:
        upper=False
        downer=False
        fake=deepcopy(el)
        while (upper==False):
            fake+=1
            if (fake & ~_make_mask(bit_to_mask)==0):
                upper=deepcopy(fake)
        fake=deepcopy(el)
        while (downer==False):
            fake-=1
            if (fake & ~_make_mask(bit_to_mask)==0):
                downer=deepcopy(fake)
        du=deepcopy(upper-el)
        dd=deepcopy(el-downer)
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
#quant_param = quant_param.view(shape)
print(quant_param)