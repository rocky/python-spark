#  Copyright (c) 2016 Rocky Bernstein
"""
More complex expression parsing
"""

from __future__ import print_function

import sys
from spark_parser.ast import AST

from py2_scan import Python2Scanner

from spark_parser import GenericASTBuilder #, DEFAULT_DEBUG

DEFAULT_DEBUG = {'rules': True, 'transition': False, 'reduce' : True,
                     'errorstack': 'full' }
class ParserError(Exception):
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return "Syntax error at or near `%r'\n" % \
               (self.token)

class PythonParser(GenericASTBuilder):
    """A more complete spark example: a Python 2 Parser.

    Note: function parse() comes from GenericASTBuilder
    """

    def __init__(self, debug=DEFAULT_DEBUG):
        super().__init__(AST, 'file_input', debug=debug)
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
    def p_python_grammar(self, args):
        '''
        single_input ::= NEWLINE
        single_input ::= simple_stmt
        single_input ::= compound_stmt NEWLINE

        file_input ::= newline_or_stmts
        newline_or_stmts ::= newline_or_stmts newline_or_stmt
        newline_or_stmts ::=
        newline_or_stmt ::= sep
        newline_or_stmt ::= stmt

        stmts      ::= stmts stmt
        stmts      ::= stmt sep
        stmts      ::=

        decorator ::= AT dotted_name arg_list_opt NEWLINE
        arglist_opt ::= LPAREN [arglist] RPAREN
        arglist_opt ::=

        decorators ::= decorators decorator
        decorators ::= decorator

        decorated ::= decorators classdef_or_funcdef
        classdef_or_funcdef ::= classdef
        classdef_or_funcdef ::= funcdef

        funcdef ::= DEF NAME parameters COLON suite

        parameters ::= LPAREN varargslist_opt RPAREN

        # FIXME: go over this
        varargslist_opt ::=  varargslist
        varargslist_opt ::=

        varargslist ::= fpdefs star_names
        varargslist ::= fpdefs kwvals

        fpdefs ::= fpdefs fpdef eq_test_op
        star_names ::= star_names STAR NAME star_star_opt
        star_names ::= star_names star_star_opt

        star_names ::= star_names STAR NAME star_star_opt
        star_names ::= star_names star_star_opt

        eq_test_opt ::= EQUAL test COMMA
        eq_test_opt ::=

        star_star_opt ::= COMMA STAR_STAR NAME
        star_star_opt ::=

        fpdef ::= NAME
        fpdef ::= LPAREN fplist_comma_opt RPAREN

        # FIXME: go over
        fplist_comma_opt ::= fplist comma_opt

        fplist ::= fplist COMMA fpdef
        fplist ::= fpdef

        comma_opt ::= COMMA
        comma_opt ::=

        stmt ::= simple_stmt
        stmt ::= compound_stmt

        simple_stmt ::= small_stmt

        small_stmt ::= expr_stmt
        small_stmt ::= print_stmt
        small_stmt ::= del_stmt
        small_stmt ::= pass_stmt
        small_stmt ::= flow_stmt
        small_stmt ::= import_stmt
        small_stmt ::= global_stmt
        small_stmt ::= exec_stmt
        small_stmt ::= assert_stmt

        expr_stmt ::= testlist augassign_or_equal

        augassing_or_equal ::=  augassign_something
        augassing_or_equal ::=  EQUAL equal_somethings

        augassign_something ::= AUGASSIGN yield_expr
        augassign_something ::= AUGASSIGN testlist

        equal_somethings ::= equal_somethings yield_expr_or_testlist
        equal_somethings ::=

        yield_expr_or_testlist ::= yield_expr_or_testlist yield_expr
        yield_expr_or_testlist ::= yield_expr_or_testlist testlist
        yield_expr_or_testlist ::=

        print_stmt ::= PRINT test_params_or_redirect
        test_params_or_redirect ::= test comma_test_opt comma_opt

        # FIXME: go over Not quite right as there is one or more..
        test_params_or_redirect ::= REDIRECT test comma_test_opt  comma_opt

        comma_test_opt ::= COMMA test
        comma_test_opt ::=

        del_stmt ::= DEL exprlist
        pass_stmt ::= PASS

        flow_stmt ::= break_stmt
        flow_stmt ::= continue_stmt
        flow_stmt ::= return_stmt
        flow_stmt ::= raise_stmt
        flow_stmt ::= yield_stmt

        break_stmt ::= BREAK

        continue_stmt ::= CONTINUE

        return_stmt ::= RETURN testlist_opt

        testlist_opt ::= testlist
        testlsit_opt ::=

        yield_stmt ::= yield_expr

        raise_stmt ::= RAISE test_opt3

        test_opt3 ::= test COMMA test COMMA test
        test_opt3 ::= test COMMA test
        test_opt3 ::= test

        import_stmt ::= import_name
        import_stmt ::= import_from

        import_name ::= IMPORT dotted_as_names

        import_from ::= FROM dots_dotted_name_or_dots import_list

        import_as_name ::= NAME
        import_as_name ::= NAME AS NAME

        dotted_as_name ::= dotted_name
        dotted_as_name ::= dotted_name AS NAME

        dots_dotted_name_or_dots ::= dots dotted_name
        dots_dotted_name_or_dots ::= DOT dots
        dots ::= dots DOT
        dots ::=

        import_list ::= IMPORT STAR
        import_list ::= IMPORT LPAREN import_as_names RPAREN
        import_list ::= IMPORT import_as_names

        import_as_names ::= import_as_name comma_import_as_names comma_opt
        import_as_names ::= import_as_name

        comma_dotted_as_names ::= comma_dotted_as_names dotted_as_name
        comma_dotted_as_names ::= dotted_as_name

        dotted_as_names ::= dotted_as_name comma_dotted_as_names
        comma_dotted_as_names ::= comma_dotted_as_names COMMA dotted_as_name
        comma_dotted_as_names ::=

        dotted_name ::= NAME dot_names
        dot_names ::= dot_names DOT NAME
        dot_names ::=

        global_stmt ::= GLOBAL NAME comma_names
        comma_names ::= comma_names COMMA NAME
        comma_names ::=

        exec_stmt ::= EXEC expr
        exec_stmt ::= EXEC expr IN test
        exec_stmt ::= EXEC expr IN test COMMA test

        assert_stmt ::= ASSERT test
        assert_stmt ::= ASSERT test COMMA test

        # Fill compound statement
        # ....
        exprlist ::= expr comma_exprs comma_opt
        comma_exprs ::= comma_expr_star COMMA expr
        comma_exprs ::=


        testlist_opt_comma ::= testlist COMMA
        testlist_opt_comma ::= testlist

        testlist ::= testlist COMMA test
        testlist ::= test

        test ::= or_test IF or_test ELSE test
        test ::= or_test
        test ::= lambdef

        or_test ::= and_test or_and_tests

        or_and_tests ::= or_and_tests or_and_test
        or_and_tests ::=

        or_and_test ::= OR and_test

        and_test ::= not_test and_not_tests

        and_not_tests ::= and_not_tests AND not_test
        and_not_tests ::=

        not_test ::= NOT not_test
        not_test ::= comparison

        not_test ::=
             'not' not_test | comparison

        comparison ::= expr comp_op_exprs

        comp_op_exprs ::= comp_op_exprs comp_op expr
        comp_op_exprs ::=

        comp_op ::= COMP_OP
        comp_op ::= IN

        expr       ::= expr BINOP expr
        expr       ::= LPAREN expr RPAREN
        expr       ::= atom

        atom       ::= NUMBER
        atom       ::= NAME
        atom       ::= strings

        strings   ::= strings STRING
        strings   ::= STRING

        sep       ::= NEWLINE
        sep       ::= SEMICOLON
        '''

def parse_python2(python_stmts,
                  show_tokens=False, parser_debug=DEFAULT_DEBUG):
    assert isinstance(python_stmts, str)
    tokens = Python2Scanner().tokenize(python_stmts)
    if show_tokens:
        for t in tokens:
            print(t)

    # For heavy grammar debugging
    # parser_debug = {'rules': True, 'transition': True, 'reduce': True,
    #                 'errorstack': True}
    # parser_debug = {'rules': True, 'transition': True, 'reduce': True,
    #                'errorstack': True}
    return PythonParser(parser_debug).parse(tokens)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        for python2_stmts in (
                "from os import path",
                "from os import path as shmath",
                ):
            print(python2_stmts)
            print('-' * 30)
            ast = parse_python2(python2_stmts, show_tokens=True)
            print(ast)
            print('=' * 30)
    else:
        python2_stmts = " ".join(sys.argv[1:])
        parse_python2(python2_stmts, show_tokens=True)
