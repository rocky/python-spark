#!/usr/bin/env python

"""Setup script for the 'uncompyle6' distribution."""

# To the extent possible we make this file look more like a
# configuration file rather than code like setup.py. I find putting
# configuration stuff in the middle of a function call in setup.py,
# which for example requires commas in between parameters, is a little
# less elegant than having it here with reduced code, albeit there
# still is some room for improvement.

# Things that change more often go here.
copyright   = """
Copyright (C) 2016 Rocky Bernstein <rb@dustyfeet.com>.
"""

classifiers =  ['Development Status :: 4 - Beta',
                'Intended Audience :: Developers',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Programming Language :: Python :: 2',
                'Programming Language :: Python :: 2.6',
                'Programming Language :: Python :: 2.7',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.3',
                'Programming Language :: Python :: 3.4',
                'Programming Language :: Python :: 3.5',
                'Topic :: Software Development :: Code Generators',
                'Topic :: Software Development :: Compilers ',
                'Topic :: Software Development :: Libraries :: Python Modules',
                ]

# The rest in alphabetic order
author             = "John Aycock"
ftp_url            = None
license            = 'MIT'
maintainer         = "Rocky Bernstein"
maintainer_email   = "rb@dustyfeet.com"
modname            = 'spark_parser'
name               = 'spark_parser'
py_modules         = None
short_desc         = 'An Early-Algorithm Context-free grammar Parser'
web                = 'https://github.com/rocky/python-spark/'

# tracebacks in zip files are funky and not debuggable
zip_safe = True

import os
def get_srcdir():
    filename = os.path.normcase(os.path.dirname(os.path.abspath(__file__)))
    return os.path.realpath(filename)

srcdir = get_srcdir()

def read(*rnames):
    return open(os.path.join(srcdir, *rnames)).read()

# Get info from files; set: long_description and VERSION
long_description   = ( read("README.rst") + '\n' )
exec(read('spark_parser/version.py'))

from setuptools import setup, find_packages
setup(
       classifiers        = classifiers,
       description        = short_desc,
       # install_requires   = install_requires,
       license            = license,
       long_description   = long_description,
       maintainer         = maintainer,
       maintainer_email   = maintainer_email,
       packages           = find_packages(),
       py_modules         = py_modules,
       name               = name,
       test_suite         = 'nose.collector',
       url                = web,
       setup_requires     = ['nose>=1.0'],
       version            = VERSION,
       zip_safe           = zip_safe)
