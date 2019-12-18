#!/usr/bin/env python3

import os
import sys
sys.path.append("../")
from common.mask_util import MaskStat
from common.hw_lib import printer_2s
from copy import deepcopy

def bit_string_inverter(string):
    new=""
    for i in string:
        if i=="0":
            new+="1"
        else:
            new+="0"
    return new

net="CustomLeNet"
dataset="CIFAR10"
info="postTrainMasking"
report_name="../reports/data_{}{}_{}.txt".format(net,dataset,info)
log_name="../reports/dataAnalysis_{}_{}_{}.txt".format(net,dataset,info)
log_name_eaw="../reports/dataAnalysisEnergyAware_{}_{}_{}.txt".format(net,dataset,info)


#getting datas
container = []
with open(report_name,"r") as rep_pointer:
    for line in rep_pointer:
        data = line.split()
        qm = data[1].split(".")[1]
        mm = data[3].split(".")[1]
        m = data[5]
        c = data[6].split(":")[1]
        correct = int(data[8])
        accuracy = float(data[10])
        if (m[0] != "1"):
            container += [MaskStat(  quant_mode=qm,
                                    mask_type=mm,
                                    mask=m,
                                    correctRange=c,
                                    correct_preds=correct,
                                    accuracy=accuracy,
                                    model_name="LeNet")]
#list of choices
quant_mode_list = ["SYMMETRIC","ASYMMETRIC_UNSIGNED","ASYMMETRIC_SIGNED"]
mask_mode_list = ["SIMPLE_MASK","ROUND_DOWN","ROUND_UP","MOD_ROUND_UP","MINIMUM_DISTANCE"]
bits = 8
start_string = 2**(bits-1)
mask_list=[]
for i in range(start_string,2**bits): #all possible mask we have (THIS MUST BE FILTERED OUT)
    mask = printer_2s(i,bits)
    mask = bit_string_inverter(mask)
    ones = mask.count("1")
    if(ones<=bits-4 and ones!=0): #filtering those for which we have results
        mask_list += [mask]
correctRange_list = ["True","False"]
parameter_dictionary={  "quant_mode": quant_mode_list,
                        "mask_type" : mask_mode_list,
                        "mask"      : mask_list,
                        "correctRange": correctRange_list}

def printResult(rep_fname,open_mode,param_analysis,param_list,cycles,dictionary,minimum,energy_class=None):
    if energy_class:
        en_str="for energy class {}".format(energy_class)
    else:
        en_str=""
    with open(rep_fname,open_mode) as log_pointer:
        log_pointer.write("{} parameter analysis {}\n".format(param_analysis.upper(),en_str))
        log_pointer.write("Swing parameters: {} \n".format(" - ".join(param_list)))
        log_pointer.write("Total cases: {}\t Total accuracy = sum{for i in range(Total cases)}(accuracy_i) - Min".format(cycles))
        for key in dictionary.keys():
            log_pointer.write("\tMasking type: {}\t Winning count: {}\t Total accuracy: {:.3f} (Min: {:.3f})\n".format(key,dictionary[key][1],dictionary[key][0],minimum))
        log_pointer.write("\n\n")


def loop_analysis(container,paramDic,paramToAnalyze,rep_fname,energy_class=None):
    #creating dictionary score board
    score_board={}
    for element in paramDic[paramToAnalyze]:
        score_board[element]=[0,0] #it's a list first used for number of wins, second for overall accuracy

    #creating list of parameters to be analyzed
    param_list=[]
    for key in paramDic.keys():
        if key!=paramToAnalyze:
            param_list+=[key]

    #choosing file opening mode
    try:
        f = open(rep_fname)
        openMode="a"
    except IOError:
        print("File {} not exist. It will be created!".format(rep_fname))
        openMode="w"
    finally:
        if openMode=="a":
            f.close()
        else:
            pass

    cycles=0
    for option1 in paramDic[param_list[0]]:
        for option2 in paramDic[param_list[1]]:
            for option3 in paramDic[param_list[2]]:
                cycles+=1
                best_accuracy=0.0
                winning=[]
                for entry in container:
                    if ((getattr(entry,param_list[0]) == option1) and (getattr(entry,param_list[1]) == option2) and (getattr(entry,param_list[2]) == option3)):
                        score_board[getattr(entry,paramToAnalyze)][0]+=entry.accuracy
                        if (entry.accuracy==best_accuracy): #first we check if it's equal!
                            winning += [getattr(entry,paramToAnalyze)]
                        if (entry.accuracy>best_accuracy): #then if is higher and if there is the need to upload 
                            winning=[] #reset list of winning parameters
                            best_accuracy = entry.accuracy
                            winning += [getattr(entry,paramToAnalyze)]
                if winning:
                    if best_accuracy>0.1:
                        for e in winning:
                            score_board[e][1]+=1
    l=[] #support list for getting the minimum
    for item in score_board.values():
        l+=[item[0]]
    minimum=min(l)
    for key in score_board.keys():
        score_board[key][0]-=minimum
    printResult(rep_fname, openMode, paramToAnalyze, param_list, cycles, score_board, minimum, energy_class)

