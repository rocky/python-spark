#!/usr/bin/env python

from helper import run_tests_unit, helper_init
import unittest

scan_dir = helper_init(__file__, 'scan')
from py2_scan import Python2Scanner

def run_scan(python_file):
    # Note: need to initialize scanner each time.
    return Python2Scanner().tokenize(python_file)

class TestPy2Scanner(unittest.TestCase):
    def test_all(self):
        run_tests_unit(self, run_scan, scan_dir, verbose=False)

if __name__ == '__main__':
    unittest.main()
