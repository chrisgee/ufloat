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
"""Created on Tue Apr 10 22:51:09 2012

@author: Christoph Gohle, Sebastian Blatt

Converted to SI base units based on the srlab.units module by
Sebastian Blatt. Even though best care has been taken to ensure that
this file is error-free, you really must check important calculations
yourself and should not rely on a magic unit package! The numbers in
this file are based on the frink unit file
(https://futureboy.us/frinkdata/units.txt), which is a much more
extensive collection of units.

"""


#import ufloat.ufloat as u
# this is being run in uarray and in ufloat contexts (u will be the respective constructor)


# ----------------------------------------------------------- Basic unit system

# SI basic units

s = u(1, {'s': 1})      # time
kg = u(1, {'kg': 1})    # mass
m = u(1, {'m': 1})      # length
A = u(1, {'A': 1})      # current
K = u(1, {'K': 1})      # temperature
mol = u(1, {'mol': 1})  # substance
cd = u(1, {'cd': 1})    # luminous intensity

# nonstandard units

bit = u(1, {'bit': 1})  # information
dBm = u(1, {'dBm': 1})  # power

# ----------------------------------------------------------- Natural constants

pi = 3.141592653589793238

c = 299792458 * m * s**-1
speedoflight = c

h = 6.62606957e-34 * m**2 * s**-1 * kg
hplanck = h
hbar = h / (2 * pi)

kB = 1.3806488e-23 * m**2 * s**-2 * kg * K**-1
boltzmann = kB

electroncharge = 1.602176565e-19 * s * A
electronmass = 9.10938291e-31 * kg

protonmass = 1.672621777e-27 * kg
amu = 1.660538921e-27 * kg

avogadro = 6.02214129e+23 * mol**-1

mu0 = 4 * pi * 1e-7 * m * s**-2 * kg * A**-2
vacuumpermeability = mu0

epsilon0 = 1.0 / (mu0 * c**2)
vacuumpermittivity = epsilon0

a0 = 4 * pi * epsilon0 * hbar**2 / (electronmass * electroncharge**2)
bohrradius = a0

bohrmagneton = electroncharge * hbar / (2 * electronmass)

alpha = 1e-7 * electroncharge**2 * c / hbar

atomic_unit_polarizability = 4 * pi * epsilon0 * bohrradius**3

rydberg_constant = 0.5 * electronmass * c * alpha**2 / (hplanck)


# ------------------------------------------------------------------------ Time

ms = 1e-3 * s
us = 1e-6 * s
ns = 1e-9 * s
ps = 1e-12 * s
fs = 1e-15 * s

second = s
minute = 60 * s
hour = 60 * minute
day = 24 * hour
week = 7 * day

# ------------------------------------------------------------------- Frequency

Hz = 1 / s
hertz = Hz

mHz = 1e-3 * Hz
uHz = 1e-6 * Hz

kHz = 1e3 * Hz
MHz = 1e6 * Hz
GHz = 1e9 * Hz
THz = 1e12 * Hz

# ------------------------------------------------------------------------ Mass

kilogram = kg

g = 1e-3 * kg
gram = g

mg = 1e-6 * kg
ug = 1e-9 * kg

t = 1e3 * kg
ton = t
metricton = t

# imperial

lb = 45359237.0 / 100000000.0 * kg
pound = lb
uspound = lb

ounce = pound / 16
oz = ounce

dram = ounce / 15
dr = dram

uston = 2000 * pound
shortton = uston


# ---------------------------------------------------------------------- Length

meter = m
metre = m

cm = 1e-2 * m
mm = 1e-3 * m
um = 1e-6 * m
micron = um
nm = 1e-9 * m
km = 1e3 * m

# imperial
inch = 0.0254 * m
mil = 1e-3 * inch
thou = mil
ft = 12 * inch
foot = ft
yd = 3 * foot
yard = yd
mi = 1760 * yard
mile = mi

point = 13837e-6 * inch
computerpoint = inch / 72.0
postscriptpoint = computerpoint
pspoint = postscriptpoint
texscaledpoint = point / 65536.0
texsp = texscaledpoint

# ------------------------------------------------------------------------ Area

barn = 1e-28 * m**2

# ---------------------------------------------------------------------- Volume

