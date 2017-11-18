#  Copyright (c) 2016-2017 by Rocky Bernstein
#  Based on decompyle.py
#  Copyright (c) 1999 John Aycock

"""Formats Python source an abstract syntax tree created by AST builder.

The below is a bit long, but still it is somehwat abbreviated.
See https://github.com/rocky/python-uncompyle6/wiki/Table-driven-semantic-actions.
for a more complete explanation, nicely marked up and with examples.

Semantic action rules for nonterminal symbols can be specified here by
creating a method prefaced with "n_" for that nonterminal. For
example, "n_exec_stmt" handles the semantic actions for the
"exec_stmt" nonterminal symbol. Similarly if a method with the name
of the nontermail is suffixed with "_exit" it will be called after
all of its children are called.

After a while writing methods this way, you'll probably find many
routines which do similar sorts of things, and soon you'll find you
want a short notation to describe rules and not have to create methods
at all.

So another other way to specify a semantic rule for a nonterminal is via
one of the tables MAP_R0, MAP_R, or MAP_DIRECT where the key is the
nonterminal name.

These dictionaries use a printf-like syntax to direct substitution
from attributes of the nonterminal and its children..

The rest of the below describes how table-driven semantic actions work;
we also a list of the format specifiers. The default() and
template_engine() methods implement most of the below.

We allow for a couple of ways to interact with a node in a tree.  So
step 1 determines from what point of view tree-wise the rule is
applied.  In the diagram below, "N" is a nonterminal name, and K
is the table key name; we show where those are with respect to each
other in the AST tree for N.

          N&K               N                  N
         / | ... \        / | ... \          / | ... \
        O  O      O      O  O      K         O O      O
                                                      |
                                                      K
      TABLE_DIRECT      TABLE_R             TABLE_R0

The default is a "TABLE_DIRECT" mapping By far, most rules used work this way.
TABLE_R0 is rarely used.

The default is a "TABLE_DIRECT" mapping.  The key K is then extracted from the
subtree and used to find a table entry T[K], if any.  The result is a
format string and arguments (a la printf()) for the formatting engine.

Escapes in the format string are:

    %c  evaluate the node recursively. Its argument is a single
        integer or tuple representing a node index.
        If a tuple is given, the first item is the node index while
        the second item is a string giving the node/noterminal name.
        This name will be checked at runtime against the node type.

    %p  like %c but sets the operator precedence.
        Its argument then is a tuple indicating the node
        index and the precidence value, an integer.

    %C  evaluate children recursively, with sibling children separated by the
        given string.  It needs a 3-tuple: a starting node, the maximimum
        value of an end node, and a string to be inserted between sibling children

    %P same as %C but sets operator precedence.  Its argument is a 4-tuple:
        the node low and high indices, the separator, a string the precidence
        value, an integer.

    %D Same as `%C` this is for left-recursive lists like kwargs where goes
       to epsilon at the beginning. It needs a 3-tuple: a starting node, the
       maximimum value of an end node, and a string to be inserted between
       sibling children. If we were to use `%C` an extra separator with an
       epsilon would appear at the beginning.

    %|  Insert spaces to the current indentation level. Takes no arguments.

    %+ increase current indentation level. Takes no arguments.

    %- decrease current indentation level. Takes no arguments.

    %{...} evaluate ... in context of N

    %% literal '%'. Takes no arguments.

The '%' may optionally be followed by a number (C) in square
brackets, which makes the template engine walk down to N[C] before
evaluating the escape code.

"""
# from __future__ import print_function

import re, sys

from py2_parser import parse_python2
from spark_parser import GenericASTTraversal # , DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG

PYTHON3 = (sys.version_info >= (3, 0))

if PYTHON3:
    from io import StringIO
    minint = -sys.maxsize-1
    maxint = sys.maxsize
else:
    from StringIO import StringIO
    minint = -sys.maxint-1
    maxint = sys.maxint

TAB = ' ' *4   # is less spacy than "\t"
INDENT_PER_LEVEL = ' ' # additional intent per pretty-print level

TABLE_R = {
}

TABLE_R0 = {}

