"""
Simple SPARK-style scanner
Copyright (c) 2016 Rocky Bernstein
"""

import re

from spark_parser.example.python2.py2_token import PythonToken

# from __future__ import print_function
from spark_parser.scanner import GenericScanner

RESERVED_WORDS = re.split(
    r"\s+",
    """and as assert break class continue def del eval exec else elif for from global
if in import lambda or pass print return while with yield None""",
)

BRACKET2NAME = {
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    "[": "LBRACKET",
    "]": "RBRACKET",
}

SYMBOL2NAME = {
    "@": "AT",
    "`": "BACKTICK",
    ":": "COLON",
    ",": "COMMA",
    ".": "DOT",
}

ENDMARKER = r""  # ctrl-d


class Python2Scanner(GenericScanner):
    def error(self, s, pos):
        """Show text and a carot under that. For example:
        x = 2y + z
             ^"""
        print("Lexical error:")
        print("%s" % s[: pos + 10])  # + 10 for trailing context
        print("%s^" % (" " * (pos - 1)))
        for t in self.rv:
            print(t)
        raise SystemExit

    def __init__(self):
        self.is_newline = True
        self.indents = [0]
        self.lineno = 1
        self.column = 0
        GenericScanner.__init__(self)

    def tokenize(self, string):
        self.rv = []
        GenericScanner.tokenize(self, string)
        return self.rv

    def add_token(self, name, s, is_newline=False):
        self.column += len(s)
        t = PythonToken(name, s, self.lineno, self.column)
        if is_newline:
            self.lineno += 1
            self.column = 0
        if self.is_newline and name not in ["DEDENT", "INDENT"]:
            while 0 < self.indents[-1]:
                self.indents = self.indents[0:-1]
                self.rv.append(PythonToken("DEDENT", "", self.lineno, self.column))
                pass
        self.is_newline = is_newline
        self.rv.append(t)

    # The function names below begin with 't_'.
    # This indicates to GenericScanner that these routines
    # form the tokens. GenericScanner introspects on the
    # method names of this class and the docstrings to come
    # up with both the names of the tokens and the regular expressions
    # that make up those tokens

    def t_paren(self, s):
        r"[(){}[\]]"
        self.add_token(BRACKET2NAME[s], s)

    def t_symbol(self, s):
        r"[@:,.`]"
        self.add_token(SYMBOL2NAME[s], s)

    def t_endmarker(self, s):
        """"""
        self.add_token("ENDMARKER", s)

    # These can a appear as unary operators. Some are also binary operators
    UNOP2NAME = {"+": "PLUS", "-": "MINUS", "~": "TILDE"}

    def t_op(self, s):
        r"\+=|-=|\*=|/=|%=|&=|\|=|^=|<<=|>>=|\*\*=|//=|//|==|<=|>=|<<|>>|[<>%^&+/=~-]"

        # Operators need to be further classified since the grammar requires this
        if s in ("<", ">", "==", ">=", "<=", "<>", "!="):
            self.add_token("COMP_OP", s)
        elif s in (
            "+=",
            "-=",
            "*=",
            "/=",
            "%=",
            "&=",
            "|=",
            "^=",
            "<<=",
            ">>=",
            "**=",
            "//=",
        ):
            self.add_token("AUGASSIGN", s)
        elif s in self.UNOP2NAME.keys():
            self.add_token(self.UNOP2NAME[s], s)
        elif s in ("|", "^", "&", "<<", ">>", "**", "/", "%", "//"):
            # These are  *ONLY* binary operators. Operators which are exclusively or
            # can be unary operators were handled previously
            self.add_token("BINOP", s)
        elif s == "=":
            self.add_token("EQUAL", s)
        else:
            print("Internal error: Unknown operator %s" % s)
            raise SystemExit

    def t_linesep(self, s):
        r";"
        self.add_token("SEMICOLON", s)

    def t_nl(self, s):
        r"\n"
        self.add_token("NEWLINE", s, is_newline=True)

    def t_name(self, s):
        r"[A-Za-z_][A-Za-z_0-9]*"
        if s in RESERVED_WORDS:
            self.add_token(s.upper(), s)
        else:
            self.add_token("NAME", s)

    # A way to handle the problem of having to match two different
    # tokens with a single regular expression.
    # We can't have two separate defs because then it would be indeterminate
    # whether we get two single stars or one double star.
    def t_star_star(self, s):
        r"\*\*?"
        token_name = "STARSTAR" if len(s) == 2 else "STAR"
        self.add_token(token_name, s)

    # CONSTANTS
    # ---------

    def t_string(self, s):
        r"([\"]{3}(.|[\n])*[\"]{3})|('{3}(.|[\n])*'{3})|('[^']*')|(\"[^\"]*\")"
        self.add_token("STRING", s)

    # numbers; int, float, and complex

    # Note we have to put longer matches earlier. Specifically radix notation and
    # fixed-point notation
    def t_number(self, s):
        r"(0x[0-9a-f]+|0b[01]+|0o[0-7]+|\d+\.\d|\d+)j?"
        self.add_token("NUMBER", s)

    # Ugh. Handle Python's indent/dedent mess.
    def handle_indent_dedent(self, s):
        indent = len(s)
        if indent > self.indents[-1]:
            self.add_token("INDENT", s)
            self.indents.append(indent)
        if indent == self.indents[-1]:
            self.is_newline = False
            pass
        else:
            # May need several levels of dedent
            while indent < self.indents[-1]:
                self.indents = self.indents[0:-1]
                self.add_token("DEDENT", s)
                pass
            pass
        return

    # Combine comment and whitespace because we want to
    # capture the space before a comment.
    def t_whitespace_or_comment(self, s):
        r"([ \t]*[#].*[^\x04][\n]?)|([ \t]+)"
        if "#" in s:
            # We have a comment
            matches = re.match(r"(\s+)(.*[\n]?)", s)
            if matches and self.is_newline:
                self.handle_indent_dedent(matches.group(1))
                s = matches.group(2)
            if s.endswith("\n"):
                self.add_token("COMMENT", s[:-1])
                self.add_token("NEWLINE", "\n")
            else:
                self.add_token("COMMENT", s)
        elif self.is_newline:
            self.handle_indent_dedent(s)
            pass
        return


if __name__ == "__main__":
    scan = Python2Scanner()

    def showit(expr):
        print(expr)
        tokens = scan.tokenize(expr + ENDMARKER)
        for t in tokens:
            print(t)
        print("-" * 30)
        return

    # showit("1 # hi")
    showit(
        """def foo():
    # comment
    return
"""
    )
#    showit("(10.5 + 2 / 30) // 3 >> 1")
#    showit("1 + 2")
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
#     showit("""
# for i in range(x):
#     while True:
#        break
# """)
