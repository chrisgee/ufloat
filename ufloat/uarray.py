# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 17:23:07 2012

@author: Christoph Gohle

This is a simplified version of 'quantities', a numpy array with units.
All the units conversion stuff has been removed including all the logic
around it to speed up things. It integrates with a scalar float class with
units 'ufloat' that is a cython extension type.
"""
import numpy as np
from functools import wraps
import sys
STRREP = False

def mulunit(unit1, unit2):
    u = unit1.copy()
    for a, exp in unit2.iteritems():
        if a in u:
            u[a] += exp
            if u[a]==0:
                u.pop(a)
        else:
            u[a] = exp
    return u

def divunit(unit1, unit2):
    u = unit1.copy()
    for a, exp in unit2.iteritems():
        if a in u:
            u[a] -= exp
            if u[a]==0:
                u.pop(a)
        else:
            u[a] = -exp
    return u
    
def simplify_unit(unit):
    u = unit.copy()
    for un in unit:
        if u[un]==0:
            u.pop(un)
    
    return u

def format_unit(unit):
    nom = ''
    denom = ''
    for u, exp in unit.iteritems():
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


def powunit(unit, exp):
    u = {}
    for unit, e in unit.iteritems():
        u[unit]=e*exp
    return u


def checkunit(unit1, unit2):
    if not unit1 == unit2:
        raise ValueError('the two units [%s] and [%s] are not the same.'%(format_unit(unit1), format_unit(unit2)))

class with_doc:

    """
    This decorator combines the docstrings of the provided and decorated objects
    to produce the final docstring for the decorated object.
    """

    def __init__(self, method, use_header=True):
        self.method = method
        if use_header:
            self.header = \
    """

    Notes
    -----
    """
        else:
            self.header = ''

    def __call__(self, new_method):
        new_doc = new_method.__doc__
        original_doc = self.method.__doc__
        header = self.header

        if original_doc and new_doc:
            new_method.__doc__ = """
    %s
    %s
    %s
        """ % (original_doc, header, new_doc)

        elif original_doc:
            new_method.__doc__ = original_doc

        return new_method

def scale_other_units(f):
    from .ufloat import ufloat
    @wraps(f)
    def g(self, other, *args):
        if isinstance(other, ufloat):
            ounit = other.unitDict
            other = np.asanyarray(other.value).view(type=UnitArray)
            #print ounit, other
            other._unit = ounit
        elif isinstance(other, UnitArray):
            ounit = other._unit
        else:
            other = np.asanyarray(other).view(type=UnitArray)
            ounit = {}
        checkunit(ounit, self._unit)
        return f(self, other, *args)
    return g

def protected_multiplication(f):
    @wraps(f)
    def g(self, other, *args):
        if getattr(other, '_unit', None):
            try:
#                print(self)
#                print(type(self))
#                print(self.base)
#                print(type(self.base))
                assert not isinstance(self.base, UnitArray)
            except AssertionError:
                raise ValueError('can not modify units of a view of a UnitArray')
        return f(self, other, *args)
    return g

def check_uniform(f):
    @wraps(f)
    def g(self, other, *args):
        if getattr(other, '_unit', None):
            raise ValueError("exponent must be dimensionless")
        other = np.asarray(other)
        try:
            assert other.min() == other.max()
        except AssertionError:
            raise ValueError('Quantities must be raised to a uniform power')
        return f(self, other, *args)
    return g

def protected_power(f):
    @wraps(f)
    def g(self, other, *args):
        if other != 1:
            try:
                assert not isinstance(self.base, UnitArray)
            except AssertionError:
                raise ValueError('can not modify units of a view of a UnitArray')
        return f(self, other, *args)
    return g

def wrap_comparison(f):
    from .ufloat import ufloat
    @wraps(f)
    def g(self, other):
        if isinstance(other, UnitArray):
            other = other.rescale(self.unit)
        elif isinstance(other, ufloat):
            other = other.rescale(self.unit)

        #print 'comparison', self, other
        return f(self, other)
    return g


class UnitArray(np.ndarray):


    # TODO: what is an appropriate value?
    __array_priority__ = 5

    def __new__(cls, data, units={}, checkunit = True, unitdef = False, dtype=None, copy=True, reconstruct=False):
        from .ufloat import ufloat
        #print 'new', cls, data, units
        if isinstance(data, cls):
            if units and checkunit:
                checkunit(data._unit, units)
            #print 'new unit array', units
            return np.array(data, dtype=dtype, copy=copy, subok=True)
        elif not unitdef:
            #print 'new from array', units
            try:
                l = len(data)
            except:
                l = 0
            if l <= 1:
                if hasattr(data,'_unit'):
                    if data._unit == {}:
                        return data.value
                    return ufloat(data.value, data._unit)
                elif units and not units == {}:
                    return ufloat(data, units)
                else:
                    return data

        if units and not units == {} or reconstruct:        
            ret = np.array(data, dtype=dtype, copy=copy).view(cls)
            ret._unit = units
        else:
            ret = np.array(data, dtype=dtype, copy=copy)
        return ret


    @property
    def value(self):
        return self.view(type=np.ndarray)

    @property
    def unit(self):
        from .ufloat import ufloat
        return ufloat(1, self._unit)

    @property
    def unitDict(self):
        return self._unit

    def asNumber(self, other = None):
        if other:
            checkunit(self.unitDict, other.unitDict)
            return self.value/other.value
        return self.value

    def rescale(self, other):
        return self.asNumber(other)

    @property
    def symbol(self):
        return format_unit(self._unit)

    @with_doc(np.ndarray.astype)
    def astype(self, dtype=None):
        from .ufloat import ufloat
        '''Scalars are returned as scalar ufloat numbers.'''
        ret = super(UnitArray, self).astype(dtype)
        # scalar quantities get converted to plain numbers, so we fix it
        # might be related to numpy ticket # 826
        #print 'astype', self, dtype
        if not isinstance(ret, type(self)):
            return ufloat(ret, self._unit)
            if self.__array_priority__ >= UnitArray.__array_priority__:
                ret = type(self)(ret, self._unit)
            else:
                ret = UnitArray(ret, self._unit)

        return ret

    def __array_finalize__(self, obj):
        #print 'finalize', self, obj
        self._unit = getattr(obj, '_unit', {})

    def __array_prepare__(self, obj, context=None):
        #print 'prepare', self, obj, context
        if context is not None:
            uf, objs, huh = context
            if uf.__name__.startswith('is'):
                return obj
            #print self, obj, res, uf, objs
            try:
                _unit = p_dict[uf](*objs)
            except KeyError:
                raise ValueError('ufunc %r not supported by units' % uf)
        else:
            _unit = {}
            
        #print 'prepare unit', _unit
        if not _unit == {}:
            res = obj.view(UnitArray)
            res._unit = _unit
        else:
            res = obj
        #print 'prepare result', res
        return res

    def __array_wrap__(self, obj, context=None):
        #print 'wrap', self, obj, context
        if not isinstance(obj, UnitArray):
            # backwards compatibility with numpy-1.3
            obj = self.__array_prepare__(obj, context)
        return obj

    @with_doc(np.ndarray.__add__)
    @scale_other_units
    def __add__(self, other):
        return super(UnitArray, self).__add__(other)

    @with_doc(np.ndarray.__radd__)
    @scale_other_units
    def __radd__(self, other):
        return np.add(other, self)
        return super(UnitArray, self).__radd__(other)

    @with_doc(np.ndarray.__iadd__)
    @scale_other_units
    def __iadd__(self, other):
        return super(UnitArray, self).__iadd__(other)

    @with_doc(np.ndarray.__sub__)
    @scale_other_units
    def __sub__(self, other):
        return super(UnitArray, self).__sub__(other)

    @with_doc(np.ndarray.__rsub__)
    @scale_other_units
    def __rsub__(self, other):
        return np.subtract(other, self)
        return super(UnitArray, self).__rsub__(other)

    @with_doc(np.ndarray.__isub__)
    @scale_other_units
    def __isub__(self, other):
        return super(UnitArray, self).__isub__(other)

    @with_doc(np.ndarray.__mod__)
    @scale_other_units
    def __mod__(self, other):
        return super(UnitArray, self).__mod__(other)

    @with_doc(np.ndarray.__imod__)
    @scale_other_units
    def __imod__(self, other):
        return super(UnitArray, self).__imod__(other)

    @with_doc(np.ndarray.__imul__)
    @protected_multiplication
    def __imul__(self, other):
        return super(UnitArray, self).__imul__(other)

    @with_doc(np.ndarray.__rmul__)
    def __rmul__(self, other):
        return np.multiply(other, self)
        return super(UnitArray, self).__rmul__(other)

    @with_doc(np.ndarray.__itruediv__)
    @protected_multiplication
    def __itruediv__(self, other):
        return super(UnitArray, self).__itruediv__(other)

    @with_doc(np.ndarray.__rtruediv__)
    def __rtruediv__(self, other):
        return np.true_divide(other, self)
        return super(UnitArray, self).__rtruediv__(other)

    if sys.version_info[0] < 3:
        @with_doc(np.ndarray.__idiv__)
        @protected_multiplication
        def __idiv__(self, other):
            return super(UnitArray, self).__itruediv__(other)

        @with_doc(np.ndarray.__rdiv__)
        def __rdiv__(self, other):
            return np.divide(other, self)

    @with_doc(np.ndarray.__pow__)
    @check_uniform
    def __pow__(self, other):
        return super(UnitArray, self).__pow__(other)

    @with_doc(np.ndarray.__ipow__)
    @check_uniform
    @protected_power
    def __ipow__(self, other):
        return super(UnitArray, self).__ipow__(other)

    def __round__(self, decimals=0):
        return np.around(self, decimals)


    @with_doc(np.ndarray.__repr__)
    def __repr__(self):
        if STRREP:
            return self.__str__()
        return '%s(%s, %s)'%(
            self.__class__.__name__, repr(self.value), repr(self._unit)
        )

#    @with_doc(np.ndarray.__repr__)
#    def __repr__(self):
#        return '%s * %s'%(
#            repr(self.value), format_unit(self._unit)
#        )

    @with_doc(np.ndarray.__str__)
    def __str__(self):
        dims = format_unit(getattr(self,'_unit',{}))
        return '%s [%s]'%(repr(self.value), dims)

    @with_doc(np.ndarray.__getitem__)
    def __getitem__(self, key):
        if isinstance(key, int):
            # This might be resolved by issue # 826
            return UnitArray(self.value[key], self._unit)
        else:
            return super(UnitArray, self).__getitem__(key)

    @with_doc(np.ndarray.__setitem__)
    def __setitem__(self, key, value):
        if isinstance(value, UnitArray):
            if self._unit != value._unit:
                value = value.rescale(self._unit)
        self.value[key] = value

    @with_doc(np.ndarray.__lt__)
    @wrap_comparison
    def __lt__(self, other):
        return self.value < getattr(other, 'value', other)

    @with_doc(np.ndarray.__le__)
    @wrap_comparison
    def __le__(self, other):
        return self.value <= getattr(other, 'value', other)

    @with_doc(np.ndarray.__eq__)
    def __eq__(self, other):
        try:
            other = other.rescale(self.unit)
        except (ValueError, AttributeError):
            return np.zeros(self.shape, '?')
        return self.value == other

    @with_doc(np.ndarray.__ne__)
    def __ne__(self, other):
        #print '#ne', self, other        
        try:
            other = other.rescale(self.unit)
            return self.value != other
        except (ValueError, AttributeError):
            #either wrong unit or no unit
            return np.ones(self.shape, '?')
        return self.value != other
            
    @with_doc(np.ndarray.__ge__)
    @wrap_comparison
    def __ge__(self, other):
        return self.value >= other

    @with_doc(np.ndarray.__gt__)
    @wrap_comparison
    def __gt__(self, other):
        return self.value > other

    #I don't think this implementation is particularly efficient,
    #perhaps there is something better
    @with_doc(np.ndarray.tolist)
    def tolist(self):
        #first get a dummy array from the ndarray method
        work_list = self.value.tolist()
        #now go through and replace all numbers with the appropriate UnitArray
        self._tolist(work_list)
        return work_list

    def _tolist(self, work_list):
        for i in range(len(work_list)):
            #if it's a list then iterate through that list
            if isinstance(work_list[i], list):
                self._tolist(work_list[i])
            else:
                #if it's a number then replace it
                # with the appropriate quantity
                work_list[i] = UnitArray(work_list[i], self._unit)

    #need to implement other Array conversion methods:
    # item, itemset, tofile, dump, byteswap

    @with_doc(np.ndarray.sum)
    def sum(self, axis=None, dtype=None, out=None):
        return UnitArray(
            self.value.sum(axis, dtype, out),
            self._unit,
            copy=False
        )

    @with_doc(np.ndarray.fill)
    def fill(self, value):
        self.value.fill(value)
        try:
            self._unit = value._unit
        except AttributeError:
            pass

    @with_doc(np.ndarray.put)
    def put(self, indicies, values, mode='raise'):
        """
        performs the equivalent of ndarray.put() but enforces units
        values - must be an UnitArray with the same units as self
        """
        if isinstance(values, UnitArray):
            if values._unit == self._unit:
                self.value.put(indicies, values, mode)
            else:
                raise ValueError("values must have the same units as self")
        else:
            raise TypeError("values must be a UnitArray")

    # choose does not function correctly, and it is not clear
    # how it would function, so for now it will not be implemented

    @with_doc(np.ndarray.argsort)
    def argsort(self, axis=-1, kind='quick', order=None):
        return self.value.argsort(axis, kind, order)

    @with_doc(np.ndarray.searchsorted)
    def searchsorted(self,values, side='left'):
        if not isinstance (values, UnitArray):
            values = UnitArray(values, copy=False)

        if values._unit != self._unit:
            raise ValueError("values does not have the same units as self")

        return self.value.searchsorted(values.value, side)

    @with_doc(np.ndarray.nonzero)
    def nonzero(self):
        return self.value.nonzero()

    @with_doc(np.ndarray.max)
    def max(self, axis=None, out=None):
        return UnitArray(
            self.value.max(),
            self._unit,
            copy=False
        )

    @with_doc(np.ndarray.min)
    def min(self, axis=None, out=None):
        return UnitArray(
            self.value.min(),
            self._unit,
            copy=False
        )

    @with_doc(np.ndarray.argmin)
    def argmin(self,axis=None, out=None):
        return self.value.argmin()

    @with_doc(np.ndarray.ptp)
    def ptp(self, axis=None, out=None):
        return UnitArray(
            self.value.ptp(),
            self._unit,
            copy=False
        )

    @with_doc(np.ndarray.clip)
    def clip(self, min=None, max=None, out=None):
        if min is None and max is None:
            raise ValueError("at least one of min or max must be set")
        else:
            if min is None: min = UnitArray(-np.Inf, self._unit)
            if max is None: max = UnitArray(np.Inf, self._unit)

        if self._unit and not \
                (isinstance(min, UnitArray) and isinstance(max, UnitArray)):
            raise ValueError(
                "both min and max must be Quantities with compatible units"
            )

        clipped = self.value.clip(
            min.rescale(self._unit).value,
            max.rescale(self._unit).value,
            out
        )
        return UnitArray(clipped, self._unit, copy=False)

    @with_doc(np.ndarray.round)
    def round(self, decimals=0, out=None):
        return UnitArray(
            self.value.round(decimals, out),
            self._unit,
            copy=False
        )

    @with_doc(np.ndarray.trace)
    def trace(self, offset=0, axis1=0, axis2=1, dtype=None, out=None):
        return UnitArray(
            self.value.trace(offset, axis1, axis2, dtype, out),
            self._unit,
            copy=False
        )

    @with_doc(np.ndarray.mean)
    def mean(self, axis=None, dtype=None, out=None):
        return UnitArray(
            self.value.mean(axis, dtype, out),
            self._unit,
            copy=False)

    @with_doc(np.ndarray.var)
    def var(self, axis=None, dtype=None, out=None):
        return UnitArray(
            self.value.var(axis, dtype, out),
            self._unit**2,
            copy=False
        )

    @with_doc(np.ndarray.std)
    def std(self, axis=None, dtype=None, out=None):
        return UnitArray(
            self.value.std(axis, dtype, out),
            self._unit,
            copy=False
        )

    @with_doc(np.ndarray.prod)
    def prod(self, axis=None, dtype=None, out=None):
        if axis == None:
            power = self.size
        else:
            power = self.shape[axis]

        return UnitArray(
            self.value.prod(axis, dtype, out),
            self._unit**power,
            copy=False
        )

    @with_doc(np.ndarray.cumprod)
    def cumprod(self, axis=None, dtype=None, out=None):
        if self._unit:
            # different array elements would have different _unit
            raise ValueError(
                "UnitArray must be dimensionless, try using simplified"
            )
        else:
            return super(UnitArray, self).cumprod(axis, dtype, out)

    # list of unsupported functions: [choose]

    def __getstate__(self):
        """
        Return the internal state of the quantity, for pickling
        purposes.

        """
        cf = 'CF'[self.flags.fnc]
        state = (1,
                 self.shape,
                 self.dtype,
                 self.flags.fnc,
                 self.tostring(cf),
                 self._unit,
                 )
        return state

    def __setstate__(self, state):
        (ver, shp, typ, isf, raw, units) = state
        np.ndarray.__setstate__(self, (shp, typ, isf, raw))
        self._unit = units

    def __reduce__(self):
        """
        Return a tuple for pickling a UnitArray.
        """
        return (_reconstruct_quantity,
                (self.__class__, np.ndarray, (0, ), 'b', ),
                self.__getstate__())

def _reconstruct_quantity(subtype, baseclass, baseshape, basetype,):
    """Internal function that builds a new MaskedArray from the
    information stored in a pickle.

    """
    _data = np.ndarray.__new__(baseclass, baseshape, basetype)
    return subtype.__new__(subtype, _data, dtype=basetype, unitdef = True, copy=False, reconstruct=True)

p_dict = {}

def _d_multiply(q1, q2, out=None):
    try:
        return mulunit(q1._unit, q2._unit)
    except AttributeError:
        try:
            return q1._unit
        except:
            return q2._unit
p_dict[np.multiply] = _d_multiply

def _d_divide(q1, q2, out=None):
    try:
        return divunit(q1._unit , q2._unit)
    except AttributeError:
        try:
            return q1._unit
        except:
            return divunit({},q2._unit)
p_dict[np.divide] = _d_divide
p_dict[np.true_divide] = _d_divide

def _d_check_uniform(q1, q2, out=None):
    try:
        assert q1._unit == q2._unit
        return q1._unit
    except AssertionError:
        raise ValueError(
            'quantities must have identical units, got "%s" and "%s"' %
            (q1.unit, q2.unit)
        )
    except AttributeError:
        try:
            if hasattr(q1, '_unit'):
                # q2 was not a quantity
                if not q1._unit or not np.asarray(q2).any():
                    return q1._unit
                else:
                    raise ValueError
            elif hasattr(q2, '_unit'):
                # q1 was not a quantity
                if not q2._unit or not np.asarray(q1).any():
                    return q2._unit
                else:
                    raise ValueError
        except ValueError:
            raise ValueError(
                'quantities must have identical units, got "%s" and "%s"' %
                (q1.unit, q2.unit)
            )

p_dict[np.add] = _d_check_uniform
p_dict[np.subtract] = _d_check_uniform
p_dict[np.mod] = _d_check_uniform
p_dict[np.fmod] = _d_check_uniform
p_dict[np.remainder] = _d_check_uniform
p_dict[np.floor_divide] = _d_check_uniform
p_dict[np.arctan2] = _d_check_uniform

def _d_power(q1, q2, out=None):
    if getattr(q2, '_unit', None):
        raise ValueError("exponent must be dimensionless")
    try:
        q2 = np.array(q2)
        p = q2.min()
        if p != q2.max():
            raise ValueError('Quantities must be raised to a uniform power')
        return powunit(q1._unit,p)
    except AttributeError:
        return {}
p_dict[np.power] = _d_power

def _d_square(q1, out=None):
    return powunit(q1._unit,2)
p_dict[np.square] = _d_square

def _d_reciprocal(q1, out=None):
    return divunit({},q1._unit)
p_dict[np.reciprocal] = _d_reciprocal

def _d_copy(q1, out=None):
    return q1._unit
p_dict[np.absolute] = _d_copy
p_dict[np.conjugate] = _d_copy
p_dict[np.negative] = _d_copy
p_dict[np.ones_like] = _d_copy
p_dict[np.rint] = _d_copy
p_dict[np.floor] = _d_copy
p_dict[np.fix] = _d_copy
p_dict[np.ceil] = _d_copy

def _d_sqrt(q1, out=None):
    return powunit(q1._unit,0.5)
p_dict[np.sqrt] = _d_sqrt

def _d_radians(q1, out=None):
    try:
        assert q1._unit == {}
    except AssertionError:
        raise ValueError(
            'expected units of radians, got "%s"' % format_unit(q1._unit)
        )
    return {}
p_dict[np.radians] = _d_radians

def _d_degrees(q1, out=None):
    try:
        assert q1._unit == {}
    except AssertionError:
        raise ValueError(
            'expected units of radians, got "%s"' % format_unit(q1._unit)
        )
    return {}
p_dict[np.degrees] = _d_degrees

def _d_dimensionless(q1, out=None):
    if getattr(q1, '_unit', None):
        raise ValueError("quantity must be dimensionless")
    return Dimensionality()
p_dict[np.log] = _d_dimensionless
p_dict[np.log10] = _d_dimensionless
p_dict[np.log2] = _d_dimensionless
p_dict[np.log1p] = _d_dimensionless
p_dict[np.exp] = _d_dimensionless
p_dict[np.expm1] = _d_dimensionless
p_dict[np.logaddexp] = _d_dimensionless
p_dict[np.logaddexp2] = _d_dimensionless

def _d_trig(q1, out=None):
    try:
        assert q1._unit == {}
    except AssertionError:
        raise ValueError(
            'expected units of radians, got "%s"' % q1._unit
        )
    return {}
p_dict[np.sin] = _d_trig
p_dict[np.sinh] = _d_trig
p_dict[np.cos] = _d_trig
p_dict[np.cosh] = _d_trig
p_dict[np.tan] = _d_trig
p_dict[np.tanh] = _d_trig

def _d_arctrig(q1, out=None):
    if getattr(q1, '_unit', None):
        raise ValueError("quantity must be dimensionless")
    return {}
p_dict[np.arcsin] = _d_arctrig
p_dict[np.arcsinh] = _d_arctrig
p_dict[np.arccos] = _d_arctrig
p_dict[np.arccosh] = _d_arctrig
p_dict[np.arctan] = _d_arctrig
p_dict[np.arctanh] = _d_arctrig


if __name__ == '__main__':
    from .ufloat import ufloat
    s = UnitArray(1, {'s':1}, unitdef = True)
    m = UnitArray(1, {'m':1}, unitdef = True)
    ss = ufloat(1, {'s':1})
    mm = ufloat(1, {'m':1})
    ms = 0.001*s
    mm = 0.001*m

