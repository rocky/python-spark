#  Copyright (c) 2016-2017 Rocky Bernstein
"""
More complex expression parsing
"""

# from __future__ import print_function

import sys
from spark_parser.ast import AST

from py2_scan import Python2Scanner, ENDMARKER

from spark_parser import GenericASTBuilder

DEFAULT_DEBUG = {'rules': False, 'transition': False, 'reduce' : False,
                 'errorstack': 'full', 'context': True, 'dups': True}

class PythonParser(GenericASTBuilder):
    """A more complete spark example: a Python 2 Parser.

    Note: function parse() comes from GenericASTBuilder
    """

    def __init__(self, start='file_input', debug=DEFAULT_DEBUG):
        super(PythonParser, self).__init__(AST, start, debug=debug)
        self.start = start
        self.debug = debug

    def debug_reduce(self, rule, tokens, parent, i):
        """Customized format and print for our kind of tokens
        which gets called in debugging grammar reduce rules
        """
        prefix = '           '
        if parent and tokens:
            p_token = tokens[parent]
            if hasattr(p_token, 'line'):
                prefix = 'L.%3d.%03d: ' % (p_token.line, p_token.column)
                pass
            pass
        print("%s%s ::= %s" % (prefix, rule[0], ' '.join(rule[1])))

    def nonterminal(self, nt, args):
        # Put left-recursive list non-terminals:
        # x ::= x y
        # x ::=
        collect = ('stmts', 'comments', 'dot_names', 'dots',
                   'comp_op_exprs', 'newline_or_stmts',
                   'comma_names', 'comma_fpdef_opt_eqtests',
                   )
        # nonterminal with a (reserved) single word derivation
        no_skip = ('pass_stmt', 'continue_stmt', 'break_stmt', 'return_stmt')

        has_len = hasattr(args, '__len__')

        if nt in collect and len(args) > 1:
            #
            #  Collect iterated thingies together.
            #
            rv = args[0]
            for arg in args[1:]:
                rv.append(arg)
        elif (has_len and len(args) == 1 and
              hasattr(args[0], '__len__') and args[0] not in no_skip and
              len(args[0]) == 1):
            # Remove singleton derivations
            rv = GenericASTBuilder.nonterminal(self, nt, args[0])
            del args[0] # save memory
        elif (has_len and len(args) == 2 and
              hasattr(args[1], '__len__') and len(args[1]) == 0):
            # Remove trailing epsilon rules, but only when there
            # are two items.
            if hasattr(args[0], '__len__') and len(args[0]) == 1:
                # Remove singleton derivation
                rv = args[0]
            else:
                rv = GenericASTBuilder.nonterminal(self, nt, args[:1])
            del args[1] # save memory
        else:
            rv = GenericASTBuilder.nonterminal(self, nt, args)
        return rv

    ##########################################################
    # Python 2 grammar rules. Grammar rule functions
    # start with the name p_ and are collected automatically
    ##########################################################
    def p_python_grammar(self, args):
        '''
        ### Note: comment rules that start ## are rules from python26.gr
        ##  We use them to assist checking translation to a SPARK-format grammar.

        single_input ::= NEWLINE
        single_input ::= simple_stmt
        single_input ::= compound_stmt NEWLINE

        file_input ::= newline_or_stmts ENDMARKER
        newline_or_stmts ::= newline_or_stmt*

        # Grammar uses NEWLINE instead of 'sep', but ; does separate statements.
        # The grammar is vague on how NEWLINE, INDENT, and DEDENT are computed.

        newline_or_stmt ::= sep
        newline_or_stmt ::= stmt_plus
        newline_or_stmt ::= comment sep

        stmts      ::= stmt*
        stmts      ::= stmt sep

        stmt_plus  ::= stmt+

        eval_input ::= testlist newlines ENDMARKER

        newlines ::= NEWLINE+

        decorator ::= AT dotted_name arglist_opt NEWLINE

        arglist_opt ::= arglist?

        ## arglist ::= (argument ',')*
        ## (argument [','] | '*' test (',' argument)* [',' '**' test] | '**' test)
        arglist ::= argument_commas arglist2

        argument_commas ::= argument_commas argument_comma
        argument_commas ::=
        argument_comma  ::= argument COMMA

        ## (argument [','] | '*' test (',' argument)* [',' '**' test] | '**' test)
        arglist2 ::= argument comma_opt
        arglist2 ::= START test comma_arguments comma_starstar_test_opt
        arglist2 ::= STARSTAR test

        comma_arguments ::= comma_argument*
        comma_argument ::= COMMA argument

        comma_starstar_test_opt ::= COMMA STARSTAR test
        comma_starstar_test_opt ::=

        ## Really [keyword '='] test
        ## argument ::= test [gen_for] | test '=' test
        argument ::= test gen_for_opt
        argument ::= test EQUAL test

        ## list_iter ::= list_for | list_if
        list_iter ::= list_for
        list_iter ::= list_if

        ## list_for ::= 'for' exprlist 'in' testlist_safe [list_iter]
        list_for ::= FOR exprlist IN testlist_safe list_iter_opt

        list_iter_opt ::= list_iter?

        ## list_if ::= 'if' old_test [list_iter]
        list_if ::= IF old_test list_iter_opt

        gen_for_opt ::= gen_for?

        ## gen_iter ::= gen_for | gen_if
        gen_iter ::= gen_for
        gen_iter ::= gen_if

        ## gen_for ::= 'for' exprlist 'in' or_test [gen_iter]
        gen_for ::= FOR exprlist IN or_test gen_iter_opt

        gen_iter_opt ::= gen_iter?

        ## gen_if ::= 'if' old_test [gen_iter]
        gen_if ::= IF old_test gen_iter_opt

        ## testlist1 ::= test (',' test)*
        testlist1 ::= test comma_tests

        decorators ::= decorator+

        decorated ::= decorators classdef_or_funcdef
        classdef_or_funcdef ::= classdef
        classdef_or_funcdef ::= funcdef

        funcdef ::= DEF NAME parameters COLON suite

        parameters ::= LPAREN varargslist_opt RPAREN

        varargslist_opt ::=  varargslist?

        # FILL IN
        ## varargslist ::= fpdef ['=' test] ',')* ('*' NAME [',' '**' NAME] | '**' NAME)

        ## varargslist ::= fpdef ['=' test] (',' fpdef ['=' test])* [',']
        varargslist ::= fpdef eq_test_opt comma_fpdef_opt_eqtests comma_opt

        ## (',' fpdef ['=' test])*
        comma_fpdef_opt_eqtests ::= comma_fpdef_opt_eqtests COMMA fpdef eq_test_opt
        comma_fpdef_opt_eqtests ::=

        star_names ::= star_names STAR NAME star_star_opt
        star_names ::= star_names star_star_opt
        star_names ::=

        eq_tests ::= eq_tests eq_test
        eq_tests ::=

        eq_test_opt ::= eq_test?

        eq_test ::= EQUAL test

        star_star_opt ::= COMMA STAR_STAR NAME
        star_star_opt ::=

        ## fpdef ::= NAME | '(' fplist ')'
        fpdef ::= NAME
        fpdef ::= LPAREN fplist RPAREN

        ## fplist ::= fpdef (',' fpdef)* [',']
        fplist ::= fpdef fplist1 comma_opt

        ## (',' fpdef)* [',']
        fplist1 ::= fplist COMMA fpdef
        fplist1 ::=

        comma_opt ::= COMMA?

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

        ##  expr_stmt ::= testlist (augassign (yield_expr|testlist)
        ##          | ('=' (yield_expr|testlist))*)
        expr_stmt ::= testlist AUGASSIGN yield_expr_or_testlist
        expr_stmt ::= testlist EQUAL yield_expr_or_testlists

        yield_expr_or_testlists ::= yield_expr_or_testlists yield_expr_or_testlist
        yield_expr_or_testlists ::= yield_expr_or_testlist

        yield_expr_or_testlist ::= yield_expr
        yield_expr_or_testlist ::= testlist

        ## yield_expr ::= 'yield' [testlist]
        yield_expr ::= YIELD testlist_opt

        print_stmt ::= PRINT test_params_or_redirect
        test_params_or_redirect ::= test comma_test_opt comma_opt

        # FIXME: go over Not quite right as there is one or more..
        test_params_or_redirect ::= REDIRECT test comma_test_opt comma_opt

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

        # return_stmt ::= 'return' [testlist]
        return_stmt ::= RETURN testlist_opt

        testlist_opt ::= testlist?

        yield_stmt ::= yield_expr

        raise_stmt ::= RAISE test_opt3

        test_opt3 ::= test COMMA test COMMA test
        test_opt3 ::= test COMMA test
        test_opt3 ::= test

        global_stmt ::= GLOBAL NAME comma_names
        comma_names ::= comma_name*

        comma_name  ::= COMMA NAME

        exec_stmt ::= EXEC expr
        exec_stmt ::= EXEC expr IN test
        exec_stmt ::= EXEC expr IN test COMMA test

        assert_stmt ::= ASSERT test
        assert_stmt ::= ASSERT test COMMA test

        test_opt ::= test?

        ## exprlist ::= expr (',' expr)* [',']
        exprlist ::= expr comma_exprs comma_opt

        ## (',' expr)*
        comma_exprs ::= comma_exprs COMMA expr
        comma_exprs ::=

        # testlist ::= test (',' test)* [',']
        testlist  ::= test comma_tests comma_opt

        # (',' test)*
        comma_tests ::= comma_tests COMMA test
        comma_tests ::=

        ## Backward compatibility cruft to support:
        ## [ x for x in lambda : True, lambda : False if x() ]
        ## even while also allowing:
        ## lambda x : 5 if x else 2
        ## (But not a mix of the two)

        ## testlist_safe ::= old_test [(',' old_test)+ [',']]
        testlist_safe ::= old_test testlist_safe1_opt

        testlist_safe1_opt ::= comma_old_tests comma_opt
        testlist_safe1_opt ::=

        ## (',' old_test)+
        comma_old_tests ::= comma_old_tests comma_old_test
        comma_old_tests ::= comma_old_test

        comma_old_test ::= COMMA old_test

        ## old_test ::= or_test | old_lambdef
        old_test ::= or_test
        old_test ::= old_lambdef

        ## old_lambdef ::= 'lambda' [varargslist] ':' old_test
        old_lambdef ::= LAMBDA varargslist_opt COLON old_test

        test ::= or_test IF or_test ELSE test
        test ::= or_test
        test ::= lambdef

        or_test ::= and_test or_and_tests

        ## ('or' and_test)*
        or_and_tests ::= or_and_test*

        or_and_test ::= OR and_test

        ## and_test ::= not_test ('and' not_test)*
        and_test ::= not_test and_not_tests

        ## ('and' not_test)*
        and_not_tests ::= and_not_tests AND not_test
        and_not_tests ::=

        ## not_test ::= 'not' not_test | comparison
        not_test ::= NOT not_test
        not_test ::= comparison

        ## comparison ::= expr (comp_op expr)*
        comparison ::= expr comp_op_exprs

        ## (comp_op expr)*
        comp_op_exprs ::= comp_op_exprs comp_op expr
        comp_op_exprs ::=

        comp_op    ::= COMP_OP
        comp_op    ::= IN
        comp_op    ::= IS
        comp_op    ::= IS NOT

        # Condensation of this
        ##  expr ::= xor_expr ('|' xor_expr)*
        ##  xor_expr ::= and_expr ('^' and_expr)*
        ##  and_expr ::= shift_expr ('&' shift_expr)*
        ##  shift_expr ::= arith_expr (('<<'|'>>') arith_expr)*
        ##  arith_expr ::= term (('+'|'-') term)*
        ##  term ::= factor (('*'|'/'|'%'|'//') factor)*
        ## We don't care about operator precidence

        expr              ::= factor binop_arith_exprs
        binop_arith_exprs ::= binop_arith_exprs binop factor
        binop_arith_exprs ::=

        binop             ::= BINOP
        binop             ::= PLUS
        binop             ::= MINUS
        binop             ::= STAR

        ## factor  ::= ('+'|'-'|'~') factor | power
        factor    ::= op_factor factor
        factor    ::= power

        op_factor ::= PLUS
        op_factor ::= MINUS
        op_factor ::= TILDE

        power      ::= atom trailers starstar_factor_opt

        ## atom ::= ('(' [yield_expr|testlist_gexp] ')' | '[' [listmaker] ']'
        ##            | '{' [dictmaker] '}' | '`' testlist1 '`'
        ##            | NAME | NUMBER | STRING+)
        atom       ::= LPAREN yield_expr_or_testlist_gexp_opt RPAREN
        atom       ::= LBRACKET listmaker_opt RBRACKET
        atom       ::= LBRACE dictmaker_opt RBRACE
        atom       ::= BACKTICK testlist1 BACKTICK
        atom       ::= NUMBER
        atom       ::= NAME
        atom       ::= strings

        dictmaker_opt ::= dictmaker?

        ## [yield_expr|testlist_gexp]
        yield_expr_or_testlist_gexp_opt ::= yield_expr
        yield_expr_or_testlist_gexp_opt ::= testlist_gexp
        yield_expr_or_testlist_gexp_opt ::=

        listmaker_opt ::= listmaker?

        ## listmaker ::= test ( list_for | (',' test)* [','] )

        listmaker ::=  test  list_for_or_comma_tests_comma_opt
        list_for_or_comma_tests_comma_opt ::= list_for
        list_for_or_comma_tests_comma_opt ::= comma_tests comma_opt

        ## testlist_gexp ::= test ( gen_for | (',' test)* [','] )
        testlist_gexp ::= test gen_for_or_comma_tests_comma_opt

        gen_for_or_comma_tests_comma_opt ::= gen_for
        gen_for_or_comma_tests_comma_opt ::= comma_tests comma_opt

        lambdef ::= LAMBDA varargslist_opt COLON test

        trailers   ::= trailer*

        ## trailer ::= '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
        trailer ::= LPAREN arglist_opt RPAREN
        trailer ::= LBRACKET subscriptlist RBRACKET
        trailer ::= DOT NAME

        ## subscriptlist ::= subscript (',' subscript)* [',']
        subscriptlist ::= subscript comma_subscripts comma_opt

        ## (',' subscript)*
        comma_subscripts ::= comma_subscripts comma_subscript
        comma_subscripts ::=

        ## ',' subscript
        comma_subscript ::= COMMA subscript

        ## subscript ::= '.' '.' '.' | test | [test] ':' [test] [sliceop]
        subscript ::= DOT DOT DOT
        subscript ::= test
        subscript ::= test_opt COLON test_opt sliceop_opt

        sliceop_opt ::= sliceop?

        ## sliceop ::= ':' [test]
        sliceop ::= COLON test_opt


        starstar_factor_opt ::= STARSTAR factor
        starstar_factor_opt ::=

        ## dictmaker ::= test ':' test (',' test ':' test)* [',']
        dictmaker ::= test COLON comma_test_colon_tests comma_opt

        ##  (',' test ':' test)*
        comma_test_colon_tests ::= comma_test_colon_tests comma_test_colon_test
        comma_test_colon_tests ::=

        ## (',' test ':' test)
        comma_test_colon_test ::= COMMA test COLON test

        classdef ::= CLASS NAME class_subclass_opt COLON suite

        class_subclass_opt ::= LPAREN testlist_opt RPAREN
        class_subclass_opt ::=


        strings   ::= STRING+

        sep       ::= comments
        sep       ::= NEWLINE
        sep       ::= SEMICOLON

        comments  ::= comment+

        comment ::= COMMENT
        comment ::= COMMENT NEWLINE
        '''

    # Import-related grammar
    def p_import(self, args):
        """
        ## import_stmt ::= import_name | import_from
        import_stmt ::= import_name
        import_stmt ::= import_from

        ## import_name ::= IMPORT dotted_as_names
        import_name ::= IMPORT dotted_as_names

        ##  import_from ::= ('from' ('.'* dotted_name | '.'+)
        ##                  'import' ('*' | '(' import_as_names ')' | import_as_names))
        import_from ::= FROM dots_dotted_name_or_dots import_list

        import_as_name ::= NAME
        import_as_name ::= NAME AS NAME

        dotted_as_name ::= dotted_name
        dotted_as_name ::= dotted_name AS NAME

        dots_dotted_name_or_dots ::= dots dotted_name
        dots_dotted_name_or_dots ::= DOT dots
        dots ::= DOT*

        ## 'import' ('*' | '(' import_as_names ')' | import_as_names))
        import_list ::= IMPORT STAR
        import_list ::= IMPORT LPAREN import_as_names RPAREN
        import_list ::= IMPORT import_as_names

        ## import_as_names ::= import_as_name ((',' import_as_name)+\) [',']
        # Note: we don't do the opt comma at the end
        import_as_names ::= import_as_name comma_import_as_names

        ##  (',' import_as_name)+
        comma_import_as_names ::= comma_import_as_names comma_import_as_name
        comma_import_as_names ::=

        ##  ',' import_as_name
        comma_import_as_name ::= COMMA import_as_name

        comma_dotted_as_names ::= dotted_as_name+

        dotted_as_names ::= dotted_as_name comma_dotted_as_names
        comma_dotted_as_names ::= comma_dotted_as_names COMMA dotted_as_name
        comma_dotted_as_names ::=

        dotted_name ::= NAME dot_names
        dot_names ::= dot_names DOT NAME
        dot_names ::=
        """

    def p_compund_stmt(self, args):
        """
        compound_stmt ::= if_stmt
        compound_stmt ::= while_stmt
        compound_stmt ::= for_stmt
        compound_stmt ::= try_stmt
        compound_stmt ::= with_stmt
        compound_stmt ::= funcdef
        compound_stmt ::= classdef
        compound_stmt ::= decorated

        if_stmt ::= IF test COLON suite elif_suites else_suite_opt
        if_stmt ::= IF test COLON NEWLINE suite elif_suites else_suite_opt

        elif_suites ::= elif_suites ELIF test COLON suite
        elif_suites ::=
        else_suite_opt ::= ELSE COLON suite
        else_suite_opt ::=

        ## while_stmt ::= 'while' test ':' suite ['else' ':' suite]
        while_stmt ::= WHILE test COLON suite else_suite_opt

        ## for_stmt ::= 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
        for_stmt ::= FOR exprlist IN testlist COLON suite else_colon_suite_opt

        ## ['else' ':' suite]
        else_colon_suite_opt ::= ELSE COLON suite
        else_colon_suite_opt ::=

        ## try_stmt ::= ('try' ':' suite
        ##      ((except_clause ':' suite)+
        ##       ['else' ':' suite]
        ##       ['finally' ':' suite] |
        ##      'finally' ':' suite))

        ## with_stmt ::= with' test [ with_var ] ':' suite
        with_stmt ::= WITH test with_var_opt COLON suite

        with_var_opt ::= with_var?

        ## with_var ::= 'as' expr
        with_var ::= AS expr

        suite ::= stmt_plus

        suite ::=  NEWLINE indent stmt_plus NEWLINE DEDENT
        suite ::=  NEWLINE indent stmt_plus DEDENT
        indent ::= INDENT comments
        indent ::= INDENT
        """


