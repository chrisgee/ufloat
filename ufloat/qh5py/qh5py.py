#!/usr/bin/env python
# -*- mode: Python; coding: utf-8 -*-
# Time-stamp: "2017-02-16 14:04:42 srlab"
#
#  file       qh5py.py
#  author     Christoph Gohle
#  created    2012-12-17 10:05:11
#
#  Copyright (C) 2011 -- 2017 Christoph Gohle, Christian Gross
#  Copyright (C) 2016, 2017 Christoph Gohle, Christian Gross, Sebastian Blatt
#
#  This file is required for qcontrol -- The MPQ-developed, python-based
#  experiment control program.
#
#  License:
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
#  Commentary:
#
#    A wrapper around h5py that supports some special data types that
#    are not natively supported. Specifically, numbers with units get
#    native support here. It also supports assigning dictionaries to
#    groups. Then each k,v pair will be added to the data as a named
#    dataset to the group that was assigned. Obviously, only string
#    type keys are supported.
#
#    SB: With new `bytes' type that is different from `str' in
#    python3, h5py starts throwing errors when trying to write a bytes
#    object that contains 0x00 (NULL byte) as a string to the HDF5
#    file. Try to autodetect this by looking for bytes objects.
#
#

# SB 160826: For bytes type handling
import six
from numpy import void


import h5py as h
import ufloat as uf
UNITATTR = 'unit'
import os.path as osp

#place all names from h5py here as well except for those that we extend

selfdefnames = ('Group', 'Dataset', 'AttributeManager', 'File', '__file__',
                '__name__', '__package__', '__path__', '__doc__')

for n in dir(h):
    if n not in selfdefnames:
        globals()[n] = getattr(h, n)


class Group(h.Group):
    def __init__(self, *args, **kwargs):
        self._sm = kwargs.pop('sm', None)
        super(Group, self).__init__(*args, **kwargs)

    def create_group(self, name):
        s = super(Group, self).create_group(name)
        return Group(s._id, sm=self)

    def create_dataset(self, name, shape=None, dtype=None, data=None, **kwds):
        s = super(Group, self).create_dataset(name, shape, dtype, data, **kwds)
        if hasattr(data, UNITATTR):
            #assume this is something that has a unit (and a 'symbol' property)
            s.attrs[UNITATTR] = data.symbol
        else:
            pass
        return Dataset(s._id, sm=self)

    def __getitem__(self, name):
        res = super(Group, self).__getitem__(name)
        if isinstance(res, h.Dataset):
            res = Dataset(res._id, sm=self)
        elif isinstance(res, h.Group):
            res = Group(res._id, sm=self)
        return res

    def __setitem__(self, name, value):
        if hasattr(value, 'unit'):
            super(Group, self).__setitem__(name, value.value)
            self[name].attrs[UNITATTR] = value.symbol

        # SB 160826 handle binary blobs. see below
        elif six.PY3 and type(value) == six.binary_type:
            self[name] = void(value)
            self[name].attrs['is_binary'] = True

        elif isinstance(value, dict):
            if name in list(self.keys()):
                g = self[name]
            else:
                g = self.create_group(name)

            for k, v in list(value.items()):
                g[k] = v
        else:
            super(Group, self).__setitem__(name, value)

    @property
    def base(self):
        if self._sm is not None:
            return self._sm.base
        else:
            return self

    @property
    def attrs(self):
        return AttributeManager(self, sm=self)

    @attrs.setter
    def attrs(self, value):
        if not isinstance(value, dict):
            raise ValueError(
                'only string valued dictionaries can be assigned to the attribute list')
        else:
            self.attrs.update(value)


class File(Group, h.File):
    def __init__(self, *args, **kwargs):
        self.close_callback = kwargs.pop('close_callback', None)
        self.cb_args = kwargs.pop('cb_args', ())
        self._sm = None
        h.File.__init__(self, *args, **kwargs)

    def __del__(self):
        if self.id.id is not 0:
            self.close()

    def close(self):
        super(File, self).close()
        if self.close_callback is not None:
            self.close_callback(*self.cb_args)
        if self.id.id is not 0:
            self.id.id = 0

            #allow pickling of the file. the unpickled file knows nothing
    def __getstate__(self):
        return osp.abspath(self.filename)

    def __setstate__(self, state):
        h.File.__init__(self, state, 'r')


class Dataset(h.Dataset):
    def __init__(self, *args, **kwargs):
        self._sm = kwargs.pop('sm', False)
        super(Dataset, self).__init__(*args, **kwargs)

    @property
    def value(self):
        return self[()]

    def __getitem__(self, args):
        res = super(Dataset, self).__getitem__(args)
        if UNITATTR in list(self.attrs.keys()):
            res = uf.ufloat(1, uf.unit_from_string(self.attrs[UNITATTR])) * res

        # SB 160826 handle binary blob, see below
        if six.PY3 and 'is_binary' in self.attrs:
            if self.attrs['is_binary'] == True:
                return res.tostring()

        return res

    def __setitem__(self, args, val):
        if UNITATTR in list(self.attrs.keys()):
            u = uf.unit_from_string(self.attrs[UNITATTR])
            if hasattr(val, 'unit'):
                #check if the unit can be rescaled to
                val = val.rescale(u)
            else:
                raise ValueError('%s should be of unit %s' % (val, u))

        # SB 160826 Check for bytes object and save as binary blob,
        # but only if we are in python3, because otherwise the
        # distinction is moot and we would have to grep through the
        # string to find 0x00 bytes. We will mark the binary blob
        # using an attribute.
        #
        # See
        #
        #   http://docs.h5py.org/en/latest/strings.html
        #
        if six.PY3 and type(val) == six.binary_type:
            self.attrs['is_binary'] = True
            super(Dataset, self).__setitem__(args, void(val))

        super(Dataset, self).__setitem__(args, val)

    @property
    def base(self):
        if self._sm is not None:
            return self._sm.base
        else:
            return self

    @property
    def attrs(self):
        return AttributeManager(self, sm=self)

    @attrs.setter
    def attrs(self, value):
        if not isinstance(value, dict):
            raise ValueError(
                'only string valued dictionaries can be assigned to the attribute list')
        else:
            self.attrs.update(value)


class AttributeManager(h.AttributeManager):
    def __init__(self, *args, **kwargs):
        self._sm = kwargs.pop('sm', None)
        super(AttributeManager, self).__init__(*args, **kwargs)

    @staticmethod
    def uattr(name):
        return '.%s.unit' % name

    def __getitem__(self, name):
        res = super(AttributeManager, self).__getitem__(name)
        unitattr = self.uattr(name)
        if unitattr in list(self.keys()):
            u = super(AttributeManager, self).__getitem__(unitattr)
            res = uf.ufloat(1, uf.unit_from_string(u)) * res
        return res

    def __setitem__(self, name, value):
        if hasattr(value, 'unit'):
            super(AttributeManager, self).__setitem__(name, value.value)
            super(AttributeManager, self).__setitem__(
                self.uattr(name), value.symbol)
        else:
            super(AttributeManager, self).__setitem__(name, value)

        base = self._sm.base
        if hasattr(base, 'readme'):
            fn = self._sm.name  #.replace('/','_')
            if base.level is not None and fn.count('/') - 1 > base.level:
                #subgroup level exceeds given level -> don't store in readme
                return
            base.readme.set(name, value, fn, save=False)

    def update(self, dict):
        """update the attributes list with the contents of a dictionary.

        Obviously this only works for dictionaries with string type keys."""
        for k, v in list(dict.items()):
            self[k] = v


# qh5py.py ends here