def loop_analysis_energyAware(container,paramDic,paramToAnalyze,bits,energy_class,rep_fname):
    container_e=[]
    for entry in container:
        ones = entry.mask.count("1")
        if ones==energy_class:
            container_e+=[entry]
    mask_list=[]
    for i in range(2**(bits-1),2**bits): #all possible mask we have (THIS MUST BE FILTERED OUT)
        mask = printer_2s(i,bits)
        mask = bit_string_inverter(mask)
        ones = mask.count("1")
        if(ones<=bits-4 and ones!=0 and ones==energy_class): #filtering those for which we have results
            mask_list += [mask]
    paramDic_e=deepcopy(paramDic)
    paramDic_e["mask"]=mask_list
    loop_analysis(container_e,paramDic_e,paramToAnalyze,rep_fname,energy_class=energy_class)
    del paramDic_e
    del container_e
#print(len(container))
#print("_".join((container[1].quant_mode,container[1].mask,str(container[1].correctRange))))

####################SETTINGS##################################
maskWinner=1
quantModeWinner=1
bestCorrection=1
bestMask=1
quantVsMask=1
####################SETTINGS###################################
try: 
    os.remove(log_name) #remove file
except FileNotFoundError:
    pass

#loop_analysis_energyAware(container, parameter_dictionary, "quant_mode", bits, 2, log_name)
#exit()
loop_analysis(container, parameter_dictionary, "quant_mode", log_name)
loop_analysis(container, parameter_dictionary, "mask_type", log_name)
loop_analysis(container, parameter_dictionary, "mask", log_name)
loop_analysis(container, parameter_dictionary, "correctRange", log_name)
for energy_class in range(1,bits-3):
    loop_analysis_energyAware(container, parameter_dictionary, "quant_mode", bits, energy_class, log_name_eaw)
    loop_analysis_energyAware(container, parameter_dictionary, "mask_type", bits, energy_class, log_name_eaw)
    loop_analysis_energyAware(container, parameter_dictionary, "mask", bits, energy_class, log_name_eaw)
    loop_analysis_energyAware(container, parameter_dictionary, "correctRange", bits, energy_class, log_name_eaw)

#best accuracy for energy class
quantDic={}
quant_rep_file="../reports/data_CustomLeNet_postTrainQuantization.txt"
with open(quant_rep_file,"r") as quant_pointer:
    for line in quant_pointer:
        data=line.split()
        qm=data[1].split(".")[1]
        eb=8-int(data[3])
        ac=float(data[7])
        if not (qm in quantDic.keys()):
            quantDic[qm]={}
        quantDic[qm][eb]=ac


for energy_class in range(1,bits-3):
    best_accuracy=0
    best_accuracy_data=None
    mask_win=0
    for entry in container:
        ones=entry.mask.count("1")
        if ((ones==energy_class) and (not (entry.mask[0]=="1"))):
            if entry.accuracy > best_accuracy:
                best_accuracy=entry.accuracy
                best_accuracy_data = entry
            if entry.accuracy > quantDic[entry.quant_mode][energy_class]:
                mask_win+=1
    #print results
    with open(log_name_eaw,"a") as log_pointer:
        log_pointer.write("Energy class {} final evaluation\n".format(energy_class))
        log_pointer.write("\tBest mask: {} {} {} {}\n".format(best_accuracy_data.quant_mode,best_accuracy_data.mask_type,best_accuracy_data.mask,best_accuracy_data.correctRange))
        log_pointer.write("\tMask accuracy: {} \t Equivalent quant architecture: {}\n".format(best_accuracy_data.accuracy,quantDic[entry.quant_mode][energy_class]))
        log_pointer.write("\tBetter maskings on same quantization type: {}\n".format(mask_win))
        log_pointer.write("\n\n")

