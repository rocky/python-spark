#!/usr/bin/env python
"""
SPARK unit test via parsing simple arithmetic expressions
"""
import unittest

from spark_parser import AST
from spark_parser.scanner import GenericScanner, GenericToken
from spark_parser.spark import GenericParser

class ExprScanner(GenericScanner):

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

    # Recognize white space, but we don't cerate a token for it.
    # This has the effect of stripping white space between tokens
    def t_whitespace(self, s):
        r' \s+ '
        pass

    # Recognize operators: +, -, *, and /
    def t_add_op(self, s):
        r'[+]'
        self.add_token('ADD_OP', s)

    def t_mult_op(self, s):
        r'[*]'
        self.add_token('MULT_OP', s)

    # Recognize integers
    def t_integer(self, s):
        r'\d+'
        self.add_token('INTEGER', s)

# Some kinds of SPARK parsing you might want to consider
# DEFAULT_DEBUG = {'rules': True, 'transition': True, 'reduce' : True}
# DEFAULT_DEBUG = {'rules': False, 'transition': False, 'reduce' : True}
DEFAULT_DEBUG = {'rules': False, 'transition': False, 'reduce': False}

class ExprParser(GenericParser):
    """A simple expression parser for numbers and arithmetic operators: +, , *, and /.

    Note: methods that begin p_ have docstrings that are grammar rules interpreted
    by SPARK.
    """

    def __init__(self, start='expr', debug=DEFAULT_DEBUG):
        GenericParser.__init__(self, start, debug)

    def p_expr_add_term(self, args):
        ' expr ::= expr ADD_OP term '
        return AST('add', [args[0], args[2]])

    def p_expr2term(self, args):
        ' expr ::= term '
        return AST('single', [args[0]])

    def p_term_mult_factor(self, args):
        ' term ::= term MULT_OP factor '
        return AST('multiply', [args[0], args[2]])

    def p_term2factor(self, args):
        ' term ::= factor '
        return AST('single', [args[0]])

    def p_factor2integer(self, args):
        ' factor ::= INTEGER '
        return AST('single', [args[0]])

def scan_expression(data):
    """
    Tokenize *filename* into integers, numbers, and operators
    """
    scanner = ExprScanner()
    return scanner.tokenize(data)

def parse_expression(tokens):
    parser = ExprParser()
    return parser.parse(tokens)

class TestSpark(unittest.TestCase):

    def test_exprs(self):

        # Build up some AST trees to use in tetsting
        test_factor_to_integer1 = AST('single', [GenericToken('INTEGER', '1')])
        test_factor_to_integer2 = AST('single', [GenericToken('INTEGER', '2')])
        test_factor_to_integer3 = AST('single', [GenericToken('INTEGER', '3')])

        test_term_to_factor1 = AST('single', [test_factor_to_integer1])
        test_term_to_factor2 = AST('single', [test_factor_to_integer2])

        test_expr_to_term1 = AST('single', [test_term_to_factor1])

        test_expr3 = AST('add', [test_expr_to_term1, test_term_to_factor2])

        test_term6 = AST('multiply', [test_term_to_factor2, test_factor_to_integer3])
        test_expr7 = AST('add', [test_expr_to_term1, test_term6])

        for data, expect in [
                ['1', test_expr_to_term1],
                ['1+2', test_expr3],
                ['1+2*3', test_expr7]]:
            # print(data)
            tokens = scan_expression(data)
            # print(tokens)
            tree = parse_expression(tokens)

            # from trepan.api import debug; debug()
            self.assertEqual(tree, expect)
            pass
        return

if __name__ == '__main__':
    unittest.main()
