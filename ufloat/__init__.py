# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 17:23:07 2012

@author: Christoph Gohle

ufloat package contains quantities with units for scalars and numpy arrays

The basic usage is as follows:

Examples
--------
To create a number with unit
>>> s = ufloat(1, {'s',1})
>>> m = ufloat(1, {'m',1})

numbers with units can be multiplied
>>> 5*s
5.0 [s]
>>> 9.81*m/s**2
9.81 [m/s**2]

and added if they have the same unit
>>> 5*s + 10*s
15.0*s

>>> 5*s + 12*m
ValueError: Can't add two quantities with differnt units 5.0 [s] and 12 [m].
"""
from ufloat import ufloat
from uarray import UnitArray
import funits
import aunits

