#!/usr/bin/env python3

import sys
sys.path.append('../')

import os
from os import walk

import common.settings as s
import common.analysis_lib as ana_lib

dirNames=[]
for (dirpath, dirnames, filenames) in walk(s.reportPath):
    dirNames.extend(dirnames)
    break
for dir in dirNames:
    for i,char in enumerate(dir):
        if (char=="_"):
            last_=i        
    ana_lib.makeRecap(s.reportPath+dir+"/",ana_lib.extractSlackTime,"report_timing",dir[last_+1:len(dir)])
