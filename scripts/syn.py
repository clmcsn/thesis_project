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
choices=["Synthesize autoCsaMultipliers","Synthesize PE_2s","Synthesize PE_MS","Exit"]
c=util.get_choice(choices,msg=msg)
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
elif (c==2 or c==3):
    #this function is an ad hoc function, can't be used anywhere else
    def write_PE_file(in_file,out_file,mask):
        with open(out_file,"w") as fout_pointer, open(in_file,"r") as fin_pointer:
            flag=False
            for line in fin_pointer:
                if flag:
                    flag=False
                    line = "\tassign internal_weight = {"
                    for i in range (s.weight_width):
                        if mask[i]=="0":
                            line += "weight[{}],".format(s.weight_width-1-i)
                        else:
                            line += "1'b0,"
                    line = line[:-1] + "};\n"
                    print("Line created for mask: {} \n \t{}\n".format(mask,line))
                if "//internal weight assignment" in line:
                    flag=True            
                fout_pointer.write(line)

    with util.ssh_session(s.ecs_user,s.ecs_host):
        with util.ssh_session(s.asic_user,s.asic_host) as asic_server:
            print("WARNING! Manually check if settings in PE.sv are coherent with the synthesis process --> {} \n".format(choices[c]))
            print("Coping the project to server...\n")
            for i in range(pow(2,s.weight_width)):
                bin_str="{0:08b}".format(i) #NOT GENERAL LINE
                forced_bits=bin_str.count("1")
                if (forced_bits<=s.max_forcedBits and bin_str[0]!="1"): #avoid mask that cut MSB
                    print("Generating the ad hoc PE.sv file...")
                    write_PE_file(s.srcPath+"/PE/PE.sv","PE.sv",bin_str)
                    asic_server.copy_to(source="PE.sv",destination=s.synPart1Path+"src/")
                    print("Genereting synthesis script...\n")
                    #create script
                    with open("syn.tcl","w") as fout_pointer, open("template/syn.tcl","r") as fin_pointer:
                        for line in fin_pointer:
                            if s.signal_string in line:
                                fout_pointer.write("report_timing -significant_digits 10 > ./report_timing_{}_{}.txt\n".format(forced_bits,bin_str))
                                fout_pointer.write("report_area > ./report_area_{}_{}.txt\n".format(forced_bits,bin_str))
                            else:
                                fout_pointer.write(line)
                    #clean the synthesis directory
                    asic_server.clean("~/syn_part1/syn")
                    #copy script and setup file
                    asic_server.copy_to("../syn/.synopsys_dc.setup",destination=s.synPart1Path+"syn/")
                    asic_server.copy_to("syn.tcl",destination=s.synPart1Path+"syn/")
                    #run synthesis
                    print("Runnin synthesis. Blocked bits:{} String:{}".format(forced_bits,bin_str))
                    asic_server.run_commands("""cd {}syn
                        mkdir work
                        {setEnvironment}
                        dc_shell-xg-t -f syn.tcl""".format(s.synPart1Path,setEnvironment=s.cmdSetSynEnv))
                    if(c==2):
                        arch="2s"
                    else:
                        arch="MS"                    
                    try:
                        os.mkdir(s.reportsPath+"PE{}_{}".format(arch,forced_bits))
                    except FileExistsError:
                        pass
                    asic_server.copy_from(s.synPart1Path+"syn/report_timing_{}_{}.txt".format(forced_bits,bin_str),s.reportsPath+"PE{}_{}".format(arch,forced_bits))
                    asic_server.copy_from(s.synPart1Path+"syn/report_area_{}_{}.txt".format(forced_bits,bin_str),s.reportsPath+"PE{}_{}".format(arch,forced_bits))
                    os.remove("syn.tcl")
                    os.remove("PE.sv")
elif (c==len(choices)):
    exit()
