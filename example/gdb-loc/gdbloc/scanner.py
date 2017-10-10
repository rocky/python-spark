"""
Simple SPARK-style scanner
Copyright (c) 2017 Rocky Bernstein
"""

from __future__ import print_function
import re
from spark_parser.scanner import GenericScanner
from gdbloc.tok import Token

class LocationScanner(GenericScanner):

    def error(self, s):
        """Show text and a caret under that. For example:
x = 2y + z
     ^
"""
        print("Lexical error:")
        print("%s" % s[:self.pos+10])  # + 10 for trailing context
        print("%s^" % (" "*(self.pos-1)))
        for t in self.rv: print(t)
        raise SystemExit

    def tokenize(self, input):
        self.rv = []
        GenericScanner.tokenize(self, input)
        return self.rv

    def add_token(self, name, v):
        t = Token(kind=name, value=v, offset=self.pos)
        self.pos += len(str(v))
        self.rv.append(t)

    # The function names below begin with 't_'.
    # This indicates to GenericScanner that these routines
    # form the tokens. GenericScanner introspects on the
    # method names of this class and the docstrings to come
    # up with both the names of the tokens and the regular expressions
    # that make up those tokens

    # Recognize white space, but we don't create a token for it.
    # This has the effect of stripping white space between tokens
    def t_whitespace(self, s):
        r'\s+'
        self.add_token('SPACE', s)
        pass

    def t_file_or_func(self, s):
        r'(?:[^-+,\d\'"\t \n:][^\'"\t \n:]*)|(?:^""".+""")|(?:\'\'\'.+\'\'\')'
        maybe_funcname = True
        if s == 'if':
            self.add_token('IF', s)
            return
        if s[0] in ["""'\""""]:
            maybe_funcname = False
            base = s[1:-1]
        else:
            base = s
        pos = self.pos
        if maybe_funcname and re.match('[a-zA-Z_]\w+\(\)', s):
            self.add_token('FUNCNAME', base)
        else:
            self.add_token('FILENAME', base)
        self.pos = pos + len(s)

    def t_colon(self, s):
        r':'
        # Used to separate a filename from a line number
        self.add_token('COLON', s)

    def t_comma(self, s):
        r','
        # Used in "list" to separate first from last
        self.add_token('COMMA', s)

    def t_direction(self, s):
        r'[+-]'
        # Used in the "list" command
        self.add_token('DIRECTION', s)

    # Recognize integers
    def t_number(self, s):
        r'\d+'
        pos = self.pos
        self.add_token('NUMBER', int(s))
        self.pos = pos + len(s)

# if __name__ == "__main__":
#     for line in (
#             # '/tmp/foo.py:12',
#             # "'''/tmp/foo.py:12'''",
#             # "/tmp/foo.py line 12",
#             # "\"\"\"/tmp/foo.py's line 12\"\"\"",
#             # "12",
#             # "../foo.py:5",
#             # "gcd()",
#             # "foo.py line 5 if x > 1",
#             "5 ,",
#             "5,",
#             "5,10",
#             ",10",
#             ):
#         tokens = LocationScanner().tokenize(line.strip())
#         for t in tokens:
#             print(t)
#             pass
#         pass
#     pass
