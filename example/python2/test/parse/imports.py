# Parsing and formatting tests for
#
# import_stmt ::=
#             import_name | import_from
#
# import_name ::=
#             'import' dotted_as_names
#
# import_from ::=
#             ('from' ('.'* dotted_name | '.'+)
#             'import' ('*' | '(' import_as_names ')' | import_as_names))
#
# import_as_name ::=
#             NAME ['as' NAME]
#
# dotted_as_name ::=
#             dotted_name ['as' NAME]
#
# import_as_names ::=
#             import_as_name (',' import_as_name)* [',']
#
# dotted_as_names ::=
#             dotted_as_name (',' dotted_as_name)*
#
# dotted_name ::=
#             NAME ('.' NAME)*

from os import path
from . import path
from .. import path
from ..foo import path
from os import path as shmath
import os
import sys, os
import os.path
import os.path as path2
import os.path, dir.foo
