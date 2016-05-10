#  Copyright (c) 2016 Rocky Bernstein
"""
More complex expression parsing
"""

from __future__ import print_function

import sys
from spark_parser.ast import AST

from scanner import ExprScanner

from spark_parser import GenericASTBuilder, DEFAULT_DEBUG

class ParserError(Exception):
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return "Syntax error at or near `%r'\n" % \
               (self.token)

class ExprParser(GenericASTBuilder):
    """A more complete expression Parser.

    Note: function parse() comes from GenericASTBuilder
    """

    def __init__(self, debug=DEFAULT_DEBUG):
        super().__init__(AST, 'expr', debug=debug)
        self.debug = debug

    def error(self, token):
            raise ParserError(token)

    def nonterminal(self, nt, args):
        collect = ()

        if nt in collect and len(args) > 1:
            #
            #  Collect iterated thingies together.
            #
            rv = args[0]
            rv.append(args[1])
        else:
            rv = GenericASTBuilder.nonterminal(self, nt, args)
        return rv

    ##########################################################
    # Python 2 grammar rules. Grammar rule functions
    # start with the name p_ and are collected automatically
    ##########################################################
    def p_expr(self, args):
        '''
        expr       ::= expr BITOP shift_expr
        expr       ::= shift_expr
        shift_expr ::= shift_expr ARITH_OP arith_expr
        shift_expr ::= arith_expr
        arith_expr ::= arith_expr ADD_OP term
        arith_expr ::= term
        term       ::= term MULT_OP factor
        term       ::= factor
        factor     ::= UNARY_OP factor
        factor     ::= atom
        atom       ::= NUMBER
        atom       ::= LPAREN expr RPAREN
        NUMBER     ::= INTEGER
        # Add this when we want to handle type checking.
        # NUMBER     ::= INTEGER DOT INTEGER
        '''

def parse_python(python_str, out=sys.stdout,
                 show_tokens=False, parser_debug=DEFAULT_DEBUG):
    assert isinstance(python_str, str)
    tokens = ExprScanner().tokenize(python_str)
    for t in tokens:
        print(t)

    # For heavy grammar debugging
    # parser_debug = {'rules': True, 'transition': True, 'reduce': True,
    #                 'errorstack': True}
    parser_debug = {'rules': False, 'transition': False, 'reduce': True,
                    'errorstack': True}
    return ExprParser(parser_debug).parse(tokens)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        expression = "(1 + 3)/2"
    else:
        expression = " ".join(sys.argv[1:])
    parse_python(expression, show_tokens=True)
