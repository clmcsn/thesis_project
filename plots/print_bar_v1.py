#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.lines as mlines

import numpy as np

"""acc_y=[9232,9233,9241,9216,9232,8989,7701,
        5302,3449,2110,2048,1014,924,
        858,886,2048,2031,1517,1637,
        1688,1058,989,1000]"""
acc_m=[9233,9241,7701,1000]
mask_x=["00000001","00000011","00000111","00001111"]
acc_q=[9229,9224,9142,8973]
acc_m[:] = [x / 100 for x in acc_m]
acc_q[:] = [x / 100 for x in acc_q]
fig, ax = plt.subplots()
x = np.arange(len(mask_x))
width=0.18
rects1 = ax.bar(x - width/2, acc_m, 0.18, label='Equivalent best masked solution')
rects2 = ax.bar(x + width/2, acc_q, 0.18, label='Quantized solution')
"""mask_x=["00000001","00000010","00000011","00000100","00000101","00000110","00000111"
            ,"00001000","00001001","00001010","00001011","00001100","00001101",
            "00001110","00001111","00010000","00010001","00010010","00010011",
            "00010100","00010101","00010110","00010111"]"""

plt.ylabel('Accuracy (%)')
plt.xlabel('Solutions')
ax.legend(loc='lower left')
#plt.axis([720/100, 1150/100, 0.6, 1.55])
plt.grid()

plt.show()
