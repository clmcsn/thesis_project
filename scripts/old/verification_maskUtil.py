#!/usr/bin/env python3

#########SETTINGS#########
checkpointPath = "../models/checkpoints/QuantLeNet_CIFAR10_epoch100.tar"

import sys
sys.path.append("../")
sys.path.append("../../distiller")
import os

import models.cifar10.LeNet as LeNet
import torch
import distiller
from common.mask_util import mask_param, get_masked_param, MaskType
from copy import deepcopy

#recover the floating point weights
network = LeNet.LeNet()
optimizer = torch.optim.Adam(network.parameters(), lr=0.0005)
quant_net=distiller.quantization.QuantAwareTrainRangeLinearQuantizer(network
                                                                        ,optimizer=optimizer
                                                                        ,bits_activations=8
                                                                        ,bits_weights=8
                                                                        ,bits_bias=8
                                                                        ,overrides=None
                                                                        ,mode=distiller.quantization.LinearQuantMode.SYMMETRIC
                                                                        ,ema_decay=0.999
                                                                        ,per_channel_wts=False
                                                                        ,quantize_inputs=True
                                                                        ,num_bits_inputs=None
)
#setting up the distiller 
dummy_input = (torch.zeros([1,3,32,32]))
quant_net.prepare_model(dummy_input)
#quant_net.quantize_params()
checkpoint = torch.load(checkpointPath,map_location='cpu')
quant_net.model.load_state_dict(checkpoint['model_state_dict'])
with open("../reports/weights_quant.txt","w") as out_pointer, open("../reports/weights_masked.txt","w") as out2_pointer:
    for name, param in network.named_parameters():
        fp_min=param.min()
        fp_max=param.max()
        fp_min_det = fp_min.clone().detach()
        fp_max_det = fp_max.clone().detach()
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
        quant_parameter = torch.round(scale* param - zero_point)
        for element in quant_parameter.flatten():
            out_pointer.write(str(float(element.data))+"\n")
        quant_parameter = quant_parameter.to(torch.int)
        mask_param(quant_parameter, [3], mask_type=MaskType.MASK)
        for element in quant_parameter.flatten():
            out2_pointer.write(str(float(element.data))+"\n")
        quant_parameter = quant_parameter.to(torch.float)