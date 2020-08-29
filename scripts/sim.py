#!/usr/bin/env python3

import sys
sys.path.append('../')
import os
import random as rand

from common.verification_util import binStimFileGen,runSimulation
import common.settings as s
import common.util as util
import subprocess
import common.hw_lib as hwl

def displayMenu():
    print("Welcome to the tester, what do you want ot simulate:")
    list=["AutoCsaMultiplier","PE_2s","PE_SM","exit"]
    for i in range(len(list)):
        print("{}) {}".format(i+1,list[i]))
    return len(list)


loop=True
while (loop):
    l=displayMenu()
    c=input()
    while (int(c)-1>int(l)):
        print("Choice out of range. Plese try again.")
        l=displayMenu()
        c=input()
    if (c=="1"):
        weightMask=input("Enter a weight validity string:\n")
        while(len(weightMask)!=s.weight_width):
            print("String has a different lenght. Try Again.")
            weightMask=input("Enter a weight validity string:\n")
        weightMask=weightMask[::-1]
        print("Input stimuli file will be automatically create!")
        with open(s.tbsPath+"tb_autoCsaMultiplier/tb_autoCsaMultiplier.txt","w") as fout_pointer:
            for i in range(pow(2,s.weight_width)):
                for j in range(pow(2,s.weight_width)):
                    printFlag=True
                    for k in range(s.weight_width):
                        num="{0:08b}".format(j)
                        if(weightMask[k]=="0" and num[-(k+1)]=="1"):
                            printFlag=False
                    if(printFlag==True):
                        fout_pointer.write("{0:08b} {1:08b}\n".format(i,j))
        #generate multiplier
        csa=hwl.multiplier(s.weight_width)
        csa.setWeightValBits(weightMask[::-1])
        csa.genCsaStructure()
        csa.genCsaMultiplier()
        #run simulation
        with util.cd(s.tbsPath+"tb_autoCsaMultiplier/project/"):
            new_env=os.environ.copy()
            new_env["NO_GUI"]="1"
            process=subprocess.Popen(["vsim -c -do ../tb-autoCsaMultiplier.tcl"],shell=True,cwd=os.getcwd(),env=new_env)
            process.wait()
        #check results
        with    open(s.tbsPath+"tb_autoCsaMultiplier/HWresult_autoCsaMultiplier.txt","r") as hwres_pointer, open(s.tbsPath+"tb_autoCsaMultiplier/tb_autoCsaMultiplier.txt","r") as insample_pointer, open("log.txt","w") as log_pointer:
            i=0
            error_count=0
            for line_sample, line_hwres in zip(insample_pointer,hwres_pointer):
                str_in=line_sample.split()
                a=int(str_in[0],2)
                b=int(str_in[1],2)
                c=int(line_hwres,2)
                if (a*b!=c):
                    error_count+=1
                    log_pointer.write("MISTAKE #{}\n".format(i))
                    log_pointer.write("Sample  :\t {} \t {}\n".format(a,b))
                    log_pointer.write("Expected:\t {} \n".format(a*b))
                    log_pointer.write("Had:     \t {} \n".format(c))
                    log_pointer.write("\n")
                i+=1
        if(error_count==0):
            print("Yeeeeee")
    elif (c=="2" or c=="3"): #complete PE

        def PE(a,w,s):
            return a*w+s
    
        print("Input stimuli file will be automatically create")
        stimuli_fname = s.tbsPath+"tb_PE/tb_PE.txt"
        binStimFileGen(fname=stimuli_fname, 
                        lineNum=s.num_sample,
                        stimInLine=3,
                        signed=[True,True,True],
                        bitDyn=[s.weight_width,s.weight_width,s.psum_width-1],
                        nBit=[s.weight_width,s.weight_width,s.psum_width])
        print("Runnin simulation through ModelSim")
        with util.cd(s.tbsPath+"tb_PE/project/"):
            process=subprocess.Popen(["vsim -c -do ../tb-PE.tcl"],shell=True,cwd=os.getcwd())
            process.wait()
        print("Checking results")
        with open(s.tbsPath+"tb_PE/HWresult_PE.txt","r") as hwres_pointer, open(s.tbsPath+"tb_PE/tb_PE.txt","r") as insample_pointer, open(s.tbsPath+"tb_PE/log.txt","w") as log_pointer:
            error_count=0
            for i,(line_sample, line_hwres) in enumerate(zip(insample_pointer,hwres_pointer)):
                str_in=line_sample.split()
                if (c=="2"):
                    a=hwl.string2s_to_int(str_in[0])
                    w=hwl.string2s_to_int(str_in[1])
                elif (c=="3"):
                    a=hwl.stringSM_to_int(str_in[0])
                    w=hwl.stringSM_to_int(str_in[1])
                s=hwl.string2s_to_int(str_in[2])
                sr=a*w+s
                hr=hwl.string2s_to_int(line_hwres.split()[0])
                if (sr!=hr):
                    error_count+=1
                    log_pointer.write("MISTAKE #{}\n".format(i))
                    log_pointer.write("Sample  :\t {} \t {} \t {}\n".format(a,w,s))
                    log_pointer.write("Expected:\t {} \n".format(sr))
                    log_pointer.write("Had:     \t {} \n".format(hr))
                    log_pointer.write("\n")
                
        if(error_count==0):
            print("Yeeeeee")
    elif (c==str(l)):
        print("Bye bye!")
        loop=False
