#!/usr/bin/env python

"""Setup script for the 'uncompyle6' distribution."""

# Get the package information used in setup().
# from __pkginfo__ import \
#     author,           author_email,       classifiers,                    \
#     install_requires, license,            long_description,               \
#     modname,          packages,           py_modules,   \
#     short_desc,       version,            web,              zip_safe

from __pkginfo__ import \
    author,           maintainer,      maintainer_email,             \
    long_description,                                                \
    modname,          py_modules,       					         \
    short_desc,       version,          web,              zip_safe

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
       packages           = ['spark'],
       py_modules         = py_modules,
       name               = 'spark_parser',
       test_suite         = 'nose.collector',
       url                = web,
       setup_requires     = ['nose>=1.0'],
       version            = version,
       zip_safe           = zip_safe)
