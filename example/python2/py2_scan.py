"""
Simple SPARK-style scanner
Copyright (c) 2016 Rocky Bernstein
"""

from __future__ import print_function
from spark_parser.scanner import GenericScanner, GenericToken

import re
RESERVED_WORDS = re.split("\s+",
"""as assert break class continue def del eval exec else elif for from global
if in import pass print return self while yield""")

BRACKET2NAME = {
    '(': 'LPAREN',   ')': 'RPAREN',
    '{': 'LBRACE',   '}': 'RBRACE',
    '[': 'LBRACKET', ']': 'RBRACKET',
    }

class Python2Scanner(GenericScanner):

    def error(self, s, pos):
        """Show text and a carot under that. For example:
x = 2y + z
     ^
"""
        print("Lexical error:")
        print("%s" % s[:pos+10])  # + 10 for trailing context
        print("%s^" % (" "*(pos-1)))
        for t in self.rv: print(t)
        raise SystemExit

    def __init__(self):
        self.is_newline = True
        self.indents = [0]
        GenericScanner.__init__(self)

    def tokenize(self, input):
        self.rv = []
        GenericScanner.tokenize(self, input)
        return self.rv

    def add_token(self, name, s, is_newline=False):
        t = GenericToken(kind=name, attr=s)
        if self.is_newline and name not in ['DEDENT', 'INDENT']:
            while 0 < self.indents[-1]:
                self.indents = self.indents[0:-1]
                self.rv.append(GenericToken(kind='DEDENT', attr=''))
                self.rv.append(GenericToken(kind='NEWLINE', attr=''))
                pass
        self.is_newline = is_newline
        self.rv.append(t)

    # The function names below begin with 't_'.
    # This indicates to GenericScanner that these routines
    # form the tokens. GenericScanner introspects on the
    # method names of this class and the docstrings to come
    # up with both the names of the tokens and the regular expressions
    # that make up those tokens

    def t_lparen(self, s):
        r'[(){}[\]]'
        self.add_token(BRACKET2NAME[s], s)

    def t_op(self, s):
        r'\+=|-=|\*=|/=|%=|&=|\|=|^=|<<=|>>=|\*\*=|//=|//|==|<=|>=|is|<<|>>|[<>%^&+/-]'
        # FIXME: handle is not and not in
        if s in ('<', '>', '==', '>=', '<>', '!=', 'in', 'not', 'is'):
            self.add_token('COMP_OP', s)
        elif s in ('+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=', '**=',
                    '//='):
            self.add_token('AUGASSIGN', s)
        elif s in ('+', '-', '*', '/', '%', '&', '|', '^', '<<', '>>', '**', '//'):
            self.add_token('OP', s)
        else:
            print("Internal error: Unknown operator %s" % s)
            raise SystemExit

    def t_unop(self, s):
        r'[~]'
        self.add_token('UNOP', s)

    def t_linesep(self, s):
         r';'
         self.add_token('SEMICOLON', s)

    # Note: we can reuse the same token name to simplify
    # regexps and as another way we can achieve regexp |
    def t_nl(self, s):
         r'\n'
         self.add_token('NEWLINE', s, is_newline=True)

    def t_comment(self, s):
         r'[#].*'
         self.add_token('COMMENT', s)

    def t_name(self, s):
        r'[A-Za-z_][A-Z-a-z_0-9]*'
        if s in RESERVED_WORDS:
            self.add_token(s.upper(), s)
        else:
            self.add_token('NAME', s)

    # A way to handle the problem of having to match two different
    # tokens with a single regular expression.
    # We can't have two separate defs because then it would be indeterminate
    # whether we get two single stars or one double star.
    def t_star_star(self, s):
        r'\*\*?'
        token_name = "STARSTAR" if len(s) == 2 else 'STAR'
        self.add_token(token_name, s)

    # CONSTANTS
    # ---------

    def t_string(self, s):
        r"('[^']*')|(\"[^\"]*\")"
        self.add_token('STRING', s)

    # numbers; int, float, and complex

    # Note we have to put longer matches earlier. Specifically radix notation and
    # fixed-point notation
    def t_number(self, s):
        r'(0x[0-9a-f]+|0b[01]+|0o[0-7]+|\d+\.\d|\d+)j?'
        self.add_token('NUMBER', s)

    def t_at(self, s):
        r'@'
        self.add_token('@', s)

    def t_dot(self, s):
        r'\.'
        self.add_token('DOT', s)

    def t_colon(self, s):
        r':'
        self.add_token('COLON', s)

    def t_comma(self, s):
        r','
        self.add_token('COMMA', s)

    def t_whitespace(self, s):
        r'[ \t]+'
        if self.is_newline:
            # Ugh. Handle Python's indent/dedent mess.
            indent = len(s)
            if indent > self.indents[-1]:
                self.add_token('INDENT', s)
                self.indents.append(indent)
            else:
                # May need several levels of dedent
                while indent < self.indents[-1]:
                    self.indents = self.indents[0:-1]
                    self.add_token('DEDENT', s)
                    pass
                pass
            pass
        return

if __name__ == "__main__":
    scan = Python2Scanner()
    def showit(expr):
        print(expr)
        tokens = scan.tokenize(expr)
        for t in tokens: print(t)
        print('-' * 30)
        return

#     showit("(10.5 + 2 / 30) // 3 >> 1")
#     showit("""
# () { } + - 'abc' \"abc\" 10 10j 0x10 # foo
# # bar
# """)
#     showit("""
# for i in range(x):
#   if True:
#      pass
#   pass
# pass""")
    showit("""
for i in range(x):
    while True:
       break
pass""")
