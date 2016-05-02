|buildstatus|

SPARK
=====

SPARK stands for the Scanning, Parsing, and Rewriting Kit. It is
a Jay Early Algorithm Parser with some generic Abstract Syntax
Tree-building routines.

The first version was written by John Aycock was described in his 1988 paper:
"Compiling Little Languages in Python" at the 7th International Python
Conference.



Installation
------------

This uses setup.py, so it follows the standard Python routine:

::

    python setup.py install # may need sudo
    # or if you have pyenv:
   python setup.py develop

Example
-------

The github example directory_ has worked out example(s).



See Also
--------

* http://pages.cpsc.ucalgary.ca/~aycock/spark/ (Old and not very well maintained)
* https://pypi.python.org/pypi/uncompyle6/

.. _directory: https://github.com/rocky/python-spark/tree/master/example
.. |downloads| image:: https://img.shields.io/pypi/dd/spark.svg
.. |buildstatus| image:: https://travis-ci.org/rocky/python-spark.svg
		 :target: https://travis-ci.org/rocky/python-spark
