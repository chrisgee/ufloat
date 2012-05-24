# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 17:08:22 2012

@author: Christoph Gohle

A extension type implementing floatingpoint numbers with units.

The Idea is based on the unum package. However the units are much simpler
(they can't be converted) and the whole type is written in cython for speed.

In fact this implementation is only about a factor three slower than usual
python floats when it comes to multiplication etc.
"""
from libc.stdlib cimport malloc, free, realloc

from uarray import UnitArray, mulunit, divunit, powunit
from numpy import ndarray

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
    for k, v in u.iteritems():
        if not k in names:
            names[k]=k
        else:
            #make sure we use the string that was stored in names
            k = names[k]
        self.dims[i].name = k
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
                nom += '%s**%s '%(u,abs(exp))
            else:
                nom += '%s '%u
        else:
            if exp < -1:
                denom += '%s**%s '%(u,abs(exp))
            else:
                denom += '%s '%u
    fill = ''
    if not denom == '':
        fill = '/'
        if nom == '':
            nom = '1'

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
            if self.dims[i].name==a:
                exp += self.dims[i].exponent
                sused[i] = 1
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
        res[self.dims[i].name]=self.dims[i].exponent
    return res





cdef object newval(double value, unit* u, copy = False):
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

#    def __init__(self, value, u = None):
#        if u and isinstance(u, dict):
#            print('init')
#            uinitd(self._unit, u)
#        elif isinstance(value, ufloat):
#            uinitu(self._unit, (<ufloat>u)._unit)

    def __dealloc__(self):
        ufree(self._unit)

    def __str__(self):
        return '%s [%s]'%(self._value, uformat(self._unit))

    def __repr__(self):
        return '%s(%s, %s)'%(
            self.__class__.__name__, repr(self._value), repr(utodict(self._unit)))

    def __mul__(self, other):
        cdef ufloat s
        if isinstance(other, ufloat) and isinstance(self, ufloat):
                return newval((<ufloat>self)._value*(<ufloat>other)._value, umul((<ufloat>self)._unit,(<ufloat>other)._unit))
        elif isinstance(other, ufloat):
            s = other
            o = self
        elif isinstance(self, ufloat):
            if isinstance(other, ndarray):
                ounit = getattr(other,'unitDict',{})
                ovalue = getattr(other, 'value', other)
                return UnitArray(<ufloat>self.value*ovalue,mulunit(self.unitDict, ounit), checkunit = False)
            s = self
            o = other
        else:
            raise Exception("why did I get here?")
        #print "self: %s, other: %s"%(s,o)
        return newval(s._value*o, s._unit, True)

    def __div__(self, other):
        cdef ufloat s
        cdef int exp
#        print self, other
        if isinstance(other, ufloat) and isinstance(self, ufloat):
                return newval((<ufloat>self)._value/(<ufloat>other)._value,
                              umul((<ufloat>self)._unit,(<ufloat>other)._unit,-1))
        elif isinstance(other, ufloat):
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
        elif isinstance(self, ufloat) and isinstance(other, ndarray):
            if self.unitDict == getattr(other, 'unitDict', {}):
                ovalue = getattr(other, 'value', other)
                return UnitArray((<ufloat>self)._value+ovalue, (<ufloat>self).unitDict)

        raise ValueError('Can\'t add two quantities with differnt units %s and %s.'%(self, other))

    def __sub__(self, other):
        if isinstance(other, ufloat) and isinstance(self, ufloat) and ucmp((<ufloat>self)._unit, (<ufloat>other)._unit):
            return newval((<ufloat>self)._value - (<ufloat>other)._value, (<ufloat>self)._unit, True)
        elif isinstance(self, ufloat) and isinstance(other, ndarray):
            if self.unitDict == getattr(other, 'unitDict', {}):
                return UnitArray((<ufloat>self)._value-other.value, (<ufloat>self).unitDict)
        raise ValueError('Can\'t subtract two quantities with differnt units %s and %s.'%(self, other))

    def __neg__(self):
        if isinstance(self, ufloat):
            return newval(-(<ufloat>self)._value, (<ufloat>self)._unit, True)
        else:
            raise Exception('how did I get here?')

    def __cmp__(self, other):
        if isinstance(self, ufloat) and isinstance(other, ufloat):
            if ucmp((<ufloat>self)._unit, (<ufloat>other)._unit):
                return cmp((<ufloat>self)._value,(<ufloat>other)._value)

        elif isinstance(self, ufloat):
            v = (<ufloat>self)._value
            o = other
        elif isinstance(other, ufloat):
            o = (<ufloat>other)._value
            v = self
        return cmp(v,o)

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

