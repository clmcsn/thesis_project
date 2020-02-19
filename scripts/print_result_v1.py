#!/usr/bin/env python3

import matplotlib.pyplot as plt

res=[[767. ,1086.,913. ,784. ,868. ,791. ,782. ,773. ,799. ,795. ,768. ,808. ,811. ,807. ,814. ,848. ,908. ,813. ,791. ,895. ,855. ,825. ,955. ,839.],
        [1.22119291  ,0.901878341,0.90687674,1.12680839,0.95187198,1.06943001,1.17117401,1.18621645,1.03110011,1.05823826,1.21003461,1.01394161,0.99041104,1.0217596 ,0.98224257,0.96539413,0.90966288,0.98651041,1.06943001,0.91465785,0.95187542,0.97639664,0.901883511,0.96636928]]
quant_timings=[1.5245093107,1.4111844301,1.2780451775,1.1602358818,1.0806212425]
quant_top1= [771,775,776,858,1027]
plt.plot(res[0][:], res[1][:], 'ro')
plt.plot(quant_top1, quant_timings, 'bo')
plt.hlines(1.5245093107, 750, 1100, colors='k')
plt.vlines(760, 0.8, 1.55, colors='k')
plt.vlines(771, 0.8, 1.55, colors='b')
plt.ylabel('critical path delay (ns)')
plt.xlabel('top1 error')
plt.axis([750, 1100, 0.8, 1.55])
plt.show()