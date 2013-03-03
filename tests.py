# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 16:08:07 2013

@author: Christoph Gohle
"""

from ufloat import funits as f
from ufloat import aunits as a
from ufloat.ufloat import ufloat
from ufloat.uarray import UnitArray 
from numpy import arange, array, all
from matplotlib.cbook import flatten, is_scalar_or_string

data = [1.,5.,20., arange(10)+1]
units = [1., a.m, a.s, f.m, f.s, f.s**-1, f.m**-1]

def is_array(thing):
    if hasattr(thing, 'dtype'):
        return True
    else:
        return is_scalar_or_string(thing)
        
l = list(flatten([[d*u for u in units] for d in data], scalarp=is_array))
v = list(flatten([[d for u in units] for d in data], scalarp=is_array))
u = list(flatten([[u for u in units] for d in data], scalarp=is_array))
print l
print v
print u

def basicmul():
    assert(5*f.s == ufloat(5,{'s':1}))
    assert(f.s*f.m == ufloat(1,{'s':1,'m':1}))
    assert(f.s*f.s == ufloat(1,{'s':2}))
    assert(a.s*a.m == UnitArray(1,{'s':1,'m':1}))
    

def basicdiv():
    assert(5/f.s == ufloat(5,{'s':-1}))
    assert(f.s/f.m == ufloat(1,{'s':1,'m':-1}))
    assert(f.s/f.s == 1)
    assert(a.s/a.m == UnitArray(1,{'s':1,'m':-1}))

def mul():
    print 'mul'
    li = zip(l,v,u)
    for left, lv, lu in li:
        for right, rv, ru in li:
            result = (lv*rv)*(lu*ru)            
            print left, '*', right, '=', result 
            assert(all(left*right == result))
        
def div():
    print 'div'
    li = zip(l,v,u)
    for left, lv, lu in li:
        for right, rv, ru in li:
            result = (lv/rv)*(lu/ru)         
            print left, '/', right, '=', result 
            assert(all(left/right == result))

def add():
    print 'add'
    li = zip(l,v,u)
    for left, lv, lu in li:
        for right, rv, ru in li:
            try:
                dummy = lu+ru
            except:
                continue
            result = (lv+rv)*(ru)
            print left, '+', right, '=', result 
            assert(all(left+right == result))

def sub():
    print 'sub'
    li = zip(l,v,u)
    for left, lv, lu in li:
        for right, rv, ru in li:
            try:
                dummy = lu-ru
            except:
                continue
            result = (lv-rv)*(ru)
            print left, '-', right, '=', result 
            assert(all(left-right == result))

def pow():
    print 'pow'
    li = zip(l,v,u)
    for left, lv, lu in li:
        for right in v:
            try:
                if not min(right)==max(right):
                #nonuniform powers are not allowed
                    continue
            except:
                pass
            result = (lv**right)*lu**right
            print left, '**', right, '=', result 
            assert(all(left**right == result))

basicmul()
basicdiv()
mul()
div()
add()
sub()
pow()
