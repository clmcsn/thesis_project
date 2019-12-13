#!/usr/bin/env python3


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

report_name="../reports/analysis_postTrainMasking.txt"


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
print(len(container))
#print("_".join((container[1].quant_mode,container[1].mask,str(container[1].correctRange))))
quant_mode_list = ["SYMMETRIC","ASYMMETRIC_UNSIGNED","ASYMMETRIC_SIGNED"]
mask_mode_list = ["SIMPLE_MASK","ROUND_DOWN","ROUND_UP","MOD_ROUND_UP","MINIMUM_DISTANCE"]
bits = 8
maskWinner=False
quantModeWinner=False
bestCorrection=False
bestMask=True

if maskWinner:
    #winning masking algorithm
    dictionary={"SIMPLE_MASK":0,"ROUND_DOWN":0,"ROUND_UP":0,"MOD_ROUND_UP":0,"MINIMUM_DISTANCE":0}
    noneC=0
    for qm in quant_mode_list:
        signed= qm != "ASYMMETRIC_UNSIGNED"
        if signed:
            start_string = 2**(bits-1)
        else:
            start_string = 1
        for i in range(start_string,2**bits): #all possible mask we have
            mask = printer_2s(i,bits)
            mask = bit_string_inverter(mask)
            ones = mask.count("1")
            if(ones<=bits-4 and ones!=0): #filtering those for which we have results
                for j in [True,False]:
                    best_accuracy=0.0
                    winning=None
                    for entry in container:
                        if ((entry.quant_mode == qm) and (entry.mask == mask) and (entry.correctRange == j)):
                            if (entry.accuracy>best_accuracy):
                                best_accuracy = entry.accuracy
                                winning = entry.mask_type
                        #if ((entry.quant_mode == "SYMMETRIC") and (entry.mask == "00001010") and (entry.correctRange == True)):
                            #print("Halooo")
                            #print("_".join((entry.quant_mode,entry.mask,str(entry.correctRange),entry.mask_type)))
                    if winning:
                        dictionary[winning]+=1
                    else:
                        #print("_".join((qm,mask,str(j))))
                        noneC+=1
    for key in dictionary.keys():
        print(key,dictionary[key])
    print("NOT CLASSIFIED: " + str(noneC))

if quantModeWinner:
    #winning quant algorithm
    dictionary={"SYMMETRIC":0,"ASYMMETRIC_UNSIGNED":0,"ASYMMETRIC_SIGNED":0}
    noneC=0
    for mm in mask_mode_list:
        start_string = 2**(bits-1)
        for i in range(start_string,2**bits): #all possible mask we have
            mask = printer_2s(i,bits)
            mask = bit_string_inverter(mask)
            ones = mask.count("1")
            if(ones<=bits-4 and ones!=0): #filtering those for which we have results
                for j in [True,False]:
                    best_accuracy=0.0
                    winning=None
                    for entry in container:
                        if ((entry.mask_type == mm) and (entry.mask == mask) and (entry.correctRange == j)):
                            if (entry.accuracy>best_accuracy):
                                best_accuracy = entry.accuracy
                                winning = entry.quant_mode
                    if winning:
                        dictionary[winning]+=1
                    else:
                        #print("_".join((mm,mask,str(j))))
                        noneC+=1
    for key in dictionary.keys():
        print(key,dictionary[key])
    print("NOT CLASSIFIED: " + str(noneC))

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
                    winning=None
                    for entry in container:
                        if ((entry.quant_mode == qm) and (entry.mask_type == mm) and (entry.mask == mask)):
                            if (entry.accuracy>best_accuracy):
                                best_accuracy = entry.accuracy
                                winning = entry.correctRange
                    if not (winning==None):
                        if winning:
                            dictionary["Correct"]+=1
                        else:
                            dictionary["NotCorrect"]+=1
                    else:
                        #print("_".join((qm,mm,mask)))
                        noneC+=1
                    cycles+=1
    for key in dictionary.keys():
        print(key,dictionary[key])
    print("TOTAL POSSIBILITIES: " + str(cycles) + " NOT CLASSIFIED: " + str(noneC))

if bestMask:
    for energy_class in range(1,bits-3):
        #creting the dictionary
        dictionary={}
        start_string = 0
        for i in range(start_string,2**bits): #all possible mask we have
            mask = printer_2s(i,bits)
            mask = bit_string_inverter(mask)
            ones = mask.count("1")
            if ones==energy_class:
                dictionary[mask]=0
        cycles=0
        noneC=0
        for qm in quant_mode_list:
            signed= qm != "ASYMMETRIC_UNSIGNED"
            for mm in mask_mode_list:
                for j in (True,False):
                    best_accuracy=0.0
                    winning=None
                    for entry in container:
                        if ((entry.quant_mode == qm) and (entry.mask_type == mm) and (entry.correctRange == j)):
                            ones = entry.mask.count("1")
                            if ones==energy_class:
                                if (entry.accuracy>=best_accuracy):
                                    best_accuracy = entry.accuracy
                                    winning = entry.mask
                    if not (winning==None):
                        dictionary[winning]+=1
                    else:
                        #print("_".join((qm,mm,mask)))
                        noneC+=1
                    cycles+=1
        for key in dictionary.keys():
            print(key,dictionary[key])
        print("TOTAL POSSIBILITIES: " + str(cycles) + " NOT CLASSIFIED: " + str(noneC))

