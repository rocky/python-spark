|CircleCI| |Pypi Installs| |Latest Version| |Supported Python Versions|

|packagestatus|

An Earley Algorithm Parser toolkit.
===========================================

This package uses Jay Earley's algorithm for parsing context-free
grammars, and comes with some generic Abstract Syntax Tree
routines. There is also a prototype scanner that does its job by
combining Python regular expressions.

(SPARK stands for Scanning, Parsing, and Rewriting Kit. It is a poor
name since it conflicts with a more popular package of the same
name. In the future we will rename this.)

The original version of this was written by John Aycock for his Ph.d
thesis and was described in his 1998 paper: "Compiling Little
Languages in Python" at the 7th International Python Conference. The
current incarnation of this code is maintained (or not) by Rocky
Bernstein.

Note: Earley algorithm parsers are almost linear when given an LR grammar.
These are grammars that are left-recursive.

Installation
------------

This package is available from PyPI::

    $ pip install spark-parser

However if you want to install from the github source::

    $ pip install       # creates wheel and install

To run from the source tree::

    $ pip install -e .  # set up to run from source tree


Features
--------

Many of the added features are directly related to using it in the Python decompiler uncompyle6_.

One unique feature of this code is the ability to have it profile
which grammar rules have been used over a series of parses. This can
inform which grammar rules are not needed.

Another unusual feature is to be able to remove grammar rules after a
rule has been added. This is used in uncompyle6_ where grammar rules
inherited from one version of Python to another.

The non-standard grammar generator system feature is the ability to
perform a callback check just before a reduction rule occurs. This
allows for checking a token stream or partial parse tree by means
other than through the grammar language.

`NEW-FEATURES
<https://github.com/rocky/python-spark/blob/master/NEW-FEATURES.rst>`_
describes these features and others in more detail.


Example
-------

The github `example directory <https://github.com/rocky/python-spark/tree/master/example>`_ has worked-out examples; The PyPI package uncompyle6_ uses this and contains a much larger example.

Support of older versions of Python
-----------------------------------

We support running this from older versions of Python in various git branches:

* ``python-2.4-to-2.7`` has code for Python 2.4 to 2.7
* ``python-3.0-to-3.2`` has code for Python 3.0 to 3.2
* ``python-3.3-to-3.5`` has code for Python 3.3 to 3.5
* ``python-3.6-to-3.10`` has code for Python 3.6 to 3.10
* ``master`` has code for Python 3.11 to the current version of Python


See Also
--------

* http://pages.cpsc.ucalgary.ca/~aycock/spark/ (Old and not very well maintained)
* https://pypi.python.org/pypi/uncompyle6/

.. |CircleCI| image:: https://circleci.com/gh/rocky/python-spark.svg?style=svg
.. _features: https://github.com/rocky/python-spark/blob/master/NEW-FEATURES.rstxo
.. _directory: https://github.com/rocky/python-spark/tree/master/example
.. _uncompyle6: https://pypi.python.org/pypi/uncompyle6/
.. |downloads| image:: https://img.shields.io/pypi/dd/spark.svg
.. |buildstatus| image:: https://travis-ci.org/rocky/python-spark.svg
		 :target: https://travis-ci.org/rocky/python-spark
.. |Supported Python Versions| image:: https://img.shields.io/pypi/pyversions/spark_parser.svg
.. |Latest Version| image:: https://badge.fury.io/py/spark-parser.svg
		 :target: https://badge.fury.io/py/spark-parser
.. |Pypi Installs| image:: https://pepy.tech/badge/spark-parser/month
.. |packagestatus| image:: https://repology.org/badge/vertical-allrepos/python:spark.svg
		 :target: https://repology.org/project/python:spark/versions
