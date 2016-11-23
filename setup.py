#!/usr/bin/env python

"""Setup script for the 'spark_parser' distribution."""

# To the extent possible we make this file look more like a
# configuration file rather than code like setup.py. I find putting
# configuration stuff in the middle of a function call in setup.py,
# which for example requires commas in between parameters, is a little
# less elegant than having it here with reduced code, albeit there
# still is some room for improvement.

# Things that change more often go here.
copyright = """
Copyright (C) 2016, 2022, 2024 Rocky Bernstein <rb@dustyfeet.com>.
"""

from setuptools import setup
classifiers =  ['Development Status :: 4 - Beta',
                'Intended Audience :: Developers',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Programming Language :: Python :: 2.3',
                'Programming Language :: Python :: 2.4',
                'Programming Language :: Python :: 2.5',
                'Programming Language :: Python :: 2.6',
                'Programming Language :: Python :: 2.7',
                'Programming Language :: Python :: 3.3',
                'Programming Language :: Python :: 3.4',
                'Programming Language :: Python :: 3.5',
                'Topic :: Software Development :: Code Generators',
                'Topic :: Software Development :: Compilers ',
                'Topic :: Software Development :: Libraries :: Python Modules',
                ]
setup()
