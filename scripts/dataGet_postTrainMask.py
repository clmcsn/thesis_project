#!/usr/bin/env python3

import os
import pathlib
import sys
sys.path.append("../")
import settings.dataGet_postTrainMask_setting as s
#from s import *
sys.path.append(s.distiller_version)

from copy import deepcopy

import torch

import distiller
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode
import distiller.utils
import distiller.models.cifar10 as models

from common.nnTools import get_all_preds, get_layersName_list, make_weightDistr_comparHistgram
from common.mask_util import MaskType, stringMask_to_list, _make_mask, MaskTable, guided_MaskTable_creator , set_specific_layers, balanceNetwork_v2
from common.hw_lib import printer_2s

#load network
network = s.network.to("cpu") #s.network id is assigned to network here. loaded to cpu fo getting baseline accuracy 
network = network.eval() 
checkpoint = torch.load(s.checkpoint_path+s.checkpoint_name, map_location="cpu") #map location for avoiding conflicts
network.load_state_dict(checkpoint['model_state_dict'])

data_loader= torch.utils.data.DataLoader(
    s.train_set
    ,shuffle=False
    ,batch_size=s.batch_size)

test_preds = get_all_preds(network, data_loader)
ref_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(s.train_set.targets)).sum().item()

with open(s.report_path+s.report_fname,"w") as log_pointer:
    log_pointer.write("Reference accuracy = {}\n".format(ref_correct))
    print("Reference accuracy = {}\n".format(ref_correct))
    for quant_mode in s.quant_mode_list:
        for mask_mode in s.mask_mode_list:
            for i in range(1,s.stop_string): #all possible mask
                mask = printer_2s(i,s.bits)
                
                #generate base line accuracy
                guided_MaskTable_creator(network,s.maskConfig_path+s.config_fname, mask, gui=False)
                mask_table = MaskTable(quant_mode, mask_mode, [] , False, network, mask_file=s.maskConfig_path+s.config_fname)
                quantizer = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=s.aw_bits, bits_parameters=s.aw_bits, bits_accum=s.acc_bits,
                                                    mode=quant_mode, mask_table=mask_table,
                                                    scale_approx_mult_bits=s.bits)
                quantizer.model.to(s.device)
                quantizer.prepare_model(s.dummy_input)
                quantizer.model.eval()
                test_preds = get_all_preds(quantizer.model, data_loader,device=s.device)
                preds_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(s.train_set.targets).to(s.device)).sum().item()
                log_pointer.write(s.rep_string.format(quant_mode,mask_mode,mask))
                log_pointer.write(s.acc_string.format("BaseLine",preds_correct))
                print(s.rep_string.format(quant_mode,mask_mode,mask))
                print(s.acc_string.format("BaseLine",preds_correct))
                ref_correct = preds_correct
                del quantizer
                del mask_table

                #generate correct range accuracy            
                guided_MaskTable_creator(network,s.maskConfig_path+s.config_fname, mask, gui=False)
                mask_table = MaskTable(quant_mode, mask_mode, [] , True, network, mask_file=s.maskConfig_path+s.config_fname)
                quantizer = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=s.aw_bits, bits_parameters=s.aw_bits, bits_accum=s.acc_bits,
                                                    mode=quant_mode, mask_table=mask_table,
                                                    scale_approx_mult_bits=s.bits)
                quantizer.model.to(s.device)
                quantizer.prepare_model(s.dummy_input)
                quantizer.model.eval()
                test_preds = get_all_preds(quantizer.model, data_loader,device=s.device)
                preds_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(s.train_set.targets).to(s.device)).sum().item()
                log_pointer.write(s.acc_string.format("RangeCorrect",preds_correct))
                print(s.acc_string.format("RangeCorrect",preds_correct))
                rc_correct = preds_correct #for later improvements
                del quantizer
                del mask_table

                #generate accuracy without masking first and last layer
                guided_MaskTable_creator(network,s.maskConfig_path+s.config_fname, mask, gui=False)
                set_specific_layers(s.unmasked_layers,s.maskConfig_path+s.config_fname)
                mask_table = MaskTable(quant_mode, mask_mode, [] , False, network, mask_file=s.maskConfig_path+s.config_fname)
                quantizer = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=s.aw_bits, bits_parameters=s.aw_bits, bits_accum=s.acc_bits,
                                                    mode=quant_mode, mask_table=mask_table,
                                                    scale_approx_mult_bits=s.bits)
                quantizer.model.to(s.device)
                quantizer.prepare_model(s.dummy_input)
                quantizer.model.eval()
                test_preds = get_all_preds(quantizer.model, data_loader,device=s.device)
                preds_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(s.train_set.targets).to(s.device)).sum().item()
                log_pointer.write(s.acc_string.format("Unmasking layers",preds_correct))
                print(s.rep_string.format(quant_mode,mask_mode,mask))
                print(s.acc_string.format("Unmasking layers",preds_correct))
                del quantizer
                del mask_table

                #generate bias correction accuracy accuracy
                guided_MaskTable_creator(network,s.maskConfig_path+s.config_fname, mask, gui=False)
                mask_table = MaskTable(quant_mode, mask_mode, [] , False, network, mask_file=s.maskConfig_path+s.config_fname)
                quantizer = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=s.aw_bits, bits_parameters=s.aw_bits, bits_accum=s.acc_bits,
                                                    mode=quant_mode, mask_table=mask_table,
                                                    scale_approx_mult_bits=s.bits)
                ref_mask_table=MaskTable(LinearQuantMode.ASYMMETRIC_UNSIGNED, MaskType.MINIMUM_DISTANCE, [] , False, network)
                ref_quantized = PostTrainLinearQuantizer( deepcopy(network), bits_activations=s.aw_bits, bits_parameters=s.aw_bits, bits_accum=s.acc_bits,
                                    mode=LinearQuantMode.ASYMMETRIC_UNSIGNED, mask_table=ref_mask_table,
                                    scale_approx_mult_bits=s.bits)
                ref_quantized.prepare_model(s.dummy_input)
                quantizer.prepare_model(s.dummy_input)
                quantizer.model.eval()
                ref_quantized.model.eval()
                balanceNetwork_v2(ref_quantized.model,
                                quantizer.model,
                                s.train_set,
                                batch_size=500,
                                device="cpu")
                quantizer.model.to(s.device)
                test_preds = get_all_preds(quantizer.model, data_loader,device=s.device)
                preds_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(s.train_set.targets).to(s.device)).sum().item()
                log_pointer.write(s.acc_string.format("CompensatedBias",preds_correct))
                print(s.rep_string.format(quant_mode,mask_mode,mask))
                print(s.acc_string.format("CompensatedBias",preds_correct))
                del ref_quantized
                del quantizer
                del mask_table

                #applyng all the tree techniques
                if (rc_correct>ref_correct) and (rc_correct!=1000): #we need to avoid a completelly biased result
                    correct = True
                    ref_str = "RangeCorrect+LayerUnmasked+CompensatedBias" 
                else:
                    correct = False
                    ref_str = "LayerUnmasked+CompensatedBias" 
                guided_MaskTable_creator(network,s.maskConfig_path+s.config_fname, mask, gui=False)
                set_specific_layers(s.unmasked_layers,s.maskConfig_path+s.config_fname)
                mask_table = MaskTable(quant_mode, mask_mode, [] , correct, network, mask_file=s.maskConfig_path+s.config_fname)
                quantizer = PostTrainLinearQuantizer(   deepcopy(network), bits_activations=s.aw_bits, bits_parameters=s.aw_bits, bits_accum=s.acc_bits,
                                                    mode=quant_mode, mask_table=mask_table,
                                                    scale_approx_mult_bits=s.bits)
                ref_mask_table = MaskTable(LinearQuantMode.ASYMMETRIC_UNSIGNED, MaskType.MINIMUM_DISTANCE, [] , False, network)
                ref_quantized = PostTrainLinearQuantizer( deepcopy(network), bits_activations=s.aw_bits, bits_parameters=s.aw_bits, bits_accum=s.acc_bits,
                                    mode=LinearQuantMode.ASYMMETRIC_UNSIGNED, mask_table=ref_mask_table,
                                    scale_approx_mult_bits=s.bits)
                ref_quantized.prepare_model(s.dummy_input)
                quantizer.prepare_model(s.dummy_input)
                quantizer.model.eval()
                ref_quantized.model.eval()
                balanceNetwork_v2(ref_quantized.model,
                                quantizer.model,
                                s.train_set,
                                batch_size=500,
                                device="cpu")
                quantizer.model.to(s.device)
                test_preds = get_all_preds(quantizer.model, data_loader,device=s.device)
                preds_correct = test_preds.argmax(dim=1).eq(torch.LongTensor(s.train_set.targets).to(s.device)).sum().item()
                log_pointer.write(s.acc_string.format(ref_str,preds_correct))
                print(s.rep_string.format(quant_mode,mask_mode,mask))
                print(s.acc_string.format(ref_str,preds_correct))
                del quantizer
                del mask_table
