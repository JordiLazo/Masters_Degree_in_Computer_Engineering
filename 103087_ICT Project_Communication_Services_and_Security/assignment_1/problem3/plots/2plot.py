#!/usr/bin/python

import pylab as pl
import numpy as np
from pylab import *
from numpy import ma
import re

def ReadData(filename):
    global time,cw
    p=re.compile('^#')
    f=open(filename)
    for line in f:
        line=line.rstrip('\n')
        a=line.split()
        if not p.match(line):
            time.append(float(a[0]))
            cw.append(float(a[1]))
    f.close()

def Plot():
    pl.figure(figsize=(15,10), dpi=80, facecolor='white', edgecolor='k')
    pl.plot(time,cw,linewidth=2,color='red',label='cw')
    pl.legend()
    pl.xlabel('Time (s)')
    pl.ylabel('Seconds')
    pl.ylim(0,15)
    pl.xlim(0.15)
    pl.grid()
    pl.show()

time=[]
cw=[]

ReadData('../original/cw.tcporig')
Plot()