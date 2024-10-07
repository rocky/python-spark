"""
Simple SPARK-style scanner
Copyright (c) 2016-2017 Rocky Bernstein
"""

from __future__ import print_function
from spark_parser.scanner import GenericScanner, GenericToken

class ExprScanner(GenericScanner):

    def error(self, s, pos):
        """Show text and a caret under that. For example:
x = 2y + z
     ^
"""
        print("Lexical error:")
        print("%s" % s[:pos+10])  # + 10 for trailing context
        print("%s^" % (" "*(pos-1)))
        for t in self.rv: print(t)
        raise SystemExit

    def __init__(self):
        GenericScanner.__init__(self)

    def tokenize(self, input):
        self.rv = []
        GenericScanner.tokenize(self, input)
        return self.rv

    def add_token(self, name, s):
        t = GenericToken(kind=name, attr=s)
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
        pass

    def t_paren(self, s):
        r'[()]'
        self.add_token('LPAREN' if s == '(' else 'RPAREN', s)

    def t_dot(self, s):
        r'\.'
        self.add_token('DOT', s)

    # Recognize binary operators.
    # The routines for '+' and '-' are separated from '*' and '/'
    # keep operator precidence separate.
    def t_add_op(self, s):
        r'[+-]'
        self.add_token('ADD_OP', s)

    def t_bit_op(self, s):
        r'[&|^]'
        self.add_token('BIT_OP', s)

    def t_bool_op(self, s):
        r'or|and'
        self.add_token('BOOL_OP', s)


    def t_shift(self, s):
        r'<<|>>'
        self.add_token('SHIFT_OP', s)

    def t_mult(self, s):
        r'[*][*]|//|[/*%]'
        self.add_token('MULT_OP', s)

    # Recognize integers
    def t_number(self, s):
        r'(0x[0-9a-f]+|0b[01]+|0o[0-7]+|\d+\.\d|\d+)j?'
        self.add_token('NUMBER', s)

    # Recognize Boolean constants
    def t_bool(self, s):
        r'True|False'
        self.add_token('BOOL', bool(s))


if __name__ == "__main__":
    tokens = ExprScanner().tokenize("(10.5 + 2**1 / 30) // 3 >> 1")
    for t in tokens:
        print(t)
    pass