TABLE_DIRECT = {
    'break_stmt':       ( '%|break\n', ),
    'continue_stmt':    ( '%|continue\n', ),
    'del_stmt':	        ( '%|del %c\n',
                          (1, 'exprlist')),
    'expr_stmt':	( '%|%c %c %c\n',
                          (0, 'testlist'), 1, 2),
    'global_stmt':	( '%|global %C\n', (1, maxint, '') ),
    'print_stmt':       ( '%|print %c\n',
                          (1, 'test_params_or_redirect') ),
    'pass_stmt':        ( '%|pass\n', ),
    'import_from':      ( '%|from %c import %c\n',
                          (1, 'dots_dotted_name_or_dots'), (2, 'import_list') ),
    'import_name':      ( '%|import %c\n', 1 ),
    'newline_or_stmt':  ('%c\n', 0),
    'elif_suites':	( '%|elif %c:\n%?%+%c%-', 2, 4),
    'comma_name':	( ', %c', 1),

    # FIXME: Not quite right. Should handle else_suite_opt at index 4
    'while_stmt':	( '%|while %c:\n%+%c%-',
                          (1, 'test'), (3, 'suite') ),

    'classdef':         ( '%|class %c%c:\n%+%c%-\n\n', 1, 2, 4 ),
    'funcdef':          ( '%|def %c%c:\n%+%c%-\n\n', 1, 2, 4 ),
    'exprlist':         ( '%c%c%c', 0, 1 , 2 ),
    'comp_op_exprs':    ( ' %c %c', 0, 1 ),
    'or_and_test':      ( ' %c %c', 0, 1 ),
    'comma_import_as_name': (', %c',
                             (1, 'import_as_name') ),
    'comma_dotted_as_names': ('%C', (1, maxint, ', ') ),

    'NAME':	 ( '%{attr}', ),
    'STRING':	 ( '%{attr}', ),
    'NUMBER':	 ( '%{attr}', ),
    'BINOP':	 ( '%{attr}', ),
    'COMP_OP':	 ( '%{attr}', ),
    'UNOP':	 ( '%{attr}', ),
    'AUGASSIGN': ( '%{attr}', ),
    'OR':	 ( 'or', ),
    'AND':	 ( 'and', ),
    'AS':	 ( 'as', ),
    'LPAREN':	 ( '(', ),
    'RPAREN':	 ( ')', ),
    'LBRACE':	 ( '{', ),
    'RBRACE':	 ( '}', ),
    'LBRACKET':	 ( '[', ),
    'RBRACKET':	 ( ']', ),
    'PLUS':	 ( '+', ),
    'MINUS':	 ( '-', ),
    'TILDE':	 ( '~', ),
    'COLON':	 ( ':', ),
    'DOT':	 ( '.', ),
    'EQUAL':	 ( '=', ),
    'STAR':	 ( '*', ),
    'STARSTAR':	 ( '**', ),

}

MAP_DIRECT = (TABLE_DIRECT, )
MAP_R0 = (TABLE_R0, -1, 0)
MAP_R = (TABLE_R, -1)

MAP = {
    'file_input':	MAP_R,
    'stmt':		MAP_R,
    'designator':	MAP_R,
}

escape = re.compile(r'''
            (?P<prefix> [^%]* )
            % ( \[ (?P<child> -? \d+ ) \] )?
                ((?P<kind> [^{] ) |
                 ( [{] (?P<expr> [^}]* ) [}] ))
        ''', re.VERBOSE)

class Python2FormatterError(Exception):
    def __init__(self, errmsg):
        self.errmsg = errmsg

    def __str__(self):
        return self.errmsg

