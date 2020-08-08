#!/usr/bin/env python3
import os
import sys
sys.path.append("../")

from common.mask_util import get_mask_hwCharact, MaskTable, LayerAttributes, stringMask_to_list, saveLayerAttributesDictionary_toFile
from common.nnTools import get_layer_dict, test, get_layersName_list, get_network_mults
import settings.optimizeNetwork_settings as s

import numpy as np
import autograd.numpy as anp
import time

from pymoo.algorithms.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.model.problem import Problem
from pymoo.model.termination import MaximumFunctionCallTermination,MaximumGenerationTermination
from pymoo.operators.integer_from_float_operator import IntegerFromFloatSampling,IntegerFromFloatMutation, IntegerFromFloatCrossover
from pymoo.operators.sampling.random_sampling import FloatRandomSampling
from pymoo.operators.crossover.simulated_binary_crossover import SimulatedBinaryCrossover
from pymoo.operators.mutation.polynomial_mutation import PolynomialMutation
import subprocess

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
            layerListTable[layer] = LayerAttributes(mask,correct)
        #generate mask configuration file
        saveLayerAttributesDictionary_toFile(layerListTable,s.config_fname)
        #run script
        subprocess.call([s.getAccuracy_script_name])
        #collect result
        with open(s.exchange_fname,"r") as in_p:
            f1 = int(in_p.readline())
        os.remove(s.exchange_fname)
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
start_time = time.time()
res = minimize(problem,
                algorithm,
                ('n_gen', s.n_gen),
                seed=1,
                verbose=True)
print("--- %s seconds ---" % (time.time() - start_time))
print(res.F)
print(res.X)
with open(s.res_file,"w") as out_pointer:
    for f, x in zip(list(res.F),list(res.X)):
        out_pointer.write("{}\t{}\n".format(f,x))
