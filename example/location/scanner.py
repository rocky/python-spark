"""
Simple SPARK-style scanner
Copyright (c) 2017 Rocky Bernstein
"""

from __future__ import print_function
from spark_parser.scanner import GenericScanner
from tok import Token

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

    def add_token(self, name, s):
        t = Token(kind=name, value=s, offset=self.pos)
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

    def t_filename(self, s):
        r'[^[\t \n:]+|".+"|\'.+\''
        if s == 'if':
            self.add_token('IF', s)
            return
        if s[0] in ["""'\""""]:
           base = s[1:-1]
        else:
           base = s
        self.add_token('FILENAME', base)

    def t_funcname(self, s):
        r'[a-zA-Z_]\w+\(\)'
        self.add_token('FUNCNAME', s)

    def t_colon(self, s):
        r':'
        self.add_token('COLON', s)

    # Recognize integers
    def t_number(self, s):
        r'\d+'
        self.add_token('NUMBER', int(s))

if __name__ == "__main__":
    for line in """
    /tmp/foo.py:12
    /tmp/foo.py line 12
    12
    ../foo.py:5
    gcd()
    foo.py line 5 if x > 1
    """.splitlines():
        if not line.strip():
            continue
        tokens = LocationScanner().tokenize(line.strip())
        for t in tokens:
            print(t)
            pass
        pass
    pass
