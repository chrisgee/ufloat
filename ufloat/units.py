# -*- coding: utf-8 -*-
#    ufloat - fast python floats with physical units
#    Copyright (C) 2015  Christoph Gohle <christoph.gohle@mpq.mpg.de>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
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
cm = 0.01*m
mm = 0.001*m
um = 0.001*mm
nm = 0.001*um
km = 1000*m
Hz = 1/s
kHz = 1000*Hz
MHz = 1000*kHz
GHz = 1000*MHz
THz = 1000*GHz
mHz = 0.001*Hz
uHz = 0.001*mHz
#electric
C = u(1, {'C':1})
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
dBm = u(1., {'dBm':1})
#mass
kg = u(1., {'kg':1})
g = 1e-3*kg
mg = 1e-6*kg
ug = 1e-9*kg
t = 1e3*kg
#temperature
K = u(1., {'K':1})
mK = 1e-3*K
uK = 1e-6*K
nK = 1e-9*K
#magnetic
G = u(1,{'G':1})
mG = 1e-3*G
uG = 1e-3*mG
nG = 1e-3*uG
pG = 1e-3*nG
kG = 1e3 * G
MG = 1e3 * kG
T = 1e4*G
mT = 1e-3*T
uT = 1e-3*mT
#energy
J = kg*m**2/s**2
#power
W = u(1., {"W":1})
mW = W*1e-3
uW = W*1e-6
nW = W*1e-9
kW = W*1e3
MW = W*1e6
GW = W*1e9

