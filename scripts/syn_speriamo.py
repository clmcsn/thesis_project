#!/usr/bin/env python3

import sys
sys.path.append('../')
import os

import common.settings as s
import common.util as util
import subprocess
import common.hw_lib as hwl

with util.ssh_session(s.ecs_user,s.ecs_host):
    #open asic session
    with util.ssh_session(s.asic_user,s.asic_host) as asic_server:
        csa=hwl.multiplier(8)
        #creating multiplier
        bin_str="11110111"
        zeros=bin_str.count("0")
        csa.setWeightValBits(bin_str)
        csa.genCsaStructure()
        csa.genCsaMultiplier()
        #copy multiplier.sv to server
        asic_server.copy_to(source=s.srcPath+"components/multiplier.sv",destination=s.synPart1Path+"src/")

        #create script
        with open("syn.tcl","w") as fout_pointer, open("template/syn.tcl","r") as fin_pointer:
            for line in fin_pointer:
                if s.signal_string in line:
                    fout_pointer.write("report_timing > ./report_timing_{}_{}.txt\n".format(zeros,bin_str))
                else:
                    fout_pointer.write(line)
        #copy script
        asic_server.copy_to("./syn.tcl",destination=s.synPart1Path+"syn/")
        #run synthesis
        print("Runnin synthesis. Blocked bits:{} String:{}".format(zeros,bin_str))
        asic_server.run_commands("""cd {}syn
            {setEnvironment}
            dc_shell-xg-t -f syn.tcl""".format(s.synPart1Path,setEnvironment=s.cmdSetSynEnv))
        try:
            os.mkdir(s.reportsPath+"csaReport_{}".format(zeros))
        except FileExistsError:
            pass
        asic_server.copy_from(s.synPart1Path+"syn/report_timing_{}_{}.txt".format(zeros,bin_str),s.reportsPath+"csaReport_{}".format(zeros))
