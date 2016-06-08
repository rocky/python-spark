#!/usr/bin/env python

from __future__ import print_function

import sys, os

# I hate how clumsy Python is here
dirname = os.path.join("..", os.path.dirname(__file__))
sys.path.append(dirname)

from py2_parser import parse_python2

for python2_stmts in (
        """def foo(): pass
""",
        # "assert x == y",
        # "global a, b, c",
        # "global a",
        ):
    print(python2_stmts)
    print('-' * 30)
    parser_debug = {'rules': True, 'transition': False, 'reduce': True,
                     'errorstack': True, 'context': True}
    ast = parse_python2(python2_stmts, start='eval_input', show_tokens=True,
                        parser_debug=parser_debug)
    print(ast)
    print('=' * 30)
    pass
