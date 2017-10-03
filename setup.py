# -*- coding: utf-8 -*-
#!/usr/bin/env python

from setuptools import setup, Extension
from Cython.Distutils import build_ext
from numpy import get_include

packages = ['ufloat', 'qh5py']
ext_modules = [Extension("ufloat.ufloat",["ufloat/ufloat.pyx"])]
requires = ['numpy']
# You can add directives for each extension too # by attaching the ‘pyrex_directives‘
for e in ext_modules:
	e.pyrex_directives = {"boundscheck": False}

setup(name="ufloat",
      version="0.1.0",
      description="Fast physical units for scalars and numpy arrays and an extension to h5py for them.",
      author = "Christoph Gohle, MPI für Quantenoptik",
      author_email = "christoph.gohle@mpq.mpg.de",
      ext_modules=ext_modules,
      packages = packages,
      cmdclass = {'build_ext': build_ext},
      include_dirs = [get_include()],
      requires = requires,
      setup_requires = ['cython','nose>=1.0'],
      test_suite = 'nose.collector'
      )

if __name__ == "__main__":
    pass