class Python2Formatter(GenericASTTraversal, object):
    stacked_params = ('f', 'indent', 'isLambda', '_globals')

    def __init__(self):
        GenericASTTraversal.__init__(self, ast=None)
        params = {
            'indent': '',
            }
        self.params = params
        self.ERROR = None
        self.pending_newlines = 0
        self.hide_internal = True
        return

    f = property(lambda s: s.params['f'],
                 lambda s, x: s.params.__setitem__('f', x),
                 lambda s: s.params.__delitem__('f'),
                 None)

    indent = property(lambda s: s.params['indent'],
                 lambda s, x: s.params.__setitem__('indent', x),
                 lambda s: s.params.__delitem__('indent'),
                 None)

    def indentMore(self, indent=TAB):
        self.indent += indent

    def indentLess(self, indent=TAB):
        self.indent = self.indent[:-len(indent)]

    def traverse(self, node, indent=None, isLambda=False):
        if indent is None: indent = self.indent
        p = self.pending_newlines
        self.pending_newlines = 0
        self.params = {
            'f': StringIO(),
            'indent': indent,
            }
        self.preorder(node)
        self.f.write('\n'*self.pending_newlines)
        result = self.f.getvalue()
        self.pending_newlines = p
        return result

    # FIXME: this is code left over from uncompyle6.
    # It can be simplified and probalby made appropriate
    # for this use by removing the pending lines.
    def write(self, *data):
        if (len(data) == 0) or (len(data) == 1 and data[0] == ''):
            return
        out = ''.join([str(j) for j in data])
        n = 0
        for i in out:
            if i == '\n':
                n += 1
                if n == len(out):
                    self.pending_newlines = max(self.pending_newlines, n)
                    return
            elif n:
                self.pending_newlines = max(self.pending_newlines, n)
                out = out[n:]
                break
            else:
                break

        if self.pending_newlines > 0:
            self.f.write('\n'*self.pending_newlines)
            self.pending_newlines = 0

        for i in out[::-1]:
            if i == '\n':
                self.pending_newlines += 1
            else:
                break

        if self.pending_newlines:
            out = out[:-self.pending_newlines]
        self.f.write(out)

    def println(self, *data):
        if data and not(len(data) == 1 and data[0] ==''):
            self.write(*data)
        self.pending_newlines = max(self.pending_newlines, 1)

    OTHER_SYM = {'{': '}', '[': ']', '(': ')', '`': '`'}

    # redo: 'atom": ( '%? %c %c', 0, 1, 2),
    def n_atom(self, node):
        """atom ::=
             ('(' [yield_expr|testlist_gexp] ')'
                 | '[' [listmaker] ']'
                 | '{' [dictmaker] '}'
                 | '`' testlist1 '`'
                 | NAME | NUMBER | STRING+)
        """
        length = len(node)
        if length == 1:
            self.preorder(node[0])
        elif length == 3:
            self.preorder(node[0])
            self.preorder(node[1])
            self.preorder(node[2])
        else:
            assert False, "Expecting atom to have length 1 or 3"
        self.prune()

    def n_subscript(self, node):
        if node == 'DOT' and len(node) == 3:
            self.write('...')
            self.prune
        for n in node:
            self.preorder(n)
        self.prune()

    # Possibly this kind of thing should be an template-engine format
    # 'import_as_name': ('%c %?as %c', 0, 2) which means:
    # 'import_as_name': ('%c', 0) if len(node) < 2 else:
    # 'import_as_name': ('%c as %c', 0, 2),
    def n_import_as_name(self, node):
        self.preorder(node[0])
        if len(node) == 3:
            self.write(' as ')
            self.preorder(node[2])
        self.prune() # stop recursing

    # redo as
    # 'dotted_name': ('%c%?%c', 0, 1)
    def n_dotted_name(self, node):
        self.preorder(node[0])
        if len(node) == 2:
            self.preorder(node[1])
        self.prune() # stop recursing

    # redo as
    # 'dotted_as_name': ('%c%? as %c', 0, 2)
    def n_dotted_as_name(self, node):
        self.preorder(node[0])
        if len(node) == 3:
            self.write(' as ')
            self.preorder(node[2])
        self.prune() # stop recursing

    def n_dots_dotted_name_or_dots(self, node):
        if node[0] == 'DOT':
            pass
        else:
            self.preorder(node[0])
            self.preorder(node[1])
            self.prune()

    # redo as
    # 'assert_stmt': ('%|assert %c%?, %c\n', 1, 2)
    def n_assert_stmt(self, node):
        self.write(self.indent, 'assert ')
        self.preorder(node[1])
        if len(node) == 4:
            self.write(', ')
            self.preorder(node[3])
        self.println()
        self.prune() # stop recursing

    def n_yield(self, node):
        self.write('yield ')
        self.preorder(node[0])
        self.prune() # stop recursing

    def n_binary_expr(self, node):
        self.preorder(node[0])
        self.write(' ')
        self.preorder(node[-1])
        self.write(' ')
        self.preorder(node[1])
        self.prune()

    def n_factor(self, node):
        self.preorder(node[0])
        if len(node) > 1:
            self.write(' ')
            self.preorder(node[1])
        self.prune()

    def n_and_not_tests(self, node):
        if len(node) > 0:
            self.preorder(node[0])
            self.write(' ')
            self.preorder(node[1])
            self.write(' ')
            self.preorder(node[2])
        self.prune()

    def n_comment(self, node):
        if node[0].attr[0] in [' ', '\t']:
            # remove last \n stored in pending newlines
            self.pending_newlines = 0
            self.write(node[0].attr, "\n")
        else:
            self.write(self.indent, node[0].attr, "\n")

    def n_exec_stmt(self, node):
        """
        exec_stmt ::= EXEC expr
        exec_stmt ::= EXEC expr IN test
        exec_stmt ::= EXEC expr IN test COMMA test
        """
        self.write(self.indent, 'exec ')
        self.preorder(node[1])

        if len(node) > 2:
            self.write(self.indent, ' in ')
            self.preorder(node[3])
            if len(node) > 5:
                self.write(self.indent, ', ')
                self.preorder(node[5])
        self.println()
        self.prune() # stop recursing

    # 'return_stmt':      ( '%|return %?%c\n', 1),
    def n_return_stmt(self, node):
        assert node[0] == 'RETURN'
        self.write(self.indent, 'return ')
        if len(node) > 1:
            self.preorder(node[1])
        self.println()
        self.prune() # stop recursing

    def n_if_stmt(self, node):
        assert node[0] == 'IF'
        self.write(self.indent, 'if ')
        self.preorder(node[1])
        assert node[2] == 'COLON'
        self.write(':\n')
        self.indentMore()
        self.preorder(node[3])
        self.indentLess()
        if len(node[4]) > 0:
            self.preorder(node[4])
        if len(node[5]) > 0:
            self.preorder(node[5])
        self.prune()

    def n_with_stmt(self, node):
        assert node[0] == 'WITH'
        self.write(self.indent, 'with ')
        self.preorder(node[1])
        i = 2
        # Redo as n_with_var
        if len(node[1]) > 0:
            self.write(' as ')
            self.preorder(node[2][0][1])
            i = 3
        assert node[i] == 'COLON'
        self.write(":\n")
        self.indentMore()
        self.preorder(node[i+1])
        self.indentLess()
        self.prune()

    # redo as
    # 'else_stmt_opt':	( '%|else:\n%?%+%c%-', 1 ),
    def n_else_suite_opt(self, node):
        if len(node) > 0:
            self.write(self.indent, 'else: ')
            self.println('')
            self.indentMore()
            self.preorder(node[2])
        self.indentLess()
        self.prune()

    # redo as
    # 'elif_suites':	( '%|elif %c:\n%?%+%c%-', 2, 4),
    def n_elif_suites(self, node):
        if len(node) > 0:
            assert node[1] == 'ELIF'
            self.write(self.indent, 'elif ')
            self.preorder(node[2])
            self.println(':')
            self.indentMore()
            self.preorder(node[4])
            self.indentLess()
            self.prune()

    # redo as
    # 'comma_fpdef_opt_eqtests": ( '%?%c, %c%c', 0, 2, 3),
    def n_comma_fpdef_opt_eqtests(self, node):
        if len(node) > 0:
            j = 1
            while j < len(node):
                self.write(', ')
                self.preorder(node[j])
                j += 3
            self.prune()

    # redo as
    # 'n_comma_tests": ( '%?%c, %c', 0, 2),
    def n_comma_tests(self, node):
        if len(node) > 0:
            self.preorder(node[0])
            assert node[1] == 'COMMA'
            self.write(', ')
            self.preorder(node[2])
            self.prune()

    # redo as
    # 'n_argument_comma": ( '%c%?%c, ', 0, 1),
    def n_argument_comma(self, node):
        self.preorder(node[0])
        if len(node) > 0:
            self.preorder(node[1])
            self.write(', ')
            self.prune()

    def n_binop_arith_exprs(self, node):
        if len(node) > 0:
            self.preorder(node[0])
            assert node[1], 'binop'
            self.write(' ')
            self.preorder(node[1])
            self.write(' ')
            self.preorder(node[2])
            self.prune()

    def n_op_factor(self, node):
        self.write(' ')
        self.preorder(node[0])
        if len(node) > 1:
            self.preorder(node[1])
        self.prune()

    # redo as
    # 'n_starstar_factor_opt": ( '%? %c %c', 0, 1),
    def n_starstar_factor_opt(self, node):
        if len(node) > 0:
            self.write(' ')
            self.preorder(node[0])
            self.write(' ')
            self.preorder(node[1])
        self.prune()

    def n_for_stmt(self, node):
        assert node[0] == 'FOR'
        self.write(self.indent, 'for ')
        self.preorder(node[1])
        assert node[2] == 'IN'
        self.write(' in ')
        self.preorder(node[3])
        assert node[4] == 'COLON'
        self.write(':\n')
        self.indentMore()
        self.preorder(node[5])
        self.indentLess()
        self.prune()

    # def n_stmt_plus(self, node):
    #     if len(node) > 1:
    #         self.write(self.indent)
    #         for n in node:
    #             self.preorder(n)
    #             self.println()
    #     else:
    #         self.preorder(node[0])

    #     self.prune()

    def template_engine(self, entry, startnode):
        """The format template interpetation engine.  See the comment at the
        beginning of this module for the how we interpret format specifications such as
        %c, %C, and so on.
        """

        # self.println("-----")
        # print("XXX", startnode)

        fmt = entry[0]
        arg = 1
        i = 0

        m = escape.search(fmt)
        while m:
            i = m.end()
            self.write(m.group('prefix'))

            typ = m.group('kind') or '{'
            node = startnode
            try:
                if m.group('child'):
                    node = node[int(m.group('child'))]
            except:
                print(node.__dict__)
                raise

            if   typ == '%':	self.write('%')
            elif typ == '+':	self.indentMore()
            elif typ == '-':	self.indentLess()
            elif typ == '|':	self.write(self.indent)
            elif typ == 'c':
                index = entry[arg]
                if isinstance(index, tuple):
                    assert node[index[0]] == index[1], (
                        "at %s[%d], %s vs %s" % (
                            node.kind, arg, node[index[0]].kind, index[1])
                        )
                    index = index[0]
                if isinstance(index, int):
                    self.preorder(node[index])
                arg += 1
            elif typ == 'p':
                p = self.prec
                length = len(entry)
                if length == 3:
                    (index, self.prec, name) = entry[arg]
                    assert node[index] == name, (
                        "at %s[%d], %s vs %s" % (
                            node.kind, arg, node[index[0]].kind, index[1])
                        )
                elif length == 2:
                    (index, self.prec) = entry[arg]
                else:
                    raise RuntimeError("Invalid %%p tuple length %d; length should be 1 or 2"
                                       % length)

                self.preorder(node[index])
                self.prec = p
                arg += 1
            elif typ == 'C':
                low, high, sep = entry[arg]
                remaining = len(node[low:high])
                for subnode in node[low:high]:
                    self.preorder(subnode)
                    remaining -= 1
                    if remaining > 0:
                        self.write(sep)
                arg += 1
            elif typ == 'D':
                low, high, sep = entry[arg]
                remaining = len(node[low:high])
                for subnode in node[low:high]:
                    remaining -= 1
                    if len(subnode) > 0:
                        self.preorder(subnode)
                        if remaining > 0:
                            self.write(sep)
                            pass
                        pass
                    pass
                arg += 1
            elif typ == 'x':
                # This code is only used in fragments
                assert isinstance(entry[arg], tuple)
                arg += 1
            elif typ == 'P':
                p = self.prec
                low, high, sep, self.prec = entry[arg]
                remaining = len(node[low:high])
                # remaining = len(node[low:high])
                for subnode in node[low:high]:
                    self.preorder(subnode)
                    remaining -= 1
                    if remaining > 0:
                        self.write(sep)
                self.prec = p
                arg += 1
            elif typ == '{':
                d = node.__dict__
                expr = m.group('expr')
                try:
                    self.write(eval(expr, d, d))
                except:
                    print(node)
                    raise
            m = escape.search(fmt, i)
        self.write(fmt[i:])

    def default(self, node):
        table = MAP_DIRECT[0]
        key = node

        for i in MAP_DIRECT[1:]:
            key = key[i]

        if key.kind in table:
            self.template_engine(table[key.kind], node)
            self.prune()

