#  Copyright (c) 2016 Rocky Bernstein
"""
More complex expression parsing
"""

from __future__ import print_function

import sys
from spark_parser.ast import AST

from scanner import LocationScanner

from spark_parser import GenericASTBuilder, DEFAULT_DEBUG

class LocationParser(GenericASTBuilder):
    """A more complete expression Parser.

    Note: function parse() comes from GenericASTBuilder
    """

    def __init__(self, debug=DEFAULT_DEBUG):
        super(LocationParser, self).__init__(AST, 'start', debug=debug)
        self.debug = debug

    def nonterminal(self, nt, args):
        has_len = hasattr(args, '__len__')

        collect = ('tokens',)
        if nt in collect:
            #
            #  Collect iterated thingies together.
            #
            rv = args[0]
            for arg in args[1:]:
                rv.append(arg)

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
    def p_location(self, args):
        '''
        start       ::= opt_space location_if opt_space
        opt_space   ::= SPACE?

        location_if ::= location
        location_if ::= location SPACE IF tokens

        # Note no space is allowed between FILENAME and NUMBER
        location    ::= FILENAME COLON NUMBER
        location    ::= FUNCNAME

        # In the below, the second FILENAME is really the word
        # "line". We ferret this out in a reduction rule though.
        location    ::= FILENAME SPACE FILENAME SPACE NUMBER

        # If just a number is given, the the filename is implied
        location    ::=  NUMBER
        location    ::=  METHOD

        # For tokens we accept anything. Were really just
        # going to use the underlying string from the part
        # after "if".  So below we all of the possible tokens

        tokens      ::= token+
        token       ::= FILENAME
        token       ::= FUNCNAME
        token       ::= COLON
        token       ::= NUMBER
        token       ::= SPACE
        '''

    def add_custom_rules(self, tokens, orig_customize):
        self.check_reduce['location'] = 'tokens'

    def reduce_is_invalid(self, rule, ast, tokens, first, last):
        if rule == ('location', ('FILENAME', 'SPACE', 'FILENAME', 'SPACE', 'NUMBER')):
            # In this rule the 2nd filename should be 'line'. if not, the rule
            # is invalid
            return tokens[first+2].value != 'line'
        return False


def parse_location(python_str, out=sys.stdout,
                   show_tokens=False, parser_debug=DEFAULT_DEBUG):
    assert isinstance(python_str, str)
    tokens = LocationScanner().tokenize(python_str)
    if show_tokens:
        for t in tokens:
            print(t)

    # For heavy grammar debugging
    # parser_debug = {'rules': True, 'transition': True, 'reduce': True,
    #                 'errorstack': True, 'dups': True}
    parser_debug = {'rules': False, 'transition': False, 'reduce': True,
                    'errorstack': True, 'dups': True}
    parser = LocationParser(parser_debug)
    parser.checkGrammar()
    parser.add_custom_rules(tokens, {})
    return parser.parse(tokens)

if __name__ == '__main__':
    lines = """
    /tmp/foo.py:12
    /tmp/foo.py line 12
    12
    ../foo.py:5
    gcd()
    foo.py line 5 if x > 1
    """.splitlines()
    for line in lines:
        if not line.strip():
            continue
        print("=" * 30)
        print(line)
        print("+" * 30)
        ast = parse_location(line, show_tokens=True)
        print(ast)
