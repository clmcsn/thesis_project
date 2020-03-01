#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np

rep0=[1.5245093107]
rep1=  [1.4079493284,
        1.4490357637,
        1.4568009377,
        1.3862899542,
        1.4111844301,
        1.4402881861,
        1.3898062706,
        1.3984121084]
rep2=   [1.2927336693,
1.3122934103,
1.3645346165,
1.2835181952,
1.4038858414,
1.2852814198,
1.3075129986,
1.3276054859,
1.3444995880,
1.3012956381,
1.3188560009,
1.2653003931,
1.2780451775,
1.3168699741,
1.3304200172,
1.3271615505,
1.2655601501,
1.3517425060,
1.3564858437,
1.3422697783,
1.3080128431,
1.2835532427,
1.2829787731,
1.3432877064,
1.3383899927,
1.3049398661,
1.2821369171,
1.3067059517];
rep3=[1.2618880272,
1.1723426580,
1.1447259188,
1.1879949570,
1.1529779434,
1.1440597773,
1.2191139460,
1.2300573587,
1.1732416153,
1.2051392794,
1.2174036503,
1.2064874172,
1.1251606941,
1.1747404337,
1.1779205799,
1.1281460524,
1.2024741173,
1.1485004425,
1.1687657833,
1.2146838903,
1.1970971823,
1.2854750156,
1.1441504955,
1.1557174921,
1.1331979036,
1.1974797249,
1.2156658173,
1.1870651245,
1.1629266739,
1.2015870810,
1.2435489893,
1.1909646988,
1.2030286789,
1.1840695143,
1.1873487234,
1.1822831631,
1.1357588768,
1.1678466797,
1.2284952402,
1.1748809814,
1.1602358818,
1.1678178310,
1.1657364368,
1.1551762819,
1.2136631012,
1.2051247358,
1.1217659712,
1.1903290749,
1.1053220034,
1.1230026484,
1.1446814537,
1.2168642282,
1.1710567474,
1.2082825899,
1.1977980137,
1.1799374819]
rep4=[1.0661059618,
1.0113387108,
1.0824244022,
1.0559911728,
1.0619523525,
1.0074603558,
1.0236003399,
1.0735825300,
1.0031380653,
1.0548578501,
1.0560219288,
1.0332046747,
1.0974042416,
1.0478690863,
1.0668545961,
1.0745797157,
1.1073879004,
1.0538614988,
1.0268298388,
1.0873960257,
1.0398379564,
1.1101962328,
1.0511168242,
1.0683138371,
1.0907630920,
1.0163030624,
1.1140242815,
1.0469925404,
1.0475592613,
1.0716961622,
1.0714821815,
1.0105075836,
1.0331073999,
1.0806212425,
1.1105785370,
1.0725069046,
1.0369802713,
1.0223021507,
1.0287998915,
1.1001883745,
1.0904200077,
1.0843364000,
1.0742081404,
1.0298068523,
1.0411052704,
1.1020041704,
1.0835819244,
1.0339295864,
1.0396922827,
1.0987429619,
1.0742378235,
1.0010066032,
1.0324521065,
1.0183292627,
0.9885450006,
1.0448068380,
1.0618095398,
1.0783684254,
1.0403528214,
1.0682622194,
1.0214039087,
1.0171086788,
1.0167821646,
1.0409879684,
1.0665258169,
1.0464912653,
1.0535202026,
1.0283957720,
1.0364881754,
1.0691934824]
rep5=[0.4837226272,
0.4868635237,
0.4897815883,
0.5269697905,
0.4420892000,
0.4389637709,
0.4667730033,
0.4209021926,
0.4956143796,
0.4548842311,
0.5293430686,
0.4226276875,
0.4389637709,
0.4990205467,
0.4521970749,
0.4768933356,
0.4491647780,
0.4516187310,
0.4420892000,
0.4420892000,
0.4779322147,
0.5041443706,
0.4636095166,
0.4814901948,
0.4451452196,
0.3937374949,
0.5090066195,
0.4837226272,
0.4667730033,
0.4902852178,
0.4226276875,
0.4672479630,
0.5087575316,
0.4670666158,
0.4389637709,
0.4897815883,
0.4672479630,
0.4670666158,
0.4361186624,
0.4516187310,
0.4949012101,
0.4389637709,
0.4837226272,
0.4166094661,
0.4667730033,
0.4868635237,
0.4840801954,
0.3961443007,
0.4447627068,
0.4239288867,
0.4822761416,
0.4420892000,
0.3960045576,
0.5021769404,
0.4868635237,
0.4800700843]
m0=sum(rep0)/len(rep0)
m1=sum(rep1)/len(rep1)
m2=sum(rep2)/len(rep2)
m3=sum(rep3)/len(rep3)
m4=sum(rep4)/len(rep4)
m5=sum(rep5)/len(rep5)
X=[0,1,2,3,4,5];
Y=[m0,m1,m2,m3,m4,m5];
blue_dot, = plt.plot(X, Y, 'bo')
plt.ylabel('Average Arrival Time')
plt.xlabel('Number of fixed bits')
plt.axis([-1, 6, 0.4, 1.55])
plt.grid()
x_ticks = np.arange(0, 6 , 1)
plt.xticks(x_ticks)
plt.yticks(Y)
plt.show()