def format_python2_stmts(python_stmts, show_tokens=False, showast=False,
                         showgrammar=False, compile_mode='exec'):
    """
    formats python2 statements
    """

    parser_debug = {'rules': False, 'transition': False,
                    'reduce': showgrammar,
                    'errorstack': True, 'context': True, 'dups': True }
    parsed = parse_python2(python_stmts, show_tokens=show_tokens,
                           parser_debug=parser_debug)
    assert parsed == 'file_input', 'Should have parsed grammar start'

    formatter = Python2Formatter()

    if showast:
        print(parsed)

    # What we've been waiting for: Generate source from AST!
    python2_formatted_str = formatter.traverse(parsed)

    return python2_formatted_str

def main(string, show_tokens=True, show_ast=True, show_grammar=True):
    from py2_scan import ENDMARKER
    formatted = format_python2_stmts(string + ENDMARKER, show_tokens, show_ast, show_grammar)
    print('=' * 30)
    print(formatted)
    return


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # main("from os import path")
        # format_test("pass")
        main(
"""
x = 1 + 2
y = 3 // 4
z += 4
""")
        main(
"""
if True:
    pass
""")
#         main(
# """
# if True:
#     if True:
#         pass
#     pass
# pass
# """)
    else:
        string = open(sys.argv[1]).read()
        main(string)
