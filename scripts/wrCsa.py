#!/usr/bin/env python3

import sys
sys.path.append('../')
from common.hw_lib import *

csa=multiplier(8)
csa.setWeightValBits("00011100")
csa.genCsaStructure()
csa.genCsaMultiplier()
