#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import pylab as pl
import numpy as np

qrtt=[]
qt_srtt=[]
qRTTest=[]
qRTTestfloat=[]
qRTT2estfloat=[]

t_srtt=0
RTTestfloat=0.0
RTTrange=128
random.seed(0)
for i in range(250):
    rtt=int(random.uniform(0,RTTrange))
    RTTestfloat=7./8*RTTestfloat+1./8*rtt
    qrtt.append(rtt)
    qRTTestfloat.append(RTTestfloat)

    delta = rtt - t_srtt>>3
    t_srtt+=delta

    qt_srtt.append(t_srtt)
#    qRTTest.append(t_srtt>>3)


for i in range(len(qrtt)):
    print(qrtt[i],'&',qt_srtt[i], ' & {:.1f}'.format(qRTTestfloat[i])   ,' \\\\')

pl.rcParams.update({'font.size': 18})
f,ax = pl.subplots(1,1,figsize=(10,6), dpi=80, facecolor='white', edgecolor='k',sharex=True)    
ax.plot(np.array(qrtt),linewidth=1,label='RTT measured')
ax.plot(np.array(qRTTestfloat),linewidth=3,label='RTTestimated (float)')
ax.plot(np.array(qt_srtt),linewidth=4,label='t_srtt')


pl.grid()
pl.legend()
pl.show()
pl.savefig('rtt_tmp.png')
