from numpy.distutils.core import setup, Extension

module1 = Extension('spampub',
                                        sources = ['spammodule_public.c'])

setup (name = 'PackageName',
              version = '1.0',
                     description = 'This is a spam package',
                            ext_modules = [module1])
