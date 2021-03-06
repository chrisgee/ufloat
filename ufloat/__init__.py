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


from numpy import *
__version__ = '0.2.1'
from .ufloat import ufloat
from .uarray import UnitArray
#from . import funits
#from . import aunits

def unit_from_string(st):
    """the inverse of format_unit.

    It's not exacly the inverse since the dict does not prescribe a order of
    string representation, i.e. format_unit(. However it should be gueranteed that
    unit_from_string(format_unit(unit))==unit"""
        
    nomdenom = st.split('/')
    nom = nomdenom[0].strip()
    if len(nomdenom)==2:
        denom = nomdenom[1]
    elif len(nomdenom)>2:
        raise ValueError('can\'t parse string %s'%st)
    else:
        denom = ''
    #print denom, nom
    nitems = nom.split(' ')
    ditems = denom.split(' ')
    #print nitems, ditems
    udict = {}
    for it in nitems:
        if it.strip() == '1' or it.strip() == '':
            break
        l = it.split('**')
        if len(l)>1:
            udict[l[0]]=float(l[1])
        else:
            udict[l[0]]=1
    for it in ditems:
        if it.strip() == '':
            break
        l = it.split('**')
        if len(l)>1:
            udict[l[0]]=-float(l[1])
        else:
            udict[l[0]]=-1
    return udict

def ufloat_from_string(st):
    st = st.strip()
    uleft = st.rfind('[')
    uright = st.rfind(']')
    if uleft>0 and uright+1==len(st):
        try:
            punit = st[uleft+1:uright]
            unit = unit_from_string(punit)
            value = eval(st[:uleft].strip())
        except:
            raise
        return ufloat(1, unit)*value
    else:
        raise ValueError('could not find a unit in %s.'%st)
        
    
