#!/usr/bin/env python3

import sys
sys.path.append('../')
import os

from common.verification_util import binStimFileGen,runSimulation
import common.settings as s
import common.util as util
import subprocess
import common.hw_lib as hwl

def displayMenu():
    print("Welcome to the tester, what do you want ot simulate:")
    list=["AutoCsaMultiplier","exit"]
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
                        num="{0:b}".format(j)
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
    elif (c=="2"):
        print("Bye bye!")
        loop=False
