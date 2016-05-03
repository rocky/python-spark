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
                'Topic :: Software Development :: Code Generators'
                'Topic :: Software Development :: Compilers '
                'Topic :: Software Development :: Libraries :: Python Modules',
                ]

# The rest in alphabetic order
author             = "John Aycock"
ftp_url            = None
license            = 'MIT'
maintainer         = "Rocky Bernstein"
maintainer_email   = "rb@dustyfeet.com"
modname            = 'spark_parser'
py_modules         = None
short_desc         = 'An Early-Algorithm LR Parser'

import os.path


def get_srcdir():
    filename = os.path.normcase(os.path.dirname(os.path.abspath(__file__)))
    return os.path.realpath(filename)

ns = {}
version            = '1.1.1'
web                = 'https://github.com/rocky/python-spark/'

# tracebacks in zip files are funky and not debuggable
zip_safe = True


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description   = ( read("README.rst") + '\n' )

__import__('pkg_resources')
from setuptools import setup

setup(
       # classifiers        = classifiers,
       description        = short_desc,
       # install_requires   = install_requires,
       # license            = license,
       long_description   = long_description,
       maintainer         = maintainer,
       maintainer_email   = maintainer_email,
       packages           = ['spark_parser'],
       py_modules         = py_modules,
       name               = 'spark_parser',
       test_suite         = 'nose.collector',
       url                = web,
       setup_requires     = ['nose>=1.0'],
       version            = version,
       zip_safe           = zip_safe)
