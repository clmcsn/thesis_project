#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
#res=[[767. ,1086.,913. ,784. ,868. ,791. ,782. ,773. ,799. ,795. ,768. ,808. ,811. ,807. ,814. ,848. ,908. ,813. ,791. ,895. ,855. ,825. ,955. ,839.],
#        [1.22119291  ,0.901878341,0.90687674,1.12680839,0.95187198,1.06943001,1.17117401,1.18621645,1.03110011,1.05823826,1.21003461,1.01394161,0.99041104,1.0217596 ,0.98224257,0.96539413,0.90966288,0.98651041,1.06943001,0.91465785,0.95187542,0.97639664,0.901883511,0.96636928]]
res=[[1.36900000e+03,
747.          ,
1.28600000e+03,
783.          ,
1.06600000e+03,
774.          ,
869.          ,
1.23200000e+03,
8.74000000e+02,
765.          ,
1.27400000e+03,
9.86000000e+02,
1.19000000e+03,
787.          ,
762.          ,
1.17800000e+03,
1.11800000e+03,
751.          ,
9.1000000e+02 ,
848.          ,
9.83000000e+02,
1.00200000e+03,
9.1800000e+02 ,
1.17300000e+03,
1.02300000e+03,
808.          ,
1.2040000e+03 ,
1.15900000e+03,
8.98000000e+02,
754.          ,
807.          ,
9.02000000e+02,
799.          ,
9.30000000e+02,
1.0460000e+03 ,
827.          ,
8.87000000e+02,
800.          ,
815.          ,
1.12200000e+03,
8.92000000e+02,
9.72000000e+02,
822.          ,
1.15000000e+03,
9.5200000e+02 ,
758.          ,
9.56000000e+02,
797.          ,
1.03600000e+03,
750.          ],
[ 5.98005373e-01,	
1.26837301   ,
5.99715612e-01,
1.08817429    ,
6.81450067e-01,	
1.12997765	  ,  
0.91732685    ,
6.05766652e-01,	
8.68639854e-01,	
1.15547088   ,
6.05489998e-01,	
7.08550621e-01,	
6.08354228e-01,	
 1.0437697  ,
1.18732567	  , 
6.40413659e-01,	
6.81173413e-01,	
1.24744203	  , 
 8.0232935e-01,	
0.92234376	  , 
7.50205943e-01,	
7.06588424e-01,	
 7.6869935e-01,	
6.50763622e-01,	
6.92547637e-01,	
0.96268465	  , 
 6.0642085e-01,	
6.73688788e-01,	
8.34736676e-01,	
1.21194954	  , 
0.99662796	  , 
8.10100818e-01,	
1.02915483	  , 
7.68243305e-01,	
 6.9058544e-01,	
0.92964179	  , 
8.62560461e-01,	
0.99978904	  , 
0.95478991	  , 
6.81091291e-01,	
8.46670208e-01,	
7.50288937e-01,	
0.93745566	  , 
6.75722952e-01,	
 7.6087323e-01,	
1.20895774	  , 
7.60417184e-01,	
 1.0418377	  , 
6.92295679e-01,	
1.26793862	   
]]
quant_timings=[1.5245093107,1.4111844301,1.2780451775,1.1602358818,1.0806212425]
quant_top1= [771,775,776,858,1027]
quant_top1[:] = [x / 100 for x in quant_top1]
res[0][:] = [x / 100 for x in res[0][:]]
red_dot, = plt.plot(res[0][:], res[1][:], 'ro')
blue_dot, = plt.plot(quant_top1, quant_timings, 'bo')
plt.hlines(1.5245093107, 720/100, 1400/100, colors='r')
plt.vlines(760/100, 0.55, 1.55, colors='k')
plt.vlines(771/100, 0.55, 1.55, colors='b')
plt.ylabel('Critical Path Delay (ns)')
plt.xlabel('Top1 Error (%)')
plt.axis([720/100, 1400/100, 0.55, 1.55])
x_ticks = np.arange(7.2, 14 , 0.5)
plt.xticks(x_ticks)
plt.grid()
#legend
blue_line = mlines.Line2D([], [], color='blue')
red_line = mlines.Line2D([], [], color='red')
black_line = mlines.Line2D([], [], color='black')
plt.legend([red_dot, blue_dot,blue_line,red_line,black_line], ["Masked Solutions", "Base Quantization Solutions", "Best Quantized Accuracy","8-bit Architecture Delay","FloatingPoint32 Accuracy"])
plt.show()