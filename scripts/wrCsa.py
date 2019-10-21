#!/usr/bin/env python3

import sys
sys.path.append('../')
from common.hw_arith_lib import *

csa=multiplier(8)
csa.setWeightValBits("11111011")
csa.genCsaStructure()
csa.printCsaStructure()
