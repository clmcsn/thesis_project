#!/usr/bin/env python3
import sys
sys.path.append("../")

from common.mask_util import get_mask_hwCharact,set_specific_layers, guided_MaskTable_creator, MaskTable, MaskLayerProperty, saveLayerTable, LayerAttributes, stringMask_to_list, balanceNetwork_v2
from common.nnTools import get_layer_dict, test, get_layersName_list, get_network_mults
import settings.optimizeNetwork_settings as s

import distiller
from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode

from copy import deepcopy
import numpy as np
import autograd.numpy as anp

from pymoo.algorithms.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.model.problem import Problem
from pymoo.visualization.scatter import Scatter
from pymoo.model.termination import MaximumFunctionCallTermination,MaximumGenerationTermination
from pymoo.operators.integer_from_float_operator import IntegerFromFloatSampling
from pymoo.operators.sampling.random_sampling import FloatRandomSampling
from pymoo.operators.integer_from_float_operator import IntegerFromFloatCrossover
from pymoo.operators.crossover.simulated_binary_crossover import SimulatedBinaryCrossover
from pymoo.operators.mutation.polynomial_mutation import PolynomialMutation
from pymoo.operators.integer_from_float_operator import IntegerFromFloatMutation
from threading import Thread
from queue import Queue

def getAccuracy(layerListTable,ref_model,q):
    import sys
    sys.path.append("../")
    import settings.optimizeNetwork_settings as s
    from distiller.quantization import PostTrainLinearQuantizer, LinearQuantMode
    from common.mask_util import get_mask_hwCharact,set_specific_layers, guided_MaskTable_creator, MaskTable, MaskLayerProperty, saveLayerTable, LayerAttributes, stringMask_to_list, balanceNetwork_v2
    #create Table
    maskT = MaskTable(s.quant_mode,s.mask_mode,s.network,mask_dict=layerListTable)
    quantizer = PostTrainLinearQuantizer(   deepcopy(s.network), bits_activations=s.aw_bits, bits_parameters=s.aw_bits, bits_accum=s.acc_bits,
                                            mode=s.quant_mode, mask_table=maskT,
                                            scale_approx_mult_bits=s.bits)
    #quantizer.model.to("cpu")
    quantizer.prepare_model(s.dummy_input)
    quantizer.model.eval()
    balanceNetwork_v2(ref_model,
                            quantizer.model,
                            s.test_set,
                            batch_size=500,
                            device="cpu")
    quantizer.model.to(s.device)
    correct = test(quantizer.model,s.test_set,s.batch_size,s.device)
    f1 = s.test_set_size - correct #top-1 error
    q.put(f1)

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
total_mult = get_network_mults(network_description)

#mask dictionary used for genetic algorithm
mask_dict={}
i=0
for mask in mask_charact_dict.keys():
    mask_dict[i]=mask+"_0" #0 stands for not correcting the range
    i+=1
    mask_dict[i]=mask+"_1" #1 stands for correcting the range
    i+=1

ref_mask_table=MaskTable(s.quant_mode, s.mask_mode, s.network, [] , False)
ref_quantized = PostTrainLinearQuantizer( deepcopy(s.network), bits_activations=s.aw_bits, bits_parameters=s.aw_bits, bits_accum=s.acc_bits,
                    mode=s.quant_mode, mask_table=ref_mask_table,
                    scale_approx_mult_bits=s.bits)
ref_quantized.prepare_model(s.dummy_input)
ref_quantized.model.eval()
ref_quantized.model.to("cpu")

class MaskingDNN(Problem):
    def __init__(self):
        super().__init__(n_var=9, n_obj=2, n_constr=1,
                            xl=0, xu=63, type_var=np.int,
                            elementwise_evaluation=True)
        self.first=True
    
    def _evaluate(self, x, out, *args, **kwargs):
        
        #F1: ACCURACY EVALUATION
        #Creating Mask List
        layerListTable={}
        for i,layer in enumerate(get_layersName_list(s.network)):
            #TODO check if layers are ordered
            m = mask_dict[int(x[i])].split("_")
            mask = m[0]
            correct = bool(int(m[1]))
            layerListTable[layer] = LayerAttributes(stringMask_to_list(mask),correct)
        if __name__ == '__main__':

            q = Queue()
            p = Thread(target=getAccuracy, args=(layerListTable,ref_quantized.model,q,))
            p.start()
            f1=q.get()
            p.join() 
        g1 = f1 - s.max_top1 #constraints of accuracy --> top1-max_top1<=0
        #F2: AVERAGE DELAY
        delay=0
        for i, m in enumerate(x): #TODO check this get bot layer and mask correct
            mask_delay = mask_charact_dict[mask_dict[int(m)].split("_")[0]] #from mask_correctRange I have to take just the mask
            layer_mult = network_description[list(network_description.keys())[i]].get_numMult()
            delay+=mask_delay*layer_mult/total_mult
        f2 = delay
        out["F"] = anp.column_stack([f1, f2]) 
        out["G"] = g1

problem = MaskingDNN()
algorithm = NSGA2(pop_size=s.pop_size,
                  sampling=IntegerFromFloatSampling(clazz=FloatRandomSampling),
                  crossover=IntegerFromFloatCrossover(clazz=SimulatedBinaryCrossover,prob=0.9,eta=15),
                  mutation=IntegerFromFloatMutation(clazz=PolynomialMutation,eta=20),
                  n_offsprings=s.n_offsprings)
res = minimize(problem,
                algorithm,
                ('n_gen', s.n_gen),
                seed=1,
                verbose=True)
print(res.F)
print(res.X)
