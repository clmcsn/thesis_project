#server paths
synPart1Path="~/syn_part1/"

#local paths
csa_outPath="./csaTemp.txt"
tbsPath="../tbs/"
templatePath="../src/template/"
componentsPath="../src/components/"
reportsPath="../reports/"
srcPath="../src/"
reportPath="../reports/"

#synopsys and synthesis
cmdSetSynEnv=". /eda/synopsys/2016-17/scripts/SYN_2016.12_RHELx86.sh"

#hardware settings
weight_width=8
psum_width=32
max_forcedBits=5
num_sample=1000000 #exaustive random checking
signal_string="//AUTO_PRINT"

#ssh settings
ecs_user="gsarda"
ecs_host="ssh.ecs.tuwien.ac.at"
ecs_name="ecs_tuwien_gateway1"
asic_user="gmsarda"
asic_host="asic"
asic_name="asic_tuwien_gateway1"

#analysis settings
timingReportFindString="arrival time"
timingReport="report_timing"
