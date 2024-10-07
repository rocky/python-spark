#!/usr/bin/env python
# Command-line program to use the parser to reflow
# a Python 2.6 program
import os, sys
from py2_scan import ENDMARKER, Python2Scanner
from py2_format import format_python2_stmts

scan = Python2Scanner()


if len(sys.argv) < 2:
    print("I need a filename to reformat")
    sys.exit(1)

do_format = True
do_scan_only = False

i = 1
if sys.argv[i] == '--scan':
    do_scan_only = True
    scan = Python2Scanner()
    do_format = False
    i += 1

for path in sys.argv[i:]:
    if not os.path.exists(path):
        print("Can't find file %s; skipping" % path)
        continue

    with open(path, 'r') as fp:
        python2_stmts = fp.read()

        print(python2_stmts)

        if do_scan_only:
            tokens = scan.tokenize(python2_stmts)
            for t in tokens: print(t)
            print('=' * 30)
        else:
            formatted = format_python2_stmts(python2_stmts + ENDMARKER,
                                             show_tokens=True, showast=True,
                                             showgrammar=True)
            print('=' * 30)
            print(formatted)
            pass
        pass

    pass
