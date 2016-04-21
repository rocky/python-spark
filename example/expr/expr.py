#!/usr/bin/env python
"""
SPARK example to parse simple arithmetic expressions
"""
import re, sys
from spark import AST, GenericParser

######## The below can go into a generic util package

def _namelist(instance):
    namelist, namedict, classlist = [], {}, [instance.__class__]
    for c in classlist:
        for b in c.__bases__:
            classlist.append(b)
        for name in list(c.__dict__.keys()):
            if name not in namedict:
                namelist.append(name)
                namedict[name] = 1
    return namelist

class Token:
    def __init__(self, type, attr=' '):
		self.type = type
		self.attr = attr

    def __cmp__(self, o):
		return cmp(self.type, o)

    def __repr__(self):
		return self.attr or self.type

class GenericScanner:
    """A class which can be used subclass off of to make
    specific sets of scanners.
    """
    def __init__(self):
        pattern = self.reflect()
        self.re = re.compile(pattern, re.VERBOSE)

        self.index2func = {}
        for name, number in self.re.groupindex.items():
            self.index2func[number-1] = getattr(self, 't_' + name)

    def makeRE(self, name):
        doc = getattr(self, name).__doc__
        rv = '(?P<%s>%s)' % (name[2:], doc)
        return rv

    def reflect(self):
        rv = []
        for name in list(_namelist(self)):
            if name[:2] == 't_' and name != 't_default':
                rv.append(self.makeRE(name))
        rv.append(self.makeRE('t_default'))
        return '|'.join(rv)

    def error(self, s, pos):
        print("Lexical error at position %s" % pos)
        raise SystemExit

    def tokenize(self, s):
        pos = 0
        n = len(s)
        while pos < n:
            m = self.re.match(s, pos)
            if m is None:
                self.error(s, pos)

            groups = m.groups()
            for i in range(len(groups)):
                if groups[i] and self.index2func.has_key(i):
                    self.index2func[i](groups[i])
            pos = m.end()

    def t_default(self, s):
        r'( . | \n )+'
        pass

######## End of generic part

class ExprScanner(GenericScanner):

    def __init__(self):
        GenericScanner.__init__(self)

    def tokenize(self, input):
        self.rv = []
        GenericScanner.tokenize(self, input)
        return self.rv

    # The function names below begin with 't_'.
    # This indicates to GenericScanner that these routines
    # form the tokens. GenericScanner introspects on the
    # method names of this class and the docstrings to come
    # up with both the names of the tokens and the regular expressions
    # that make up those tokens

    # Recognize white space, but we don't cerate a token for it.
    # This has the effect of stripping white space between tokens
    def t_whitespace(self, s):
        r' \s+ '
        pass

    # Recognize operators: +, -, *, and /
    def t_op(self, s):
        r'[+-/*]'
        t = Token(type='op', attr=s)
        self.rv.append(t)

    # Recognize integers
    def t_integer(self, s):
        r'\d+'
        t = Token(type='integer', attr=s)
        self.rv.append(t)

class ExprParser(GenericParser):
    """A simple expression parser for numbers and arithmetic operators: +, *
    """

    def __init__(self, start='expr'):
        debug = {'rules': True, 'transition': True, 'reduce' : True}
        GenericParser.__init__(self, start, debug)


    def p_expr_1(self, args):
        ' expr ::= expr + term '
        return AST(type=args[1], left=args[0], right=args[2])

    def p_expr_2(self, args):
        ' expr ::= term '
        return args[0]

    def p_term_1(self, args):
        ' term ::= term * factor '
        return AST(type=args[1], left=args[0], right=args[2])

    def p_term_2(self, args):
        ' term ::= factor '
        return args[0]

    def p_factor_1(self, args):
        ' factor ::= number '
        return AST(type=args[0])

def scan_expression(filename):
    """
    Tokenize *filename* into integers, numbers, and operators
    """
    input = open(filename).read()
    scanner = ExprScanner()
    return scanner.tokenize(input)

def parse_expression(tokens):
    parser = ExprParser()
    return parser.parse(tokens)

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        tokens = scan_expression('expr1.txt')
    else:
        tokens = scan_expression(sys.argv[1])
    print(tokens)
    # Not working yet
    # print(parse_expression(tokens))
