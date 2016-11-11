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
Created on Thu Feb  7 02:05:56 2013

@author: Christoph Gohle
"""

import numpy
from numpy import arange
import ufloat.funits
import ufloat.aunits
from time import time

class scalar(object):
    s = 5.
    m = 10.
    
def tests(u):
    print('#######################')
    print('# %s'%u)
    print('#######################')
    t = time()
    a = [i*u.s for i in arange(100000.)]
    print('scalar left multiply: \t\t%f'%(time()-t))
    t = time()
    a = [u.s*i for i in arange(100000.)]
    print('scalar right multiply: \t\t%f'%(time()-t))
    t = time()
    a = [u.s*numpy.arange(1000) for i in arange(10000)]
    print('array right multiply: \t\t%f'%(time()-t))
    t = time()
    a = [numpy.arange(1000)*u.s for i in arange(10000)]
    print('array left multiply: \t\t%f'%(time()-t))
    t = time()
    a = [5*u.m*u.s for i in arange(10000)]
    print('unit multiply: \t\t%f'%(time()-t))
    t = time()
    a = [5*u.m+i*u.m for i in arange(10000)]
    print('unit add: \t\t%f'%(time()-t))
    


#tests(units)
#tests(quantities)
tests(ufloat.funits)
tests(ufloat.aunits)
tests(scalar)
#tests(unum.units)
#tests(pinttest)
#tests(sympytest)
