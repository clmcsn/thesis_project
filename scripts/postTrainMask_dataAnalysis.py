#!/usr/bin/env python3

import os
import sys
sys.path.append("../")
from common.mask_util import MaskStat
from common.hw_lib import printer_2s

def bit_string_inverter(string):
    new=""
    for i in string:
        if i=="0":
            new+="1"
        else:
            new+="0"
    return new

def str_to_bool(string):
    if string=="True":
        return True
    else:
        return False

report_name="../reports/data_CustomLeNetCIFAR10_postTrainMasking.txt"
log_name="../reports/dataAnalysis_CustomLeNetCIFAR10_postTrainMasking.txt"

#getting datas
container = []
with open(report_name,"r") as rep_pointer:
    for line in rep_pointer:
        data = line.split()
        qm = data[1].split(".")[1]
        mm = data[3].split(".")[1]
        m = data[5]
        c = str_to_bool(data[6].split(":")[1])
        correct = int(data[8])
        accuracy = float(data[10])
        if (correct > 1000):
            container += [MaskStat(  quant_mode=qm,
                                    mask_type=mm,
                                    mask=m,
                                    correctRange=c,
                                    correct_preds=correct,
                                    accuracy=accuracy,
                                    model_name="LeNet")]
#print(len(container))
#print("_".join((container[1].quant_mode,container[1].mask,str(container[1].correctRange))))
quant_mode_list = ["SYMMETRIC","ASYMMETRIC_UNSIGNED","ASYMMETRIC_SIGNED"]
mask_mode_list = ["SIMPLE_MASK","ROUND_DOWN","ROUND_UP","MOD_ROUND_UP","MINIMUM_DISTANCE"]
bits = 8
####################SETTINGS##################################
maskWinner=1
quantModeWinner=1
bestCorrection=1
bestMask=1
####################SETTINGS###################################
try: 
    os.remove(log_name) #remove file
except FileNotFoundError:
    pass

if maskWinner:
    #winning masking algorithm
    dictionary={"SIMPLE_MASK":0,"ROUND_DOWN":0,"ROUND_UP":0,"MOD_ROUND_UP":0,"MINIMUM_DISTANCE":0}
    cycles=0
    noneC=0
    for qm in quant_mode_list: #for every possible quantization mode
        signed= qm != "ASYMMETRIC_UNSIGNED"
        if signed:
            start_string = 2**(bits-1)
        else:
            start_string = 1
        for i in range(start_string,2**bits): #all possible mask we have (THIS MUST BE FILTERED OUT)
            mask = printer_2s(i,bits)
            mask = bit_string_inverter(mask)
            ones = mask.count("1")
            if(ones<=bits-4 and ones!=0): #filtering those for which we have results
                for j in [True,False]: #correction swing parameter
                    cycles+=1
                    best_accuracy=0.0
                    winning=[]
                    for entry in container:
                        if ((entry.quant_mode == qm) and (entry.mask == mask) and (entry.correctRange == j)):
                            if (entry.accuracy==best_accuracy): #first we check if it's equal!
                                winning += [entry.mask_type]
                            if (entry.accuracy>best_accuracy): #then if is higher and if there is the need to upload 
                                winning=[] #reset list of winning parameters
                                best_accuracy = entry.accuracy
                                winning += [entry.mask_type]
                    if winning:
                        for e in winning:
                            dictionary[e]+=1
                    else:
                        noneC+=1
                    
    #print results
    with open(log_name,"w") as log_pointer:
        log_pointer.write("Masking Type best accuracy count\n")
        log_pointer.write("Swing parameters: Quantization Mode - Mask - Correcting Range\n")
        log_pointer.write("Total cases:{}\t Non significant cases:{}\n".format(cycles,noneC))
        for key in dictionary.keys():
            log_pointer.write("\tMasking type: {}\t Winning count: {}\n".format(key,dictionary[key]))
        log_pointer.write("\n\n")

