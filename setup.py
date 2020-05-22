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
Copyright (C) 2016 Rocky Bernstein <rb@dustyfeet.com>.
"""

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.3",
    "Programming Language :: Python :: 2.4",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

# The rest in alphabetic order
author = "John Aycock"
ftp_url = None
license = "MIT"
maintainer = "Rocky Bernstein"
maintainer_email = "rb@dustyfeet.com"
modname = "spark_parser"
name = "spark_parser"
py_modules = None
short_desc = "An Earley-Algorithm Context-free grammar Parser Toolkit"
web = "https://github.com/rocky/python-spark/"

# tracebacks in zip files are funky and not debuggable
zip_safe = True

# Python-version | package | last-version |
# -----------------------------------------
# 3.2            | click   | 4.0          |
# 3.2            | pip     | 8.1.2        |
# 3.3            | pip     | 10.0.1       |
# 3.4            | pip     | 19.1.1       |

import os.path as osp


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


srcdir = get_srcdir()


def read(*rnames):
    return open(osp.join(srcdir, *rnames)).read()


# Get info from files; set: long_description and VERSION
long_description = read("README.rst") + "\n"
exec(read("spark_parser/version.py"))

import sys

if (3, 0) <= sys.version_info[:2] <= (3, 2):
    click_version = "<= 4.0"
else:
    click_version = ""

from setuptools import setup, find_packages

setup(
    classifiers=classifiers,
    description=short_desc,
    install_requires=["click%s" % click_version],
    license=license,
    long_description=long_description,
    long_description_content_type="text/x-rst",
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    packages=find_packages(),
    py_modules=py_modules,
    name=name,
    scripts=["bin/spark-parser-coverage"],
    test_suite="nose.collector",
    url=web,
    tests_require=["nose>=1.0"],
    version=VERSION,
    zip_safe=zip_safe,
)
