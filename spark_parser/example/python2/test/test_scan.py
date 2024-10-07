#!/usr/bin/env python

import unittest
from sys import version_info

from helper import helper_init, run_tests_unit

scan_dir = helper_init(__file__, "scan")

if version_info[:2] < (3, 9):
    from py2_scan import Python2Scanner
else:
    from spark_parser.example.python2.py2_scan import Python2Scanner


def run_scan(python_file):
    # Note: need to initialize scanner each time.
    return Python2Scanner().tokenize(python_file)


class TestPy2Scanner(unittest.TestCase):
    def test_all(self):
        run_tests_unit(self, run_scan, scan_dir, verbose=False)


if __name__ == "__main__":
    unittest.main()
