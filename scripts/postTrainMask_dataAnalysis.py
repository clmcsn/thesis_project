#!/usr/bin/env python3


import sys
sys.path.append("../")
from common.mask_util as MaskStat

report_name_"../reports/analysis_postTrainMasking.txt"


#getting datas
container = []
with open(report_name,"r") as rep_pointer:
    for line in rep_pointer:
        data = line.split()
        qm = data[1].split(.)[1]
        mm = data[3].split(.)[1]
        m = data[5]
        c = data[7]
        correct = int(data[9])
        accuracy = float(data[11])
        if (correct > 1000):
            container += MaskStat(  quant_mode=qm,
                                    mask_type=mm
                                    mask=m,
                                    correctRange=c,
                                    correct_preds=correct,
                                    accuracy=accuracy,
                                    model_name="LeNet")

quant_mode_list = ["SYMMETRIC","ASYMMETRIC_UNSIGNED","ASYMMETRIC_SIGNED"]
mask_mode_list = ["SIMPLE_MASK","ROUND_DOWN","ROUND_UP","MOD_ROUND_UP","MINIMUM_DISTANCE"]
#winning algorithm
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
                