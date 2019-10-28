#!/usr/bin/env python3

import sys
sys.path.append('../')
import os

import common.settings as s
import common.util as util
import subprocess
import common.hw_lib as hwl

import datetime

# ==============================================================
# SET THESE VARIABLES BEFORE USING!!
remote_root = '/syn_part1/'
# ==============================================================

# print welcome message
print("""# =================================================================
# *****************************************************************
# ****************** Welcome to the synthesizer! ******************
# ************           {date}           ************
# *****************************************************************
# =================================================================\n""".format(date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

msg="What do you want to do:\n"
list=["Synthesize autoCsaMultipliers","Exit"]
c=util.get_choice(list,msg=msg)
if (c==1): #case we want to synthesize all csaTree
    #open ecs session
    with util.ssh_session(s.ecs_user,s.ecs_host):
        #open asic session
        with util.ssh_session(s.asic_user,s.asic_host) as asic_server:
            for i in range(pow(2,s.weight_width)):
                bin_str="{0:08b}".format(i) #NOT GENERAL LINE
                zeros=bin_str.count("0")
                if (zeros<=s.max_forcedBits):
                    #creating multiplier
                    csa=hwl.multiplier(s.weight_width)
                    csa.setWeightValBits(bin_str)
                    csa.genCsaStructure()
                    csa.genCsaMultiplier()
                    #copy multiplier.sv to server
                    asic_server.copy_to(source=s.srcPath+"/components/multiplier.sv",destination=s.synPart1Path+"src/")
                    #create script
                    with open("syn.tcl","w") as fout_pointer, open("template/syn.tcl","r") as fin_pointer:
                        for line in fin_pointer:
                            if s.signal_string in line:
                                fout_pointer.write("report_timing -significant_digits 10 > ./report_timing_{}_{}.txt\n".format(zeros,bin_str))
                            else:
                                fout_pointer.write(line)
                    #clean the synthesis directory
                    asic_server.clean("~/syn_part1/syn")
                    #copy script and setup file
                    asic_server.copy_to("../syn/.synopsys_dc.setup",destination=s.synPart1Path+"syn/")
                    asic_server.copy_to("syn.tcl",destination=s.synPart1Path+"syn/")
                    #run synthesis
                    print("Runnin synthesis. Blocked bits:{} String:{}".format(zeros,bin_str))
                    asic_server.run_commands("""cd {}syn
                        mkdir work
                        {setEnvironment}
                        dc_shell-xg-t -f syn.tcl""".format(s.synPart1Path,setEnvironment=s.cmdSetSynEnv))
                    try:
                        os.mkdir(s.reportsPath+"csaReport_{}".format(zeros))
                    except FileExistsError:
                        pass
                    asic_server.copy_from(s.synPart1Path+"syn/report_timing_{}_{}.txt".format(zeros,bin_str),s.reportsPath+"csaReport_{}".format(zeros))
                    os.remove("syn.tcl")
                    del csa
elif (c==len(list)):
    exit()
