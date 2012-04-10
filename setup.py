# -*- coding: utf-8 -*-
#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from numpy import get_include

packages = ['ufloat']
ext_modules = [#Extension("cyunits", ["cyunits.pyx"]),
#               Extension("funit",["funit.pyx"]),
               Extension("ufloat.ufloat",["ufloat/ufloat.pyx"])]
requires = ['numpy']
# You can add directives for each extension too # by attaching the ‘pyrex_directives‘
for e in ext_modules:
	e.pyrex_directives = {"boundscheck": False}

setup(name="ufloat",
      version="0.0.1",
      description="fast physical units for scalars and numpy arrays",
      author = "Christoph Gohle, MPI für Quantenoptik",
      author_email = "christoph.gohle@mpq.mpg.de",
      ext_modules=ext_modules,
      packages = packages,
      include_dirs = [get_include()],
      cmdclass = {"build_ext": build_ext},
      requires = requires
      )

if __name__ == "__main__":
    setup()
