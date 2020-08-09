#!/usr/bin/env python3

import settings.optimizeNetwork_settings as s

from common.mask_util import MaskTable, compensateNetwork
from common.nnTools import test
from distiller.quantization import PostTrainLinearQuantizer

from copy import deepcopy

#create reference model
ref_mask_table=MaskTable(s.bits,s.quant_mode, s.mask_mode, s.network, [] , False)
ref_quantized = PostTrainLinearQuantizer( deepcopy(s.network), bits_activations=s.aw_bits, bits_parameters=s.aw_bits, bits_accum=s.acc_bits,
                    mode=s.quant_mode, mask_table=ref_mask_table,
                    scale_approx_mult_bits=s.bits)
ref_quantized.prepare_model(s.dummy_input)
ref_quantized.model.eval()
ref_quantized.model.to("cpu")

#loading mask
mask_table = MaskTable(s.bits,s.quant_mode, s.mask_mode, s.network, mask_file=s.config_fname)
quantizer = PostTrainLinearQuantizer( deepcopy(s.network), bits_activations=s.aw_bits, bits_parameters=s.aw_bits, bits_accum=s.acc_bits,
                    mode=s.quant_mode, mask_table=mask_table,
                    scale_approx_mult_bits=s.bits)

quantizer.prepare_model(s.dummy_input)
quantizer.model.eval()
compensateNetwork(ref_quantized.model,
                    quantizer.model,
                    s.test_set,
                    "../conf_files/conf_path.json",
                    batch_size=500,
                    device="cpu")
        
quantizer.model.to(s.device)
correct = test(quantizer.model,s.test_set,s.batch_size,s.device)
f1 = s.test_set_size - correct #top-1 error
with open(s.exchange_fname,"w") as out_p:
    out_p.write(str(f1))
