|buildstatus| |Supported Python Versions|

SPARK
=====

SPARK stands for Scanning, Parsing, and Rewriting Kit. It uses Jay
Earley's algorithm for parsing context free grammars, and comes with
some generic Abstract Syntax Tree routines. There is also a prototype
scanner which does its job by combining Python regular expressions.

The original version of this was written by John Aycock for his Ph.d
thesis and was described in his 1998 paper: "Compiling Little
Languages in Python" at the 7th International Python Conference. The
current incarnation of this code is maintained (or not) by Rocky
Bernstein.

Note: Earley algorithm parsers are almost linear when given an LR grammar.
These are grammars which are left-recursive.

Installation
------------

This uses `setup.py`, so it follows the standard Python routine:

::

    python setup.py install # may need sudo
    # or if you have pyenv:
    python setup.py develop

Example
-------

The github `example` directory_ has a worked-out examples; Package uncompyle6_
uses this and contains a much larger example.

See Also
--------

* features_
* http://pages.cpsc.ucalgary.ca/~aycock/spark/ (Old and not very well maintained)
* https://pypi.python.org/pypi/uncompyle6/

.. _features: https://github.com/rocky/python-spark/blob/master/NEW-FEATURES.rst
.. _directory: https://github.com/rocky/python-spark/tree/master/example
.. _uncompyle6: https://pypi.python.org/pypi/uncompyle6/
.. |downloads| image:: https://img.shields.io/pypi/dd/spark.svg
.. |buildstatus| image:: https://travis-ci.org/rocky/python-spark.svg
		 :target: https://travis-ci.org/rocky/python-spark
.. |Supported Python Versions| image:: https://img.shields.io/pypi/pyversions/spark_parser.svg
