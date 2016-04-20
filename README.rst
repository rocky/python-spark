|downloads| |buildstatus|

SPARK
=====

SPARK stands for the Scanning, Parsing, and Rewriting Kit. It formerly
had no name, and was referred to as the "little language framework."
The first version (circa 1998) was described in the paper Compiling
Little Languages in Python at the 7th International Python Conference.



Installation
------------

This uses setup.py, so it follows the standard Python routine:

::

    python setup.py install # may need sudo
    # or if you have pyenv:
    python setup.py develop

A GNU makefile is also provided so `make install` (possibly as root or
sudo) will do the steps above.

Testing
-------

::

   make check

A GNU makefile has been added to smooth over setting running the right
command, and running tests from fastest to slowest.

If you have remake_ installed, you can see the list of all tasks
including tests via `remake --tasks`


See Also
--------

* http://pages.cpsc.ucalgary.ca/~aycock/spark/
* https://pypi.python.org/pypi/uncompyle6/

.. |downloads| image:: https://img.shields.io/pypi/dd/spark.svg
.. |buildstatus| image:: https://travis-ci.org/rocky/python-uspark.svg
		 :target: https://travis-ci.org/rocky/python-spark
