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
Created on Sat Apr  7 17:08:22 2012

@author: Christoph Gohle

A extension type implementing floatingpoint numbers with units.

The Idea is based on the unum package. However the units are much simpler
(they can't be converted) and the whole type is written in cython for speed.

In fact this implementation is only about a factor three slower than usual
python floats when it comes to multiplication etc.
"""
from __future__ import division

from libc.stdlib cimport malloc, free, realloc

from .uarray import UnitArray, mulunit, divunit, powunit
from numpy import ndarray
from . import uarray


cdef extern from "stdio.h":
   int printf(char*,...)

#dictionary storing all used unit names (so that references stay unique)
cdef dict names = {}
#helper array for multiplication (gloabl, so that it does not need to get realloced every time)
cdef int *sused = <int *>malloc(10*sizeof(int))
cdef int ssize = 10

#just for debugging
#def __nameDict():
#    return names

###########################
# cython implementation of a 'unit' class
##########################
#dimension (with exponent)
cdef struct dim:
    char *name
    float exponent

#unit is a list of dimensions of length ndims
cdef struct unit:
    dim *dims
    int ndims

cdef unit* unew(length):
    cdef unit *self = <unit*>malloc(sizeof(unit))
    if self == NULL:
        return NULL

    self.dims = <dim *>malloc(length*sizeof(dim))
    if self.dims == NULL:
        free(self)
        return NULL
    self.ndims = length
    for i in xrange(length):
        self.dims[i].name = NULL
        self.dims[i].exponent = 0
    return self

cdef unit* uinitd(unit* self, dict u) except NULL:
    """initialize a unit block self with a copy of u"""
    if self == NULL:
        raise ValueError('self is NULL!')

    if not self.ndims == len(u):
        raise ValueError('the length of the unit struct needs to be the same as the dict')
    i=0
    for k, v in u.items():
        if isinstance(k, str):
            name = k.encode('UTF-8') #we encode everything into utf-8üs¨ß        
        else:
            name = k
        if not name in names:
            names[name]=name
        else:
            #make sure we use the string that was stored in names
            name = names[name]
        self.dims[i].name = name
        self.dims[i].exponent = v
        i+=1

    return self

cdef unit* uinitu(unit* self, unit *u) except NULL:
    """initialize a self struct with a copy of u"""
    if self == NULL or u == NULL:
        raise ValueError('one of the units is NULL!')
    if not self.ndims == u.ndims:
        raise ValueError('The size of self does not match the other size')
    self.ndims = u.ndims
    for i in xrange(self.ndims):
        self.dims[i].name = u.dims[i].name
        self.dims[i].exponent = u.dims[i].exponent
    return self

cdef ufree(unit *self):
    """free the unit memory block"""
    if not self == NULL:
        if not self.dims == NULL:
            free(self.dims)
        free(self)

cdef object uformat(unit *self):
    """create a string representation of self"""
    if self == NULL:
        return ''
    nom = ''
    denom = ''
    cdef char *u
    cdef float exp
    for i in xrange(self.ndims):
        u = self.dims[i].name
        exp = self.dims[i].exponent
        if exp > 0:
            if exp > 1:
                nom += u'{}**{} '.format(u.decode('UTF-8'),abs(exp))
            else:
                nom += u'{} '.format(u.decode('UTF-8'))
        else:
            if exp < -1:
                denom += u'{}**{} '.format(u.decode('UTF-8'),abs(exp))
            else:
                denom += u'{} '.format(u.decode('UTF-8'))
    fill = u''
    if not denom == u'':
        fill = u'/'
        if nom == u'':
            nom = u'1'
    return nom.strip()+fill+denom.strip()

cdef unit* upow(unit* self, float exp) except NULL:
    """take the unit self to the power exp"""
    cdef unit* res
    if self == NULL:
        raise ValueError('unit must not be NULL')

    res = unew(self.ndims)
    for i in xrange(self.ndims):
        res.dims[i].name = self.dims[i].name
        res.dims[i].exponent = self.dims[i].exponent*exp

    return res

cdef unit* umul(unit* self, unit* other, float sign = 1) except NULL:
    """mulitiply two units self and other with
    other taken to the power sign first"""
    if self == NULL or other == NULL:
        raise ValueError('units are None while they should be unit')

    cdef unit* u = unew(self.ndims+other.ndims)
    global sused, ssize
    #fix size of helper
    if ssize < self.ndims:
        sused = <int *>realloc(sused, self.ndims*sizeof(int))
        ssize = self.ndims
    if sused == NULL:
        ssize = 0
        raise MemoryError('out of memory in allocating a helper array')
    for i in xrange(self.ndims):
        sused[i]=0

    cdef char* a
    cdef float exp
    cdef int newi = 0
    for i in xrange(other.ndims):
        a = other.dims[i].name
        exp = sign*other.dims[i].exponent
        for j in xrange(self.ndims):
            if self.dims[j].name==a:
                exp += self.dims[j].exponent
                sused[j] = 1
                break
        if not exp == 0:
            u.dims[newi].name = a
            u.dims[newi].exponent = exp
            newi += 1

    for i in xrange(self.ndims):
        if sused[i] == 0:
            u.dims[newi].name = self.dims[i].name
            u.dims[newi].exponent = self.dims[i].exponent
            newi += 1

    u.dims = <dim *>realloc(u.dims, newi*sizeof(dim))
    if newi is not 0 and u.dims == NULL:
        ufree(u)
        raise MemoryError('failed to realloc dimensions memory')
    u.ndims = newi

    return u

cdef int ucmp(unit* self, unit* other):
    """compare two units and return True if equal, false otherwise"""
    if self == NULL or other == NULL:
        return False
    for i in xrange(self.ndims):
        same = False
        for j in xrange(other.ndims):
            if self.dims[i].name==other.dims[j].name and self.dims[i].exponent == other.dims[j].exponent:
                    same = True
                    break
        if same == False:
            break
    return same

cdef dict utodict(unit* self):
    """create a python dictionary to represent the unit"""
    cdef dict res = {}
    if self == NULL:
        return res
    for i in xrange(self.ndims):
        res[self.dims[i].name.decode('UTF-8')]=self.dims[i].exponent
    return res





cdef object newval(double value, unit* u, bint copy = False):
    """helper for creating new unit values"""
    cdef ufloat res
    if u.ndims>0: # and not value == 0:
        res = ufloat(value)
        if not copy:
            res._unit = u
        else:
            res._unit = unew(u.ndims)
            uinitu(res._unit, u)
        return res
    else:
        if not copy:
            ufree(u)
        else:
            pass
        return value
        
#########################################
# ufloat: a float class with units
#########################################
cdef class ufloat:
    """a floating point class with units"""
#    cdef int _unit
    cdef double _value
    cdef unit* _unit
    prefixmap = {'f':-15,'p':-12,'n':-9,'u':-6,'m':-3, 'k':3, 'M':6, 'G':9, 'T':12, 'P':15}
    __array_priority__ = 10
    def __cinit__(self, value, u = None):
        """Create a new floatingpoint number with units

        Parameters
        ----------
        value : the value of the quantity
            this can either be a ufloat (in which case the ufloat will be copied) or
            a number that can be cast to float

        u : unit of the quantity
            A dictionary of the form {'unit_name':exponent,...} specifying the unit
            of the quantity. Defaults to None (no unit). If value is of type ufloat,
            this parameter is ignored
        """
        cdef ufloat v
        if u and isinstance(u, dict):
            self._unit = unew(len(u))
            uinitd(self._unit, u)
            #printf("%p",self._unit)
            self._value = value
        elif isinstance(value, ufloat):
            v = value
            self._value = v._value
            self._unit = unew(v._ndims)
            uinitu(self._unit, (<ufloat>u)._unit)
        else:
            self._value = value
            self._unit = NULL
            #raise ValueError('Either needs to be a ufloat or a unit has to be specified)


        
    def __dealloc__(self):
        ufree(self._unit)

    def __str__(self):
        return '%s [%s]'%(self._value, uformat(self._unit))

    def __repr__(self):
        if uarray.STRREP:
            return self.__str__()
        return '%s(%s, %s)'%(
            self.__class__.__name__, repr(self._value), repr(utodict(self._unit)))

    def __mul__(self, other):
        cdef ufloat s
#        print 'mul', self, other
        if isinstance(other, ufloat) and isinstance(self, ufloat):
                return newval((<ufloat>self)._value*(<ufloat>other)._value, umul((<ufloat>self)._unit,(<ufloat>other)._unit))
        elif isinstance(other, ufloat):
            if isinstance(self, ndarray):
                ounit = getattr(self,'unitDict',{})
                ovalue = getattr(self, 'value', self)
#                print 'self', ounit, ovalue
                return UnitArray(<ufloat>other.value*ovalue,mulunit(other.unitDict, ounit), checkunit = False)
            s = other
            o = self
        elif isinstance(self, ufloat):
            if isinstance(other, ndarray):
                ounit = getattr(other,'unitDict',{})
                ovalue = getattr(other, 'value', other)
#                print 'other', ounit, ovalue
                return UnitArray(<ufloat>self.value*ovalue,mulunit(self.unitDict, ounit), checkunit = False)
            s = self
            o = other
        else:
            raise Exception("why did I get here?")
        #print "self: %s, other: %s"%(s,o)
        return newval(s._value*o, s._unit, True)


    #ATTENTION __truediv__ and __div__ have the same code (to support both python2 and python3)
    #an update on one REQUIRES the same update on the other
    #FIXME: is there some construct to get rid of this redundant piece of code?
    def __truediv__(self, other):
        cdef ufloat s
        cdef int exp
#        print self, other
        if isinstance(other, ufloat) and isinstance(self, ufloat):
                return newval((<ufloat>self)._value/(<ufloat>other)._value,
                              umul((<ufloat>self)._unit,(<ufloat>other)._unit,-1))
        elif isinstance(other, ufloat):
            if isinstance(self, ndarray):
                #print 'self.nd, other float'
                ounit = getattr(self,'unitDict',{})
                ovalue = getattr(self, 'value', self)
                return UnitArray(ovalue/<ufloat>other.value,divunit(ounit, other.unitDict), checkunit = False)
            s = other
            o = self
            exp = -1
            return newval(o/s._value, upow(s._unit,-1))
        elif isinstance(self, ufloat):
            if isinstance(other, ndarray):
                ounit = getattr(other,'unitDict',{})
                ovalue = getattr(other, 'value', other)
                return UnitArray(<ufloat>self.value/ovalue,divunit(self.unitDict, ounit), checkunit = False)
            s = self
            o = other
            exp = 1
        else:
            raise Exception("why did I get here?")
#        print "self: %s, other: %s"%(s,o)
        return newval(s._value/o, upow(s._unit,exp))

    def __div__(self, other):
        cdef ufloat s
        cdef int exp
#        print self, other
        if isinstance(other, ufloat) and isinstance(self, ufloat):
                return newval((<ufloat>self)._value/(<ufloat>other)._value,
                              umul((<ufloat>self)._unit,(<ufloat>other)._unit,-1))
        elif isinstance(other, ufloat):
            if isinstance(self, ndarray):
                #print 'self.nd, other float'
                ounit = getattr(self,'unitDict',{})
                ovalue = getattr(self, 'value', self)
                return UnitArray(ovalue/<ufloat>other.value,divunit(ounit, other.unitDict), checkunit = False)
            s = other
            o = self
            exp = -1
            return newval(o/s._value, upow(s._unit,-1))
        elif isinstance(self, ufloat):
            if isinstance(other, ndarray):
                ounit = getattr(other,'unitDict',{})
                ovalue = getattr(other, 'value', other)
                return UnitArray(<ufloat>self.value/ovalue,divunit(self.unitDict, ounit), checkunit = False)
            s = self
            o = other
            exp = 1
        else:
            raise Exception("why did I get here?")
#        print "self: %s, other: %s"%(s,o)
        return newval(s._value/o, upow(s._unit,exp))
        
    def __pow__(self, other, modulo):
        #FIXME: modulo not supported (what does it?)
        cdef ufloat s
        if isinstance(other, ufloat) or isinstance(other, ndarray):
            raise ValueError('Can\'t expontiate using exponent with units or array')
        elif isinstance(self, ufloat):
            s = self
        else:
            raise Exception("why did I get here?")
        #print "self: %s, other: %s"%(s,o)
        return newval(s._value**other, upow(s._unit,other))

    def __add__(self, other):
        if isinstance(other, ufloat) and isinstance(self, ufloat) and ucmp((<ufloat>self)._unit, (<ufloat>other)._unit):
            return newval((<ufloat>self)._value + (<ufloat>other)._value, (<ufloat>self)._unit, True)
        elif isinstance(other, ndarray) or isinstance(self, ndarray):
            udict = getattr(self, 'unitDict', {})
            if udict == getattr(other, 'unitDict', {}):
                svalue = getattr(self, 'value', self)
                ovalue = getattr(other, 'value', other)
                return UnitArray(svalue+ovalue, udict)

        raise ValueError('Can\'t add two quantities with differnt units %s and %s.'%(self, other))

    def __sub__(self, other):
        if isinstance(other, ufloat) and isinstance(self, ufloat) and ucmp((<ufloat>self)._unit, (<ufloat>other)._unit):
            return newval((<ufloat>self)._value - (<ufloat>other)._value, (<ufloat>self)._unit, True)
        elif isinstance(other, ndarray) or isinstance(self, ndarray):
            udict = getattr(self, 'unitDict', {})
            if udict == getattr(other, 'unitDict', {}):
                svalue = getattr(self, 'value', self)
                ovalue = getattr(other, 'value', other)
                return UnitArray(svalue-ovalue, udict)
        raise ValueError('Can\'t subtract two quantities with differnt units %s and %s.'%(self, other))

    def __neg__(self):
        if isinstance(self, ufloat):
            return newval(-(<ufloat>self)._value, (<ufloat>self)._unit, True)
        else:
            raise Exception('how did I get here?')

    def __richcmp__(self, other, op):
        if isinstance(self, ufloat) and isinstance(other, ufloat):
            c = ucmp((<ufloat>self)._unit, (<ufloat>other)._unit)
            v = (<ufloat>self)._value
            o = (<ufloat>other)._value
        elif isinstance(self, ufloat):
            c = ucmp((<ufloat>self)._unit, (<ufloat>getattr(other, 'unit', ufloat(1,{})))._unit)
            v = float((<ufloat>self)._value)
            o = getattr(other,'value',other)
        elif isinstance(other, ufloat):
            c = ucmp((<ufloat>other)._unit, (<ufloat>getattr(self, 'unit', ufloat(1,{})))._unit)
            o = float((<ufloat>other)._value)
            v = getattr(self, 'value', self)
        else:
            raise ValueError('Why here? %s, %s, %s'%(self,other,op))
        if c==1:        
            if op == 0:
                result = (v<o)
                #print '#le', result
            elif op == 2:
                result = (v==o)
                #print '#eq', result
            elif op == 4:
                result = (v>o)
                #print '#gr', result
            elif op == 1:
                result = (v<=o)
                #print '#leq', result
            elif op == 3:
                result = (v!=o)
                #print '#neq', result
            elif op == 5:
                result = (v>=o)
                #print '#geq', result
            else:
                raise ValueError('unknown op %d.'%op)
        else:
            if op == 2:
                #print '#things with different units are not equal'
                result = False
            elif op == 3:
                #print '#dito'
                result = True
            else:
                raise ValueError('can\'t compare apples to peaches')
        #print(result)
        return result
        
    property value:
        def __get__(self):
            return self._value

    def asNumber(self, other = None):
        if isinstance(other, ufloat):
            if ucmp(self._unit, (<ufloat>other)._unit):
                return self._value/((<ufloat>other)._value)
            else:
                raise ValueError('Quantity %s can\'t be converted to %s'%(self, other.unit))
        elif isinstance(other, UnitArray):
            if self.unitDict == other.unitDict:
                return self._value/(other.value)
            else:
                raise ValueError('Quantity %s can\'t be converted to %s'%(self, other.unit))
        return self._value

    def rescale(self, other):
        return self.asNumber(other)

    property unit:
        def __get__(self):
            cdef ufloat u = ufloat(1)
            u._unit = unew(self._unit.ndims)
            uinitu(u._unit, self._unit)
            return u
            #(1.0, utodict(self._unit))

        def __set__(self, nunit):
            cdef unit* u = NULL
            if isinstance(nunit, dict):
                u = unew(len(nunit))
                uinitd(u, nunit)
            if isinstance(nunit, ufloat):
                u = upow((<ufloat>nunit)._unit, 1)
            if not ucmp(self._unit, u):
                ufree(u)
                raise ValueError('cant change to a different unit')
            else:
                #nothing to be done
                pass

    property unitDict:
        def __get__(self):
            """A dictionary representation of the quantitie's unit."""
            return utodict(self._unit)

    property symbol:
        def __get__(self):
            """a string representation of the dimension"""
            return uformat(self._unit)

    #Pickling support
    def __reduce__(self):
        return (ufloat,
                (self._value, self.unitDict))

