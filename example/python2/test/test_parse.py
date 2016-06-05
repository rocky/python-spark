#!/usr/bin/env python

from __future__ import print_function

import sys, os

# I hate how clumsy Python is here
dirname = os.path.join("..", os.path.dirname(__file__))
sys.path.append(dirname)

from py2_parser import parse_python2

for python2_stmts in (
        # "from os import path",
        # "from os import path as shmath",
        # "import os",
        # "import sys, os",
        # "import sys, os",
        # "import os.path",
        # "import os.path, dir.foo",
        # "exec 'exec-string' in locals, globals",
        # "exec 'exec-string' in dict",
        # "exec 'exec-string'",
        # "pass",
        # "pass; del x",
        "x + y",
        "assert x == y",
        # "global a, b, c",
        # "global a",
        ):
    print(python2_stmts)
    print('-' * 30)
    ast = parse_python2(python2_stmts, show_tokens=True)
    print(ast)
    print('=' * 30)
    pass
