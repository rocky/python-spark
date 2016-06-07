#!/usr/bin/env python

from helper import helper_init

scan_dir = helper_init(__file__, 'scan')
from py2_scan import Python2Scanner

scan = Python2Scanner()

def showit(expr):
    print(expr)
    tokens = scan.tokenize(expr)
    for t in tokens: print(t)
    print('-' * 30)
    return

for expr in (
#     "(10.5 + 2 / 30) // 3 >> 1",
#     """() { } + - 'abc' \"abc\" 10 10j 0x10 # foo
# # bar
# """,
    """
if True:
   if False:
      del x
   assert True
else:
   import os
   pass
    """,):
    showit(expr)
    pass
