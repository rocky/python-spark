#!/usr/bin/env python

import unittest

from helper import helper_init, run_tests_unit

format_dir = helper_init(__file__, "format")
from spark_parser.example.python2.py2_format import format_python2_stmts


def run_format(python2_stmts):
    formatted = format_python2_stmts(python2_stmts, showast=False)
    return str(formatted).split("\n")


class TestPy2Format(unittest.TestCase):
    def test_all(self):
        run_tests_unit(self, run_format, format_dir)


if __name__ == "__main__":
    unittest.main()