def parse_python2(python_stmts, start='file_input',
                  show_tokens=False, parser_debug=DEFAULT_DEBUG, check=False):
    assert isinstance(python_stmts, str)
    tokens = Python2Scanner().tokenize(python_stmts)
    if show_tokens:
        for t in tokens:
            print(t)

    # For heavy grammar debugging:
    # parser_debug = {'rules': True, 'transition': True, 'reduce': True,
    #               'errorstack': 'full', 'context': True, 'dups': True}
    # Normal debugging:
    # parser_debug = {'rules': False, 'transition': False, 'reduce': True,
    #                'errorstack': 'full', 'context': True, 'dups': True}
    parser = PythonParser(start=start, debug=parser_debug)
    if check:
        parser.check_grammar()
    return parser.parse(tokens)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        for python2_stmts in (
#                 # "if True: pass",
#                 """
# while True:
#     if False:
#         continue

# """,
                # "if True: pass",
                """return f()""",
                ):
            print(python2_stmts)
            print('-' * 30)
            ast = parse_python2(python2_stmts + ENDMARKER,
                                start='file_input', show_tokens=False, check=True)
            print(ast)
            print('=' * 30)
    else:
        python2_stmts = " ".join(sys.argv[1:])
        parse_python2(python2_stmts, show_tokens=False, check=True)
