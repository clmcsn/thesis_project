#!/usr/bin/env python3

import sys
sys.path.append('../')

import os
from os import walk

import common.settings as s

# extractSlackTime(timing_rep_file):
#
# DESCRIPTION
#    Returns SLACK TIME out of a synopsys timing report.
# INPUT
#    Needs as inputs:
#       pointer to the timing report file
# OUTPUT
#    Returns slack time as integer
def extractSlackTime(timing_rep_file):
    with open(timing_rep_file,"r") as rep_pointer:
        for line in rep_pointer:
            if s.timingReportFindString in line:
                strings=line.split()
                return float(strings[3])
        print ("Slack time not found. Please check if {} is a Synopsys timing report file.".format(timing_rep_file))
        exit (1)
###############FUNZIONE SOPRA DA RIFARE IN MODO GENERALE PASSANDO COME PARAMETRO LA TRIGGER STRING



# extractFileList(path,ID):
#
# DESCRIPTION
#    Returns a file names list, in which every name matches an ID string
# INPUT
#    Needs as inputs:
#       path: directory where to extract file names.
#       ID  : string to identify which files.
# OUTPUT
#    Returns list of file names.
def extractFileList(path,ID):
    filelist=[]
    res_file_list=[]
    for (dirpath, dirnames, filenames) in walk(path):
        filelist.extend(filenames)
        break
    for x in filelist:
        if ID in x:
            res_file_list+=[x]
    return res_file_list

def makeRecap(reportDirectory,extractFunction,reportType,recapID):
    report_list=extractFileList(reportDirectory,reportType)
    with open(reportDirectory+"_recap_"+recapID,"w") as log_pointer:
        log_pointer.write("%% RECAP FILE for {} directory of {} type\n\n".format(reportDirectory,reportType))
        for rep_file in report_list:
            if reportType in rep_file:
                value=extractFunction(reportDirectory+rep_file)
                log_pointer.write("FILE:{}\t{}\n".format(rep_file,value))
        