if quantModeWinner:
    #winning quant algorithm
    dictionary={"SYMMETRIC":0,"ASYMMETRIC_UNSIGNED":0,"ASYMMETRIC_SIGNED":0}
    cycles=0
    noneC=0
    for mm in mask_mode_list:
        start_string = 2**(bits-1) ##I SELECT ONLY THOSE RUN FOR THE WIN
        for i in range(start_string,2**bits): #all possible mask we have
            mask = printer_2s(i,bits)
            mask = bit_string_inverter(mask)
            ones = mask.count("1")
            if(ones<=bits-4 and ones!=0): #filtering those for which we have results
                for j in [True,False]:
                    cycles+=1
                    best_accuracy=0.0
                    winning=[]
                    for entry in container:
                        if ((entry.mask_type == mm) and (entry.mask == mask) and (entry.correctRange == j)):
                            if (entry.accuracy==best_accuracy): #first we check if it's equal!
                                winning += [entry.quant_mode]
                            if (entry.accuracy>best_accuracy):
                                winning = []
                                best_accuracy = entry.accuracy
                                winning += [entry.quant_mode]
                    if winning:
                        for e in winning:
                            dictionary[e]+=1
                    else:
                        #print("_".join((mm,mask,str(j))))
                        noneC+=1
    #print results
    with open(log_name,"a") as log_pointer:
        log_pointer.write("Quantization Type best accuracy count\n")
        log_pointer.write("Swing parameters: Masking Mode - Mask - Correcting Range\n")
        log_pointer.write("Total cases:{}\t Non significant cases:{}\n".format(cycles,noneC))
        for key in dictionary.keys():
            log_pointer.write("\Quantization type: {}\t Winning count: {}\n".format(key,dictionary[key]))
        log_pointer.write("\n\n")

if bestCorrection:
    #winning correction or not correction
    dictionary={"Correct":0,"NotCorrect":0}
    cycles=0
    noneC=0
    for qm in quant_mode_list:
        signed= qm != "ASYMMETRIC_UNSIGNED"
        if signed:
            start_string = 2**(bits-1)
        else:
            start_string = 1
        for mm in mask_mode_list:
            for i in range(start_string,2**bits): #all possible mask we have
                mask = printer_2s(i,bits)
                mask = bit_string_inverter(mask)
                ones = mask.count("1")
                if(ones<=bits-4 and ones!=0): #filtering those for which we have results
                    best_accuracy=0.0
                    winning=[]
                    for entry in container:
                        if ((entry.quant_mode == qm) and (entry.mask_type == mm) and (entry.mask == mask)):
                            if (entry.accuracy==best_accuracy):
                                winning+=[entry.correctRange]
                            if (entry.accuracy>best_accuracy):
                                winning=[]
                                best_accuracy = entry.accuracy
                                winning += [entry.correctRange]
                    if winning:
                        for e in winning:
                            if e:
                                dictionary["Correct"]+=1
                            else:
                                dictionary["NotCorrect"]+=1
                    else:
                        #print("_".join((qm,mm,mask)))
                        noneC+=1
                    cycles+=1
    #print results
    with open(log_name,"a") as log_pointer:
        log_pointer.write("Correction policy best accuracy count\n")
        log_pointer.write("Swing parameters: Quantization Mode - Masking Mode - Mask\n")
        log_pointer.write("Total cases:{}\t Non significant cases:{}\n".format(cycles,noneC))
        for key in dictionary.keys():
            log_pointer.write("\tCorrect: {}\t Winning count: {}\n".format(key,dictionary[key]))
        log_pointer.write("\n\n")

if bestMask:
    for energy_class in range(1,bits-3):
        #creting the dictionary
        dictionary={}
        start_string = 2**(bits-1) #msb masking always get lower accuracy, useless to include them
        #creating dictionary structure
        for i in range(start_string,2**bits): #all possible mask we have
            mask = printer_2s(i,bits)
            mask = bit_string_inverter(mask)
            ones = mask.count("1")
            if ones==energy_class:
                dictionary[mask]=0
        #init loop
        cycles=0
        noneC=0
        for qm in quant_mode_list:
            signed= qm != "ASYMMETRIC_UNSIGNED"
            for mm in mask_mode_list:
                for j in (True,False):
                    best_accuracy=0.0
                    winning=[]
                    for entry in container:
                        if ((entry.quant_mode == qm) and (entry.mask_type == mm) and (entry.correctRange == j)):
                            if not (entry.mask[0]=="1"): #msb masking always get lower accuracy, useless to include them
                                ones = entry.mask.count("1")
                                if ones==energy_class:
                                    if (entry.accuracy==best_accuracy):
                                        winning+=[entry.mask]
                                    if (entry.accuracy>best_accuracy):
                                        winning=[]
                                        best_accuracy = entry.accuracy
                                        winning += [entry.mask]
                    if winning:
                        for e in winning:
                            dictionary[e]+=1
                    else:
                        #print("_".join((mm,mask,str(j))))
                        noneC+=1
                    cycles+=1
        #print results
        with open(log_name,"a") as log_pointer:
            log_pointer.write("Mask for energy class {} best accuracy count\n".format(energy_class))
            log_pointer.write("Swing parameters: Quantization Mode - Masking Mode - Range correct\n")
            log_pointer.write("Total cases:{}\t Non significant cases:{}\n".format(cycles,noneC))
            for key in dictionary.keys():
                log_pointer.write("\tCorrect: {}\t Winning count: {}\n".format(key,dictionary[key]))
            log_pointer.write("\n\n")

