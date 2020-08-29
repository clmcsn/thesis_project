import random
import subprocess
from common.hw_lib import twos_comp, printer_2s

# binStimFileGen(fname,lineNum,stimInLine,sign,bitDyn,nBit,delimiter):
#
# DESCRIPTION
#    Creates a file with <stimNum> stimuli.
# INPUT
#    Needs as inputs:
#       fname:      string with complete output file path nameself.
#       lineNum:    amount of lines.
#       stimInLine: how many stimuli in a line.
#       #TODO   signed is useless in fase of file creation (they will all be bit streams)
#               it just should be used in phase of interpretation 
#       signed:       touple with as many element as stimInLine
#                   True for positive and negative, False for only positive
#       bitDyn:     touple with as many element as stimInLine
#                   real dynamic of output numb.
#       nBit:       touple with as many element as stimInLine
#                   number of output bit in the string.
#       delimiter:  delimiter character between two consecutive stimuli.
#                   default value "\t"
# OUTPUT
#    Creates a file of stimuli in the specified path.
def binStimFileGen(fname,lineNum,stimInLine,signed,bitDyn,nBit,delimiter="\t"):
    if (stimInLine!=len(signed) or stimInLine!=len(bitDyn) or stimInLine!=len(nBit)):
        raise ValueError("Incoherent data provided.")
    with open(fname,"w") as fout_pointer:
        for i in range(lineNum):
            string=""
            for j in range(stimInLine):
                if(signed[j]):
                    num=random.randint(-2**(bitDyn[j]-1),2**(bitDyn[j]-1)-1)
                else:
                    num=random.randint(0,2**(bitDyn[j])-1)
                string+=printer_2s(num,nBit[j])
                string+=delimiter
            fout_pointer.write(string+"\n")

# binStimGen(sign,bitDyn,nBit):
#
# DESCRIPTION
#    Creates a binary stimulus.
# INPUT
#    Needs as inputs:
#       sign:       True for positive and negative, False for only positive
#       bitDyn:     real dynamic of output numb.
#       nBit:       number of output bit in the string.
# OUTPUT
#    Returns a stimulus.

def binStimGen(sign,bitDyn,nBit):
    if(sign):
        num=random.randint(-2**(bitDyn-1),2**(bitDyn-1)-1)
    else:
        num=random.randint(0,2**(bitDyn)-1)
    string=printer_2s(num,nBit)
    return string

# stimGen(sign,bitDyn):
#
# DESCRIPTION
#    Creates an integer stimulus.
# INPUT
#    Needs as inputs:
#       sign:       True for positive and negative, False for only positive
#       bitDyn:     real dynamic of output numb.
# OUTPUT
#    Returns a stimulus.

def stimGen(sign,bitDyn):
    if(sign):
        num=random.randint(-2**(bitDyn-1),2**(bitDyn-1)-1)
    else:
        num=random.randint(0,2**(bitDyn)-1)
    return num

# runSimulation(dotDoFilePath):
#
# DESCRIPTION
#   runs a simulation given a specific .do file
# INPUT
#    Needs as inputs:
#       dotDoFile:  the name of the file. The function works only if called by a script in the
#                   project/scripts directory

def runSimulation(dotDoFile):
    dotDoFilePath="../tbs/"+dotDoFile[:-3]+"/"+dotDoFile
    subprocess.call(["vsim", "-c", "-do", dotDoFilePath])
