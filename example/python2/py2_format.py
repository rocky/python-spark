#  Copyright (c) 2016 by Rocky Bernstein

"""Formats Python source an abstract syntax tree created by AST builder.

Semantic action rules for nonterminal symbols can be specified here by
creating a method prefaced with "n_" for that nonterminal. For
example, "n_exec_stmt" handles the semantic actions for the
"exec_smnt" nonterminal symbol. Similarly if a method with the name
of the nontermail is suffixed with "_exit" it will be called after
all of its children are called.

Another other way to specify a semantic rule for a nonterminal is via
rule given in one of the tables MAP_R0, MAP_R, or MAP_DIRECT.

These uses a printf-like syntax to direct substitution from attributes
of the nonterminal and its children..

The rest of the below describes how table-driven semantic actions work
and gives a list of the format specifiers. The default() and engine()
methods implement most of the below.

  Step 1 determines a table (T) and a path to a
  table key (K) from the node type (N) (other nodes are shown as O):

         N                  N               N&K
     / | ... \          / | ... \        / | ... \
    O  O      O        O  O      K      O  O      O
              |
              K

  MAP_R0 (TABLE_R0)  MAP_R (TABLE_R)  MAP_DIRECT (TABLE_DIRECT)

  The default is a direct mapping.  The key K is then extracted from the
  subtree and used to find a table entry T[K], if any.  The result is a
  format string and arguments (a la printf()) for the formatting engine.
  Escapes in the format string are:

    %c  evaluate children N[A] recursively*
    %C  evaluate children N[A[0]]..N[A[1]-1] recursively, separate by A[2]*
    %P  same as %C but sets operator precedence
    %D  same as %C but is for left-recursive lists like kwargs which
        goes to epsilon at the beginning. Using %C an extra separator
        with an epsilon appears at the beginning
    %|  tab to current indentation level
    %+ increase current indentation level
    %- decrease current indentation level
    %{...} evaluate ... in context of N
    %% literal '%'
    %p evaluate N setting precedence


  * indicates an argument (A) required.

  The '%' may optionally be followed by a number (C) in square brackets, which
  makes the engine walk down to N[C] before evaluating the escape code.
"""
from __future__ import print_function

import re, sys

PYTHON3 = (sys.version_info >= (3, 0))

from py2_parser import parse_python2
from spark_parser import GenericASTTraversal # , DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG

if PYTHON3:
    from io import StringIO
    minint = -sys.maxsize-1
    maxint = sys.maxsize
else:
    from StringIO import StringIO
    minint = -sys.maxint-1
    maxint = sys.maxint

# TAB = '\t'			# as God intended
TAB = ' ' *4   # is less spacy than "\t"
INDENT_PER_LEVEL = ' ' # additional intent per pretty-print level

TABLE_R = {
}

TABLE_R0 = {}

TABLE_DIRECT = {
    'break_stmt':       ( '%|break\n', ),
    'continue_stmt':    ( '%|continue\n', ),
    'del_stmt':	        ( '%|del %c\n', 1),
    'expr_stmt':	( '%|%c%c\n', 0, 1),
    'global_stmt':	( '%|global %C\n', (1, maxint, '')),
    'print_stmt':       ( '%|print %c\n', 1),
    'pass_stmt':        ( '%|pass\n', ),
    'import_from':      ( '%|from %c import %c\n', 1, 2 ),
    'import_name':      ( '%|import %c\n', 1 ),
    'newline_or_stmt':  ('%c\n', 0),
    'elif_suites':	( '%|elif %c:\n%?%+%c%-', 2, 4),
    'comma_name':	( ', %c', 1),
    'while_stmt':	( '%|while %c:\n%+%c%-', 1, 3),
    'classdef':         ( '%|class %c%c:\n%+%c%-\n\n', 1, 2, 4 ),
    'funcdef':          ( '%|def %c%c:\n%+%c%-\n\n', 1, 2, 4 ),
    'exprlist':         ( '%c%c%c', 0, 1 , 2 ),
    'comp_op_exprs':    ( ' %c %c', 0, 1 ),
    'or_and_test':      ( ' %c %c', 0, 1 ),
    'comma_import_as_name': (', %c', 1 ),
    'comma_dotted_as_names': ('%C', (1, maxint, ', ') ),
    'augassign_yield_expr_or_testlist' : ( ' %c %c', 0, 1 ),

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
                ((?P<type> [^{] ) |
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
        out = ''.join((str(j) for j in data))
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
      l = len(node)
      if l == 1:
          self.preorder(node[0])
      elif l == 3:
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

    # Possibly this kind of thing should be an engine format
    # 'import_as_name': ('%c %?as %c', 0, 2) which means:
    #   'import_as_name': ('%c', 0)
    # if len(node) < 2 else:
    #   'import_as_name': ('%c as %c', 0, 2),
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
            self.preorder(node[0])
            assert node[1] == 'COMMA'
            self.write(', ')
            self.preorder(node[2])
            self.preorder(node[3])
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

    def engine(self, entry, startnode):
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

            typ = m.group('type') or '{'
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
                if isinstance(entry[arg], int):
                    self.preorder(node[entry[arg]])
                arg += 1
            elif typ == 'p':
                (index, self.prec) = entry[arg]
                self.preorder(node[index])
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
        mapping = self._get_mapping(node)
        table = mapping[0]
        key = node

        for i in mapping[1:]:
            key = key[i]

        if key.type in table:
            self.engine(table[key.type], node)
            self.prune()

    def format_python2(self, ast):
        """convert AST to Python2 source code"""
        return self.traverse(ast)

    @classmethod
    def _get_mapping(cls, node):
        return MAP.get(node, MAP_DIRECT)


def format_python2_stmts(python_stmts, show_tokens=False, showast=False,
                         showgrammar=False, compile_mode='exec'):
    """
    formats python2 statements
    """

    parser_debug = {'rules': False, 'transition': False,
                    'reduce': showgrammar,
                    'errorstack': True, 'context': True }
    parsed = parse_python2(python_stmts, show_tokens=show_tokens,
                           parser_debug=parser_debug)
    assert parsed == 'file_input', 'Should have parsed grammar start'

    formatter = Python2Formatter()

    if showast:
        print(parsed)

    # What we've been waiting for: Generate source from AST!
    python2_formatted_str = formatter.format_python2(parsed)

    return python2_formatted_str

if __name__ == '__main__':
    def format_test(python2_stmts):
        from py2_scan import ENDMARKER
        formatted = format_python2_stmts(python2_stmts + ENDMARKER,
                                         show_tokens=False, showast=True,
                                         showgrammar=False)
        print('=' * 30)
        print(formatted)
        return
    # format_test("from os import path")
    # format_test("pass")
    format_test("""
x = 1 + 2
y = 3 // 4
""")
#     format_test("""
# if True:
#   if True:
#      pass
# pass

# """)
