#!/usr/bin/env python3

import sys
import os
import subproccess

COMMAND="scp"
ECS_SERVER="gmsarda@asic"
ASIC_SERVER="gsarda@ssh.ecs.tuwien.ac.at"

subprocess.call(["vsim", "-c", "-do", "../common/sim/divisorNOGUI.do"])

if len(sys.argv)!=3:
    print("Error: Please insert two valid paths")
else:
    if (~(os.path.isfile(argv[1] or os.path.isdir(argv[2]))):
        print("Error: Make sure that second argument is a valid path!")
    else:
        subprocess.call([])
