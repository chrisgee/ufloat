# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 22:51:09 2012

@author: Christoph Gohle
"""

#import ufloat.ufloat as u
# this is being run in uarray and in ufloat contexts (u will be the respective constructor)

s = u(1,{'s':1})
ms = 0.001*s
us = 0.001*ms
ns = 0.001*us
m = u(1,{'m':1})
mm = 0.001*m
um = 0.001*mm
nm = 0.001*um
km = 1000*m
Hz = 1/s
kHz = 1000*Hz
MHz = 1000*kHz
GHz = 1000*MHz
V = u(1,{'V':1})
mV = 0.001*V
uV = 0.001*mV
kV = 1000*V
MV = 1000*kV
A = u(1,{'A':1})
mA = 0.001*A
uA = 0.001*mA
kA = 1000*A
MA = 1000*kA
#add more units here!