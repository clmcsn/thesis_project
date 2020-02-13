#!/usr/bin/env python3

import sys
sys.path.append("../")

from common.mask_util import get_mask_hwCharact,set_specific_layers, guided_MaskTable_creator, MaskTable, MaskLayerProperty, saveLayerTable
from common.nnTools import get_layer_dict, test
import settings.optimizeNetwork_settings as s

import distiller
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode

from copy import deepcopy

#fetching the characterization mask
print("Fetching mask characterization from {}...\n".format(s.maskTimingCharFile))
mask_charact_dict = get_mask_hwCharact(s.maskTimingCharFile)
#it is important to sort dictionary for simplify the code later.
#during the characterization there wouldn't be the need to check for dominated solutions
#in the table
mask_charact_dict = {k: v for k, v in sorted(mask_charact_dict.items(), key=lambda item: item[1])}

#fetch network description
print("Fetching network description from {}...\n".format(s.network_file_descriptor))
network_description = get_layer_dict(s.network_file_descriptor)

#filling table as dictionary of dictionaries
if s.toCharact:
    print("Creating layer-wise characterization table...")
    LayerTable = {}
    for layer in network_description.keys():
        print("Processing {} layer".format(layer))
        LayerTable[layer] = {}
        for mask in mask_charact_dict.keys():
            #generate test network
            guided_MaskTable_creator(s.network,s.maskConfig_path+s.config_fname, std_mask="00000000",correctRange=False, gui=False) #generate file with no masks
            set_specific_layers([layer],s.maskConfig_path+s.config_fname,mask) # set only the layer I want to mask
            mask_table = MaskTable(s.quant_mode, s.mask_mode, [] , False, s.network, mask_file=s.maskConfig_path+s.config_fname)
            quantizer = PostTrainLinearQuantizer(   deepcopy(s.network), bits_activations=s.aw_bits, bits_parameters=s.aw_bits, bits_accum=s.acc_bits,
                                                        mode=s.quant_mode, mask_table=mask_table,
                                                        scale_approx_mult_bits=s.bits)
            quantizer.model.to(s.device)
            quantizer.prepare_model(s.dummy_input)
            quantizer.model.eval()
            falseC_preds=test(quantizer.model, s.test_set, batch_size=s.batch_size, device=s.device)
            del quantizer
            del mask_table
            #generate test network
            guided_MaskTable_creator(s.network,s.maskConfig_path+s.config_fname, std_mask="00000000",correctRange=True, gui=False) #generate file with no masks
            set_specific_layers([layer],s.maskConfig_path+s.config_fname,mask) # set only the layer I want to mask
            mask_table = MaskTable(s.quant_mode, s.mask_mode, [] , True, s.network, mask_file=s.maskConfig_path+s.config_fname)
            quantizer = PostTrainLinearQuantizer(   deepcopy(s.network), bits_activations=s.aw_bits, bits_parameters=s.aw_bits, bits_accum=s.acc_bits,
                                                        mode=s.quant_mode, mask_table=mask_table,
                                                        scale_approx_mult_bits=s.bits)
            quantizer.model.to(s.device)
            quantizer.prepare_model(s.dummy_input)
            quantizer.model.eval()
            trueC_preds=test(quantizer.model, s.test_set, batch_size=s.batch_size, device=s.device)
            del quantizer
            del mask_table
            #select the winner
            if trueC_preds>falseC_preds and trueC_preds!=1000:
                correct=True
                accuracy=trueC_preds
            else:
                correct=False
                accuracy=falseC_preds
            
            #insert the mask into the table. Must check if dominated!
            dominated=False
            for value in LayerTable[layer].values():
                """In this part I can add the voltage underscaling part"""
                if value.accuracy>accuracy:
                    dominated=True
                    break
            if not dominated:
                LayerTable[layer][mask]=MaskLayerProperty(correct,accuracy)
                print("Adding to {}:".format(layer))
                print("\t Mask:{}\t{}\t{}".format(mask,correct, accuracy))
    saveLayerTable(LayerTable,s.maskCharactFile)
else:
    print("Mask where already characterized.\n{} file found.".format(s.maskCharactFile))
    LayerTable = loadLayerTable(s.maskCharactFile)
