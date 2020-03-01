#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib import rc, rcParams
rc('font',**{'family':'serif'})
rc('text', usetex=True)
rcParams.update({
    'font.family':'sans-serif',
    'font.sans-serif':['Liberation Sans'],
    })
import numpy as np
mask_x=["00000110","00000111"
            ,"00001000","00001001","00001010","00001011","00001100","00001101",
            "00001110","00001111","00010000","00010001","00010010","00010011",
            "00010100","00010101","00010110","00010111"]

base_line=[8989,7701,
        5302,3449,2110,2048,1014,924,
        858,886,2048,2031,1517,1637,
        1688,1058,989,1000]

range_correct=[9173,8526,
        9115,8448,2239,5277,1000,1000,
        1000,1000,1000,1000,1000,1000,
        1000,1000,1000,1000]

compensate_bias=[9179,9178,
        9199,9197,9121,9170,8601,8090,
        6447,4442,9009,9000,8819,8862,
        8716,8669,8260,6707]

mixed_approach=[9212,9207,
        9223,9194,9176,9205,8692,8171,
        7275,6435,9124,9121,9009,9067,
        8880,8748,8120,7010]

base_line[:] = [x / 100 for x in base_line]
range_correct[:] = [x / 100 for x in range_correct]
compensate_bias[:] = [x / 100 for x in compensate_bias]
mixed_approach[:] = [x / 100 for x in mixed_approach]
fig, ax = plt.subplots()
x = np.arange(len(mask_x))
width=0.21
rects1 = ax.barh(x - width*3/2, base_line, width, label='Baseline accuracy')
rects2 = ax.barh(x + width*3/2, mixed_approach, width, label='Mixed approach')
rects3 = ax.barh(x + width/2, range_correct, width, label='Range correction')
rects3 = ax.barh(x - width/2, compensate_bias, width, label='Bias compensation')
plt.xlabel('Accuracy (\%)')
x_ticks = np.arange(0, 100 , 10)
plt.xticks(x_ticks)
plt.ylabel('Solutions')
ax.legend(loc='lower left')
#plt.axis([720/100, 1150/100, 0.6, 1.55])
plt.grid()

plt.show()