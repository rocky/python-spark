#!/usr/bin/env python

import sys
import unittest

from helper import helper_init, run_tests_unit

parse_dir = helper_init(__file__, "parse")

if sys.version_info[:2] < (3, 9):
    from py2_parser import parse_python2
else:
    from spark_parser.example.python2.py2_parser import parse_python2


def run_parse(python2_stmts):
    tokens = parse_python2(python2_stmts, show_tokens=False)
    return str(tokens).split("\n")


class TestPy2Parser(unittest.TestCase):
    def test_all(self):
        run_tests_unit(self, run_parse, parse_dir, verbose=False)


if __name__ == "__main__":
    unittest.main()