l = 1e-3 * m**3
L = l
liter = l
litre = l

ccm = 1e-6 * m**3

# imperial

gal = 231 * inch**3
gallon = gal
qt = gal / 4.0
quart = qt
pt = quart / 2.0
pint = pt
floz = pint / 16.0
fluidounce = floz

cup = quart / 4.0
tbsp = cup / 16.0
tablespoon = tbsp
tsp = tbsp / 3.0
teaspoon = tsp

bbl = 42 * gal
barrel = bbl

# --------------------------------------------------------------------- Current

ampere = A

mA = 1e-3 * A
uA = 1e-6 * A
nA = 1e-9 * A

kA = 1e3 * A
MA = 1e6 * A

# ----------------------------------------------------------------- Temperature

kelvin = K

mK = 1e-3 * K
uK = 1e-6 * K
nK = 1e-9 * K
pK = 1e-12 * K

# ------------------------------------------------------------------- Substance

# ---------------------------------------------------------- Luminous intensity

candela = cd

# ----------------------------------------------------------------- Information

kbit = 1e3 * bit
Mbit = 1e6 * bit
Gbit = 1e9 * bit
Tbit = 1e12 * bit

kibit = 2**10 * bit
Mibit = 2**10 * kibit
Gibit = 2**10 * Mibit
Tibit = 2**10 * Gibit

byte = 8 * bit
kbyte = 1e3 * byte
Mbyte = 1e6 * byte
Gbyte = 1e9 * byte
Tbyte = 1e12 * byte

# ---------------------------------------------------------------------- Charge

C = s * A
coulomb = C

# --------------------------------------------------------------------- Voltage

V = m**2 * s**-3 * kg * A**-1
volt = V

mV = 1e-3 * V
uV = 1e-6 * V
nV = 1e-9 * V

kV = 1e3 * V
MV = 1e6 * V

# ------------------------------------------------------- Magnetic flux density

T = s**-2 * kg * A**-1
tesla = T

mT = 1e-3 * T
uT = 1e-6 * T
nT = 1e-9 * T
pT = 1e-12 * T

G = 1e-4 * T
gauss = G

mG = 1e-3 * G
uG = 1e-6 * G
nG = 1e-9 * G
pG = 1e-12 * G

kG = 1e3 * G
MG = 1e6 * G

# --------------------------------------------------------- Electric resistance

ohm = m**2 * s**-3 * kg * A**-2
Ω = ohm

mohm = 1e-3 * ohm
uohm = 1e-6 * ohm

kohm = 1e3 * ohm
Mohm = 1e6 * ohm
Gohm = 1e9 * ohm

# -------------------------------------------------------- Electric conductance

S = 1 / ohm
sievert = S
mho = S

# ----------------------------------------------------------------- Capacitance

F = m**-2 * s**4 * kg * -1 * A**2
farad = F

mF = 1e-3 * F
uF = 1e-6 * F
nF = 1e-9 * F
pF = 1e-12 * F

# ------------------------------------------------------------------ Inductance

H = m**2 * s**-2 * kg * A**-2
henry = H

mH = 1e-3 * H
uH = 1e-6 * H
nH = 1e-9 * H
pH = 1e-12 * H

# ---------------------------------------------------------------------- Energy

J = m**2 * s**-2 * kg
joule = J

calorie = 10467.0 / 2500.0 * J
cal = calorie

erg = 1e-7 * J

eV = electroncharge.value * J

Ry = rydberg_constant.value * hplanck.value / c.value * J
rydberg = Ry
hartree = 2 * Ry

# ----------------------------------------------------------------------- Power

W = J / s
watt = W

mW = W * 1e-3
uW = W * 1e-6
nW = W * 1e-9
kW = W * 1e3
MW = W * 1e6
GW = W * 1e9

# -------------------------------------------------------------------- Pressure

Pa = m**-1 * s**-2 * kg
pascal = Pa

mPa = 1e-3 * Pa
kPa = 1e3 * Pa

bar = 1e5 * Pa
mbar = 1e-3 * bar

Torr = 20265.0 / 152.0 * Pa
torr = Torr

mmHg = 133.322387415 * Pa

atm = 101325 * Pa

psi = 8896443230521.0 / 1290320000.0 * Pa
