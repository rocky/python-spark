#  Copyright (c) 2016-2018 Rocky Bernstein
"""
More complex expression parsing
"""

from __future__ import print_function

import sys
from spark_parser.ast import AST

from scanner import ExprScanner

from spark_parser import GenericASTBuilder, DEFAULT_DEBUG

class ExprParser(GenericASTBuilder):
    """A more complete expression Parser.

    Note: function parse() comes from GenericASTBuilder
    """

    def __init__(self, debug=DEFAULT_DEBUG):
        super(ExprParser, self).__init__(AST, 'expr', debug=debug)
        self.debug = debug

    def nonterminal(self, nt, args):
        has_len = hasattr(args, '__len__')
        if (has_len and len(args) == 1 and
            hasattr(args[0], '__len__') and len(args[0]) == 1):
            # Remove singleton derivations
            rv = GenericASTBuilder.nonterminal(self, nt, args[0])
            del args[0] # save memory
        else:
            rv = GenericASTBuilder.nonterminal(self, nt, args)
        return rv

    ##########################################################
    # Expression grammar rules. Grammar rule functions
    # start with the name p_ and are collected automatically
    ##########################################################
    def p_expr(self, args):
        '''
        expr       ::= expr BOOL_OP term
        expr       ::= expr SHIFT_OP term
        expr       ::= term
        term       ::= term MULT_OP factor
        factor     ::= term
        term       ::= term ADD_OP atom
        term       ::= atom
        atom       ::= NUMBER
        atom       ::= LPAREN expr RPAREN
        '''

def parse_expr(python_str, out=sys.stdout,
               show_tokens=False, parser_debug=DEFAULT_DEBUG):
    assert isinstance(python_str, str)
    tokens = ExprScanner().tokenize(python_str)
    if show_tokens:
        for t in tokens:
            print(t)

    # Some kinds of parsing debugging options you might want to consider...
    #
    # The most verbose debugging::
    # parser_debug = {'rules': True,
    #                 'transition': True,
    #                 'reduce' : True,
    #                 'dups': True
    #                 }
    #
    # The kind of debugging I generally use:
    # parser_debug = {'rules': False,
    #                 'transition': False,
    #                 'reduce' : True,   # show grammar rule reductions
    #                 'dups': True
    # }

    parser = ExprParser(parser_debug)
    parser.check_grammar()
    return parser.parse(tokens)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        expression = "(1 + 3)/2"
    else:
        expression = " ".join(sys.argv[1:])
    ast = parse_expr(expression, show_tokens=True)
    print(ast)
