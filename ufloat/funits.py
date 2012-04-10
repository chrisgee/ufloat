# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 23:13:49 2012

@author: Christoph Gohle
"""

from ufloat import ufloat as u
from os.path import join, dirname
execfile(join(dirname(__file__),'units.py'), {'u':u}, locals())