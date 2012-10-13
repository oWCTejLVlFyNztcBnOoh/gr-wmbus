#!/usr/bin/env python

"""
Make a histogram of normally distributed random numbers and plot the
analytic PDF over it
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

import struct

sbet_file = open('./traces/foo5.frame1.demod4.u8')
sbet_data = sbet_file.read()

x =  []
for s in sbet_data:
    (a) = struct.unpack("B", s)
    #x.append(a[0])
    x.append(a[0] & 0x03)
    x.append((a[0]/4) & 0x03)
    x.append((a[0]/4/4) & 0x03)

fig = plt.figure()
ax = fig.add_subplot(111)

# the histogram of the data
n, bins, patches = ax.hist(x, 64, normed=1, facecolor='green', alpha=0.75)

# hist uses np.histogram under the hood to create 'n' and 'bins'.
# np.histogram returns the bin edges, so there will be 50 probability
# density values in n, 51 bin edges in bins and 50 patches.  To get
# everything lined up, we'll compute the bin centers
#bincenters = 0.5*(bins[1:]+bins[:-1])
# add a 'best fit' line for the normal PDF
#y = mlab.normpdf( bincenters, mu, sigma)
#l = ax.plot(bincenters, y, 'r--', linewidth=1)

ax.set_xlabel('Smarts')
ax.set_ylabel('Probability')
#ax.set_title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
ax.set_xlim(-.5, 63.5)
#ax.set_ylim(0, 0.03)
ax.grid(True)

plt.show()
