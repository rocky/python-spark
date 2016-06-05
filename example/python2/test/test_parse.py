#!/usr/bin/env python

from __future__ import print_function
import sys, os
from helper import run_tests

# I hate how clumsy Python is here
dirname = os.path.join(".", os.path.dirname(__file__))
parent_dir = os.path.join("..", os.path.dirname(__file__))
sys.path.append(parent_dir)
from py2_parser import parse_python2

parse_dir = os.path.join(dirname, 'parse')

def run_parse(python2_stmts):
    tokens = parse_python2(python2_stmts, show_tokens=False)
    return str(tokens).split("\n")

run_tests(run_parse, parse_dir)
