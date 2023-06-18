#!/usr/bin/python
import pylab as pl
import numpy as np
from pylab import *
from numpy import ma
import re

def ReadData(filename):
    time, cw = [], []
    p=re.compile('^#')
    f=open(filename)
    for line in f:
        line=line.rstrip('\n')
        a=line.split()
        if not p.match(line):
            time.append(float(a[0]))
            cw.append(float(a[1]))
    f.close()
    return time, cw

def plot_cw(real_cw, estimated_cw):
    time_real, real_cw = zip(*real_cw)
    time_e, estimated_cw= zip(*estimated_cw)
    pl.figure(figsize=(15,10), dpi=80, facecolor='white', edgecolor='k')
    pl.plot(time_real, real_cw,linewidth=2,color='red',label='cw')
    pl.plot(time_e, estimated_cw,linewidth=2,color='blue',label='estimated_cw')
    pl.legend()
    pl.xlabel('Time (s)')
    pl.ylabel('CW')
    pl.ylim(0,15)
    pl.xlim(0.15)
    pl.grid()
    pl.show()


def plot_throughput(th_1, th_2, lb1, lb2):
    time_real, real_cw = zip(*th_1)
    time_e, estimated_cw= zip(*th_2)
    pl.figure(figsize=(15,10), dpi=80, facecolor='white', edgecolor='k')
    pl.plot(time_real, real_cw,linewidth=2,color='red',label=lb1)
    pl.plot(time_e, estimated_cw,linewidth=2,color='blue',label=lb2)
    pl.legend()
    pl.xlabel('Time (s)')
    pl.ylabel('Segments/s')
    pl.ylim(0,15)
    pl.xlim(0.15)
    pl.grid()
    pl.show()


if __name__ == '__main__':
    time, cw = ReadData('./original/cw.tcporig')
    cw = [(t, c) for t, c in zip(time, cw)]
    plot(cw, cw)