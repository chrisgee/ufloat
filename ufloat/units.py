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

s = u(1.0, {'s': 1})      # time
kg = u(1.0, {'kg': 1})    # mass
m = u(1.0, {'m': 1})      # length
A = u(1.0, {'A': 1})      # current
K = u(1.0, {'K': 1})      # temperature
mol = u(1.0, {'mol': 1})  # substance
cd = u(1.0, {'cd': 1})    # luminous intensity

# nonstandard units

bit = u(1.0, {'bit': 1})  # information
dBm = u(1.0, {'dBm': 1})  # power

# ----------------------------------------------------------- Natural constants

pi = 3.141592653589793238

c = 299792458.0 * m * s**-1
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

mu0 = 4.0 * pi * 1e-7 * m * s**-2 * kg * A**-2
vacuumpermeability = mu0

epsilon0 = 1.0 / (mu0 * c**2)
vacuumpermittivity = epsilon0

a0 = 4.0 * pi * epsilon0 * hbar**2 / (electronmass * electroncharge**2)
bohrradius = a0

bohrmagneton = electroncharge * hbar / (2 * electronmass)

alpha = 1e-7 * electroncharge**2 * c / hbar

atomic_unit_polarizability = 4.0 * pi * epsilon0 * bohrradius**3

rydberg_constant = 0.5 * electronmass * c * alpha**2 / (hplanck)


# ----------------------------------------------------------------- SI prefixes

yocto = 1e-24
zepto = 1e-21
atto = 1e-18
femto = 1e-15
pico = 1e-12
nano = 1e-9
micro = 1e-6
milli = 1e-3
centi = 1e-2
deci = 1e-1
deka = 1e1
hecto = 1e2
kilo = 1e3
mega = 1e6
giga = 1e9
tera = 1e12
peta = 1e15
exa = 1e18
zetta = 1e21
yotta = 1e24


# ------------------------------------------------------------------------ Time

ms = milli * s
us = micro * s
ns = nano * s
ps = pico * s
fs = femto * s

second = s
minute = 60 * s
hour = 60 * minute
day = 24 * hour
week = 7 * day

# ------------------------------------------------------------------- Frequency

Hz = 1 / s
hertz = Hz

mHz = milli * Hz
uHz = micro * Hz
μHz = uHz

kHz = kilo * Hz
MHz = mega * Hz
GHz = giga * Hz
THz = tera * Hz

# ------------------------------------------------------------------------ Mass

kilogram = kg

g = 1e-3 * kg
gram = g

mg = 1e-6 * kg
ug = 1e-9 * kg
μg = ug

t = 1e3 * kg
ton = t
metricton = t

# imperial

lb = 45359237.0 / 100000000.0 * kg
pound = lb
uspound = lb

ounce = pound / 16
oz = ounce

dram = ounce / 16
dr = dram

uston = 2000 * pound
shortton = uston


# ---------------------------------------------------------------------- Length

meter = m
metre = m

cm = centi * m
mm = milli * m
um = micro * m
μm = um
micron = um
nm = nano * m
km = kilo * m

# imperial
inch = 0.0254 * m
mil = milli * inch
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

l = milli * m**3
L = l
liter = l
litre = l

ccm = micro * m**3

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

mA = milli * A
uA = micro * A
μA = uA
nA = nano * A

kA = kilo * A
MA = mega * A

# ----------------------------------------------------------------- Temperature

kelvin = K

mK = milli * K
uK = micro * K
μK = uK
nK = nano * K
pK = pico * K

# ------------------------------------------------------------------- Substance

# ---------------------------------------------------------- Luminous intensity

candela = cd

# ----------------------------------------------------------------- Information

kbit = kilo * bit
Mbit = mega * bit
Gbit = giga * bit
Tbit = tera * bit

kibit = 2**10 * bit
Mibit = 2**10 * kibit
Gibit = 2**10 * Mibit
Tibit = 2**10 * Gibit

byte = 8 * bit
kbyte = kilo * byte
Mbyte = mega * byte
Gbyte = giga * byte
Tbyte = tera * byte

# ---------------------------------------------------------------------- Charge

C = s * A
coulomb = C

# --------------------------------------------------------------------- Voltage

V = m**2 * s**-3 * kg * A**-1
volt = V

mV = milli * V
uV = micro * V
μV = uV
nV = nano * V

kV = kilo * V
MV = mega * V

# ------------------------------------------------------- Magnetic flux density

T = s**-2 * kg * A**-1
tesla = T

mT = milli * T
uT = micro * T
μT = uT
nT = nano * T
pT = pico * T

G = 1e-4 * T
gauss = G

mG = milli * G
uG = micro * G
μG = uG
nG = nano * G
pG = pico * G

kG = kilo * G
MG = mega * G

# --------------------------------------------------------- Electric resistance

ohm = m**2 * s**-3 * kg * A**-2
Ω = ohm

mohm = milli * ohm
uohm = micro * ohm

kohm = kilo * ohm
Mohm = mega * ohm
Gohm = giga * ohm

# -------------------------------------------------------- Electric conductance

S = 1 / ohm
sievert = S
mho = S

# ----------------------------------------------------------------- Capacitance

F = m**-2 * s**4 * kg * -1 * A**2
farad = F

mF = milli * F
uF = micro * F
μF = uF
nF = nano * F
pF = pico * F

# ------------------------------------------------------------------ Inductance

H = m**2 * s**-2 * kg * A**-2
henry = H

mH = milli * H
uH = micro * H
μH = uH
nH = nano * H
pH = pico * H

# ---------------------------------------------------------------------- Energy

J = m**2 * s**-2 * kg
joule = J

calorie = 10467.0 / 2500.0 * J
cal = calorie

erg = 1e-7 * J

eV = electroncharge.value * J
electronvolt = eV

Ry = rydberg_constant.value * hplanck.value / c.value * J
rydberg = Ry
hartree = 2 * Ry

# ----------------------------------------------------------------------- Power

W = J / s
watt = W

mW = milli * W
uW = micro * W
μW = uW
nW = nano * W
kW = kilo * W
MW = mega * W
GW = giga * W

# -------------------------------------------------------------------- Pressure

Pa = m**-1 * s**-2 * kg
pascal = Pa

mPa = milli * Pa
kPa = 1e3 * Pa

bar = 1e5 * Pa
mbar = milli * bar

Torr = 20265.0 / 152.0 * Pa
torr = Torr

mmHg = 133.322387415 * Pa

atm = 101325 * Pa

psi = 8896443230521.0 / 1290320000.0 * Pa
