#!/usr/bin/env python3

import matplotlib.pyplot as plt
x=[1950,1985,2000,2015]
y=[10,100,1000,10000]
xp=[1960,1980,2006,2009,2009,2010,2012,2012,2013,2014]
yp=[15,290,29,690,330,1300,1000,95,9500,490]
yl=[100,1190,10000,11000]
plt.semilogy()
plt.grid()
plt.hlines(yl,1950,2016)
plt.plot(xp, yp, 'ro')
plt.show()