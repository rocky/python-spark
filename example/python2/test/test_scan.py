#!/usr/bin/env python

from __future__ import print_function
import sys, os
from helper import run_tests

# I hate how clumsy Python is here
dirname = os.path.join(".", os.path.dirname(__file__))
parent_dir = os.path.join("..", os.path.dirname(__file__))
sys.path.append(parent_dir)
from py2_scan import Python2Scanner

scan_dir = os.path.join(dirname, 'scan')

def run_scan(python_file):
    # Note: need to initialize scanner each time.
    return Python2Scanner().tokenize(python_file)

run_tests(run_scan, scan_dir)
