# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 23:13:49 2012

@author: Christoph Gohle
"""

from .ufloat import UnitArray as a
from os.path import join, dirname
filename = join(dirname(__file__),'units.py')
with open(filename) as f:
    code = compile(f.read(), filename, 'exec')
    exec(code, {'u': lambda v, d: a(v,d, unitdef = True)}, locals())
del code

