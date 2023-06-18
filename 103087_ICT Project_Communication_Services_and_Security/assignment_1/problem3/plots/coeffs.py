#!/bin/python
# By Csar Fdez , 2014
import pylab as pl
import numpy as np
from pylab import *
from numpy import ma
import math

def coeffa(n):
    return (1/(math.pi*n))*(math.sin(3*math.pi*n/4)- math.sin(math.pi*n/4)+ math.sin(7*math.pi*n/4)- math.sin(6*math.pi*n/4))

def coeffb(n):
    return (1/(math.pi*n))*(-math.cos(3*math.pi*n/4)+ math.cos(math.pi*n/4)- math.cos(7*math.pi*n/4)+ math.cos(6*math.pi*n/4))

def Signal(t,T):
    a=t-int(t)
    if a<1./8: 
        return 0
    elif a< 3./8:
        return 1
    elif a< 6./8:
        return 0
    elif a< 7./8:
        return 1
    else:
        return 0

def SignalC(t,n):
    r=a[0]/2
    for i in range(1,n):
        r+=a[i]*math.cos(i*2*math.pi*t)+b[i]*math.sin(i*2*math.pi*t)
    return r


def PlotSignal(n,f):
    sig=[]
    sigc=[]
    for i in range(PointsPerPeriod*NumberOfPeriodsToPlot):
        sig.append(Signal(1.*i/PointsPerPeriod,Period))
        sigc.append(SignalC(1.*i/PointsPerPeriod,n))
    

    pl.figure(figsize=(10,8), dpi=80, facecolor='white', edgecolor='k')
    pl.plot(sig,linewidth=4,label='Senyal')
    l='Senyal aprox. amb '+str(n)+' coeffs.'
    pl.plot(sigc,linewidth=2,color='red',label=l)
    pl.xlabel('Temps')
    pl.grid()
    pl.ylabel('')
    pl.ylim(-0.2,1.2)
    labels=['0']
    for i in range(1,NumberOfPeriodsToPlot+1):
        labels.append(str(i)+'T')
    pl.xticks(range(0,PointsPerPeriod*NumberOfPeriodsToPlot+1,PointsPerPeriod),labels)
    pl.legend()
    #pl.savefig(f)
    pl.show()

def PlotCoeffs():
    w=0.2
    inda=np.arange(len(a))
    indb=np.arange(len(b))
    pl.figure(figsize=(10,8), dpi=80, facecolor='white', edgecolor='k')
    pl.bar(inda,a,width=w,color='red',label='a')
    pl.bar(indb+w,b,width=w,color='blue',label='b')
    pl.legend()
    pl.grid()
    pl.xlabel('n')
    pl.ylabel('$a_n$,$b_n$')
    pl.show()

a=[0.75]
b=[0]
for i in range(1,300):
    a.append(coeffa(i))
    b.append(coeffb(i))

PointsPerPeriod = 100
Period = 2
NumberOfPeriodsToPlot = 2

PlotCoeffs()
PlotSignal(10,'')
PlotSignal(200,'')
exit(0)
for n in 3,5,10,40,200:
    filename='signal-'+str(n)+'.png'
    PlotSignal(n,filename)
