#!/usr/bin/env python
# Command-line program to use the parser to reflow
# a Python 2.6 program
import sys
from py2_scan import Python2Scanner

scan = Python2Scanner()


if len(sys.argv) < 2:
    print("I need a filename to reformat")
    sys.exit(1)

do_format = True
do_scan_only = False

i = 1
if sys.argv[i] == '--scan':
    pass
