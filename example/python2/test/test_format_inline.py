#!/usr/bin/env python

from __future__ import print_function

import sys, os

# I hate how clumsy Python is here
dirname = os.path.join("..", os.path.dirname(__file__))
sys.path.append(dirname)

from py2_format import format_python2_stmts

for python2_stmts in (
          """
while True:
   pass

pass
"""
        ):
    print(python2_stmts)
    print('-' * 30)
    formatted = format_python2_stmts(python2_stmts, show_tokens=True, showast=True, showgrammar=True)
    print(formatted)
    pass
