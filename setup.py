#!/usr/bin/env python

from distutils.core import setup, Extension
from numpy import get_include

module_table = Extension("spampub", ["spampub.c"]
                         #,extra_compile_args=['-O3'],extra_link_args=['']
                         )
setup(name="spampub",
      version="1.1.3",
      description="Bug test from numpy-dev",
      author = "Val Kalatsky, Enthought, Inc.",
      author_email = "info@enthought.com",
      ext_modules=[module_table],
      include_dirs = [get_include()]
      )

if __name__ == "__main__":
    setup()
