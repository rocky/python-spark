#!/usr/bin/env python

from __future__ import print_function

import sys, os

# I hate how clumsy Python is here
dirname = os.path.join("..", os.path.dirname(__file__))
sys.path.append(dirname)

from py2_format import format_python2_stmts

for python2_stmts in (
       "from os import path",
       "from os import path as shmath",
        "import os",
        "import sys, os",
        "import os.path",
        # "import os.path, dir.foo",
#        "exec 'exec-string' in locals, globals",
#        "exec 'exec-string' in dict",
#        "exec 'exec-string'",
#        "pass",
#        "pass; del x",
#        "assert x == y",
#        "global a, b, c",
#        "global a",
        ):
    print(python2_stmts)
    print('-' * 30)
    formatted = format_python2_stmts(python2_stmts, show_tokens=False, showast=False)
    print(formatted)
    pass
