#!/usr/bin/env python

from __future__ import print_function

import sys, os

# I hate how clumsy Python is here
dirname = os.path.join("..", os.path.dirname(__file__))
sys.path.append(dirname)

from py2_scan import Python2Scanner

scan = Python2Scanner()

def showit(expr):
    print(expr)
    tokens = scan.tokenize(expr)
    for t in tokens: print(t)
    print('-' * 30)
    return

for expr in (
    "(10.5 + 2 / 30) // 3 >> 1",
    """() { } + - 'abc' \"abc\" 10 10j 0x10 # foo
# bar
""",
    """for i in range(x):
  pass
"""):
    showit(expr)
    pass
