#!/usr/bin/env python3

#########SETTINGS#########
checkpointPath = "../models/checkpoints/LeNet_CIFAR10_epoch41.tar"

import sys
sys.path.append("../")
import os

import models.cifar10.LeNet as LeNet
import torch

#recover the floating point weights
network = LeNet.LeNet()
checkpoint = torch.load(checkpointPath,map_location='cpu')
checkpoint['map_location'] = 'cpu'
network.load_state_dict(checkpoint['model_state_dict'])

#tutte le operazioni fatte su distiller vengono fatte su Parameters!
#ciò che mi serve sta in network.conv1.weight
fp_parameter=network.conv1.weight
#choosing asymetric quantization
#per-channel option = false

#no clipping is required (clipping=None even if it's possible to clip)

#saturation function will become just get min and max:
fp_min=fp_parameter.min()
fp_max=fp_parameter.max()
#for other type of clipping mode, still don't know if reachable with quant aware
#there are other sat_fn that requires many more parameters

#signed mode == True
is_scalar=False
fp_min_det=fp_min.clone().detach()
fp_max_det=fp_max.clone().detach()

fp_min_det = fp_min_det.to(torch.float32)
fp_max_det = fp_max_det.to(torch.float32)

#where 8 is the numeber of bits
n = 2 ** 8 - 1

# Make sure 0 is in the range
fp_min_det = torch.min(fp_min_det, torch.zeros_like(fp_min_det))
fp_max_det = torch.max(fp_max_det, torch.zeros_like(fp_max_det))

diff = fp_max_det - fp_min_det
    # If float values are all 0, we just want the quantized values to be 0 as well. So overriding the saturation
    # value to 'n', so the scale becomes 1
diff[diff == 0] = n

#finally zero_point + scale factore
scale = n / diff
zero_point = scale * fp_min_det

#because integral zero point is true, what does it mean?
zero_point = zero_point.round()

#signed numbers so we scale the zero point to right!
zero_point += 2 ** (8 - 1)

#scale * input - zero_point
#quantize
quant_parameter = torch.round(scale* fp_parameter - zero_point)
shape=quant_parameter.size()
t = quant_parameter.dtype
masked_quant_parameter1 = quant_parameter.clone().flatten().to(torch.int)
for element in masked_quant_parameter1:
    toMask = element & (1<<3)
    if toMask:
        element.sub_(2**3) #in place operation
        #element = element - 2**3
masked_quant_parameter1 = masked_quant_parameter1.view(shape).to(t)
quant_parameter[0][0][0]=torch.tensor([127])
masked_quant_parameter2 = quant_parameter.clone().flatten().to(torch.int)
print(type(masked_quant_parameter2),type(quant_parameter))
for element in masked_quant_parameter2:
    #voglio mascherare il 4o bit ---> tutti i 3 vanno parametrizzati
    toMask = element & (1<<3)
    if toMask:
        toSum = element & (1<<(3-1))
        if toSum:
            mask = 2**3 -1
            element.sub_(element & mask)
            element.add_(2**3) #TODO chech overflow for positive numbers
        else:
            mask = 2**(3+1) - 1
            element.sub_(element & mask)
            element.add_(2**3 - 1)
masked_quant_parameter2 = masked_quant_parameter2.view(shape).to(torch.float)
print(quant_parameter[0][0])
print(masked_quant_parameter1[0][0])
print(masked_quant_parameter2[0][0])
