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
import uncompyle6.parser as python_parser

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
    'pass_stmt':		( '%|pass\n', ),
    'import_from': ( '%|from %c import %c\n', 1, 2 ),
    'import_name': ( '%|import %c\n', 1 ),
    'newline_or_stmt': ('%c', 0),
     'dotted_name': ('%c%c', 0, 1),
    'comma_dotted_as_names': ('%C', (1, maxint, ', ') ),
    # 'import_as_name': ('%c as %c', 0, 2),
    'import_as_name': ('%c', 0),
    'NAME':	( '%{attr}', ),
    'DOT':	( '.', ),

    'BINARY_ADD':	( '+' ,),
    'BINARY_SUBTRACT':	( '-' ,),
    'BINARY_MULTIPLY':	( '*' ,),
    'BINARY_DIVIDE':	( '/' ,),
    'BINARY_TRUE_DIVIDE':	( '/' ,),
    'BINARY_FLOOR_DIVIDE':	( '//' ,),
    'BINARY_MODULO':	( '%%',),
    'BINARY_POWER':	( '**',),
    'BINARY_LSHIFT':	( '<<',),
    'BINARY_RSHIFT':	( '>>',),
    'BINARY_AND':	( '&' ,),
    'BINARY_OR':	( '|' ,),
    'BINARY_XOR':	( '^' ,),
    'INPLACE_ADD':	( '+=' ,),
    'INPLACE_SUBTRACT':	( '-=' ,),
    'INPLACE_MULTIPLY':	( '*=' ,),
    'INPLACE_DIVIDE':	( '/=' ,),
    'INPLACE_TRUE_DIVIDE':	( '/=' ,),
    'INPLACE_FLOOR_DIVIDE':	( '//=' ,),
    'INPLACE_MODULO':	( '%%=',),
    'INPLACE_POWER':	( '**=',),
    'INPLACE_LSHIFT':	( '<<=',),
    'INPLACE_RSHIFT':	( '>>=',),
    'INPLACE_AND':	( '&=' ,),
    'INPLACE_OR':	( '|=' ,),
    'INPLACE_XOR':	( '^=' ,),
    'binary_expr':	( '%c %c %c', 0, -1, 1 ),

    'UNARY_POSITIVE':	( '+',),
    'UNARY_NEGATIVE':	( '-',),
    'UNARY_INVERT':	( '~%c'),
    'unary_expr':   ( '%c%c', 1, 0),

    'unary_not':	( 'not %c', 0 ),
    'unary_convert':	( '`%c`', 0 ),
    'get_iter':	( 'iter(%c)', 0 ),
    'slice0':		( '%c[:]', 0 ),
    'slice1':		( '%c[%p:]', 0, (1, 100) ),
    'slice2':		( '%c[:%p]', 0, (1, 100) ),
    'slice3':		( '%c[%p:%p]', 0, (1, 100), (2, 100) ),

    'IMPORT_FROM':	( '%{pattr}', ),
    'load_attr':	( '%c.%[1]{pattr}', 0),
    'LOAD_NAME':	( '%{pattr}', ),
    'LOAD_CLASSNAME':	( '%{pattr}', ),
    'LOAD_GLOBAL':	( '%{pattr}', ),
    'LOAD_DEREF':	( '%{pattr}', ),
    'LOAD_LOCALS':	( 'locals()', ),
    'LOAD_ASSERT':  ( '%{pattr}', ),
#   'LOAD_CONST':	( '%{pattr}', ),	# handled by n_LOAD_CONST
    'DELETE_FAST':	( '%|del %{pattr}\n', ),
    'DELETE_NAME':	( '%|del %{pattr}\n', ),
    'DELETE_GLOBAL':	( '%|del %{pattr}\n', ),
    'delete_subscr':	( '%|del %c[%c]\n', 0, 1,),
    'binary_subscr':	( '%c[%p]', 0, (1, 100)),
    'binary_subscr2':	( '%c[%p]', 0, (1, 100)),
    'store_subscr':	( '%c[%c]', 0, 1),
    'STORE_FAST':	( '%{pattr}', ),
    'STORE_NAME':	( '%{pattr}', ),
    'STORE_GLOBAL':	( '%{pattr}', ),
    'STORE_DEREF':	( '%{pattr}', ),
    'unpack':		( '%C%,', (1, maxint, ', ') ),
    'unpack_w_parens':		( '(%C%,)', (1, maxint, ', ') ),
    'unpack_list':	( '[%C]', (1, maxint, ', ') ),
    'build_tuple2':	( '%P', (0, -1, ', ', 100) ),

    'list_iter':	( '%c', 0),
    'list_for':		( ' for %c in %c%c', 2, 0, 3 ),
    'list_if':		( ' if %c%c', 0, 2 ),
    'list_if_not':		( ' if not %p%c', (0, 22), 2 ),
    'lc_body':		( '', ),	# ignore when recusing

    'comp_iter':	( '%c', 0),
    'comp_for':		( ' for %c in %c%c', 2, 0, 3 ),
    'comp_if':		( ' if %c%c', 0, 2 ),
    'comp_ifnot':	( ' if not %p%c', (0, 22), 2 ),
    'comp_body':	( '', ),	# ignore when recusing
    'set_comp_body':    ( '%c', 0 ),
    'gen_comp_body':    ( '%c', 0 ),
    'dict_comp_body':   ( '%c:%c', 1, 0 ),

    'assign':		( '%|%c = %p\n', -1, (0, 200) ),
    'augassign1':	( '%|%c %c %c\n', 0, 2, 1),
    'augassign2':	( '%|%c.%[2]{pattr} %c %c\n', 0, -3, -4),
    'designList':	( '%c = %c', 0, -1 ),
    'and':          	( '%c and %c', 0, 2 ),
    'ret_and':        	( '%c and %c', 0, 2 ),
    'and2':          	( '%c', 3 ),
    'or':           	( '%c or %c', 0, 2 ),
    'ret_or':           	( '%c or %c', 0, 2 ),
    'conditional':  ( '%p if %p else %p', (2, 27), (0, 27), (4, 27)),
    'ret_cond':     ( '%p if %p else %p', (2, 27), (0, 27), (4, 27)),
    'conditionalnot':  ( '%p if not %p else %p', (2, 27), (0, 22), (4, 27)),
    'ret_cond_not':  ( '%p if not %p else %p', (2, 27), (0, 22), (4, 27)),
    'conditional_lambda':  ( '(%c if %c else %c)', 2, 0, 3),
    'return_lambda':    ('%c', 0),
    'compare':		( '%p %[-1]{pattr} %p', (0, 19), (1, 19) ),
    'cmp_list':		( '%p %p', (0, 20), (1, 19)),
    'cmp_list1':	( '%[3]{pattr} %p %p', (0, 19), (-2, 19)),
    'cmp_list2':	( '%[1]{pattr} %p', (0, 19)),
    'funcdef':  	( '\n\n%|def %c\n', -2), # -2 to handle closures
    'funcdefdeco':  	( '\n\n%c', 0),
    'mkfuncdeco':  	( '%|@%c\n%c', 0, 1),
    'mkfuncdeco0':  	( '%|def %c\n', 0),
    'classdefdeco':  	( '\n\n%c', 0),
    'classdefdeco1':  	( '%|@%c\n%c', 0, 1),
    'kwarg':    	( '%[0]{pattr}=%c', 1),
    'kwargs':    	( '%D', (0, maxint, ', ') ),
    'importlist2':	( '%C', (0, maxint, ', ') ),

    'assert':		( '%|assert %c\n' , 0 ),
    'assert2':		( '%|assert %c, %c\n' , 0, 3 ),
    'assert_expr_or': ( '%c or %c', 0, 2 ),
    'assert_expr_and':    ( '%c and %c', 0, 2 ),
    'print_items_stmt': ( '%|print %c%c,\n', 0, 2),
    'print_items_nl_stmt': ( '%|print %c%c\n', 0, 2),
    'print_item':  ( ', %c', 0),
    'print_nl':	( '%|print\n', ),
    'print_to':		( '%|print >> %c, %c,\n', 0, 1 ),
    'print_to_nl':	( '%|print >> %c, %c\n', 0, 1 ),
    'print_nl_to':	( '%|print >> %c\n', 0 ),
    'print_to_items':	( '%C', (0, 2, ', ') ),

    'call_stmt':	( '%|%p\n', (0, 200)),
    'break_stmt':	( '%|break\n', ),
    'continue_stmt':	( '%|continue\n', ),

    'raise_stmt0':	( '%|raise\n', ),
    'raise_stmt1':	( '%|raise %c\n', 0),
    'raise_stmt2':	( '%|raise %c, %c\n', 0, 1),
    'raise_stmt3':	( '%|raise %c, %c, %c\n', 0, 1, 2),

    'ifstmt':		( '%|if %c:\n%+%c%-', 0, 1 ),
    'iflaststmt':		( '%|if %c:\n%+%c%-', 0, 1 ),
    'iflaststmtl':		( '%|if %c:\n%+%c%-', 0, 1 ),
    'testtrue':     ( 'not %p', (0, 22) ),

    'ifelsestmt':	( '%|if %c:\n%+%c%-%|else:\n%+%c%-', 0, 1, 3 ),
    'ifelsestmtc':	( '%|if %c:\n%+%c%-%|else:\n%+%c%-', 0, 1, 3 ),
    'ifelsestmtl':	( '%|if %c:\n%+%c%-%|else:\n%+%c%-', 0, 1, 3 ),
    'ifelifstmt':	( '%|if %c:\n%+%c%-%c', 0, 1, 3 ),
    'elifelifstmt':	( '%|elif %c:\n%+%c%-%c', 0, 1, 3 ),
    'elifstmt':		( '%|elif %c:\n%+%c%-', 0, 1 ),
    'elifelsestmt':	( '%|elif %c:\n%+%c%-%|else:\n%+%c%-', 0, 1, 3 ),
    'ifelsestmtr':	( '%|if %c:\n%+%c%-%|else:\n%+%c%-', 0, 1, 2 ),
    'elifelsestmtr':	( '%|elif %c:\n%+%c%-%|else:\n%+%c%-\n\n', 0, 1, 2 ),

    'whileTruestmt':	( '%|while True:\n%+%c%-\n\n', 1 ),
    'whilestmt':	( '%|while %c:\n%+%c%-\n\n', 1, 2 ),
    'while1stmt':	( '%|while 1:\n%+%c%-\n\n', 1 ),
    'while1elsestmt':  ( '%|while 1:\n%+%c%-%|else:\n%+%c%-\n\n', 1, 3 ),
    'whileelsestmt':	( '%|while %c:\n%+%c%-%|else:\n%+%c%-\n\n', 1, 2, -2 ),
    'whileelselaststmt':	( '%|while %c:\n%+%c%-%|else:\n%+%c%-', 1, 2, -2 ),
    'forstmt':		( '%|for %c in %c:\n%+%c%-\n\n', 3, 1, 4 ),
    'forelsestmt':	(
        '%|for %c in %c:\n%+%c%-%|else:\n%+%c%-\n\n', 3, 1, 4, -2),
    'forelselaststmt':	(
        '%|for %c in %c:\n%+%c%-%|else:\n%+%c%-', 3, 1, 4, -2),
    'forelselaststmtl':	(
        '%|for %c in %c:\n%+%c%-%|else:\n%+%c%-\n\n', 3, 1, 4, -2),
    'trystmt':		( '%|try:\n%+%c%-%c\n\n', 1, 3 ),
    'tryelsestmt':		( '%|try:\n%+%c%-%c%|else:\n%+%c%-\n\n', 1, 3, 4 ),
    'tryelsestmtc':		( '%|try:\n%+%c%-%c%|else:\n%+%c%-', 1, 3, 4 ),
    'tryelsestmtl':		( '%|try:\n%+%c%-%c%|else:\n%+%c%-', 1, 3, 4 ),
    'tf_trystmt':		( '%c%-%c%+', 1, 3 ),
    'tf_tryelsestmt':		( '%c%-%c%|else:\n%+%c', 1, 3, 4 ),
    'except':                   ('%|except:\n%+%c%-', 3 ),
    'except_pop_except':        ('%|except:\n%+%c%-', 4 ),
    'except_cond1':	( '%|except %c:\n', 1 ),
    'except_cond2':	( '%|except %c as %c:\n', 1, 5 ),
    'except_suite':     ( '%+%c%-%C', 0, (1, maxint, '') ),
    'except_suite_finalize':     ( '%+%c%-%C', 1, (3, maxint, '') ),
    'tryfinallystmt':	( '%|try:\n%+%c%-%|finally:\n%+%c%-\n\n', 1, 5 ),
    'withstmt':     ( '%|with %c:\n%+%c%-', 0, 3),
    'withasstmt':   ( '%|with %c as %c:\n%+%c%-', 0, 2, 3),
    'STORE_FAST':	( '%{pattr}', ),
    'kv':		( '%c: %c', 3, 1 ),
    'kv2':		( '%c: %c', 1, 2 ),
    'mapexpr':		( '{%[1]C}', (0, maxint, ', ') ),

    #######################
    # Python 2.5 Additions
    #######################

    # Import style for 2.5
    'importstmt': ( '%|import %c\n', 2),
    'importstar': ( '%|from %[2]{pattr} import *\n', ),
    'importmultiple': ( '%|import %c%c\n', 2, 3 ),
    'import_cont'   : ( ', %c', 2 ),

    # CE - Fixes for tuples
    'assign2':     ( '%|%c, %c = %c, %c\n', 3, 4, 0, 1 ),
    'assign3':     ( '%|%c, %c, %c = %c, %c, %c\n', 5, 6, 7, 0, 1, 2 ),

}


MAP_DIRECT = (TABLE_DIRECT, )
MAP_R0 = (TABLE_R0, -1, 0)
MAP_R = (TABLE_R, -1)

MAP = {
    'file_input':	MAP_R,
    'stmt':		MAP_R,
    'stmt':		MAP_R,
    'del_stmt':		MAP_R,
    'designator':	MAP_R,
    'exprlist':		MAP_R0,
    'dots_dotted_name_or_dots': MAP_R0,
}

escape = re.compile(r'''
            (?P<prefix> [^%]* )
            % ( \[ (?P<child> -? \d+ ) \] )?
                ((?P<type> [^{] ) |
                 ( [{] (?P<expr> [^}]* ) [}] ))
        ''', re.VERBOSE)

class ParserError(python_parser.ParserError):
    def __init__(self, error, tokens):
        self.error = error # previous exception
        self.tokens = tokens

    def __str__(self):
        lines = ['--- This code section failed: ---']
        lines.extend( list(map(str, self.tokens)) )
        lines.extend( ['', str(self.error)] )
        return '\n'.join(lines)

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

    isLambda = property(lambda s: s.params['isLambda'],
                 lambda s, x: s.params.__setitem__('isLambda', x),
                 lambda s: s.params.__delitem__('isLambda'),
                 None)

    _globals = property(lambda s: s.params['_globals'],
                 lambda s, x: s.params.__setitem__('_globals', x),
                 lambda s: s.params.__delitem__('_globals'),
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

    def print_docstring(self, indent, docstring):
        quote = '"""'
        self.write(indent)
        if not PYTHON3 and not isinstance(docstring, str):
            # Must be unicode in Python2
            self.write('u')
            docstring = repr(docstring.expandtabs())[2:-1]
        else:
            docstring = repr(docstring.expandtabs())[1:-1]

        for (orig, replace) in (('\\\\', '\t'),
                                ('\\r\\n', '\n'),
                                ('\\n', '\n'),
                                ('\\r', '\n'),
                                ('\\"', '"'),
                                ("\\'", "'")):
            docstring = docstring.replace(orig, replace)

        # Do a raw string if there are backslashes but no other escaped characters:
        # also check some edge cases
        if ('\t' in docstring
            and '\\' not in docstring
            and len(docstring) >= 2
            and docstring[-1] != '\t'
            and (docstring[-1] != '"'
                 or docstring[-2] == '\t')):
            self.write('r') # raw string
            # restore backslashes unescaped since raw
            docstring = docstring.replace('\t', '\\')
        else:
            # Escape '"' if it's the last character, so it doesn't
            # ruin the ending triple quote
            if len(docstring) and docstring[-1] == '"':
                docstring = docstring[:-1] + '\\"'
            # Escape triple quote anywhere
            docstring = docstring.replace('"""', '\\"\\"\\"')
            # Restore escaped backslashes
            docstring = docstring.replace('\t', '\\\\')
        lines = docstring.split('\n')
        calculate_indent = maxint
        for line in lines[1:]:
            stripped = line.lstrip()
            if len(stripped) > 0:
                calculate_indent = min(calculate_indent, len(line) - len(stripped))
        calculate_indent = min(calculate_indent, len(lines[-1]) - len(lines[-1].lstrip()))
        # Remove indentation (first line is special):
        trimmed = [lines[0]]
        if calculate_indent < maxint:
            trimmed += [line[calculate_indent:] for line in lines[1:]]

        self.write(quote)
        if len(trimmed) == 0:
            self.println(quote)
        elif len(trimmed) == 1:
            self.println(trimmed[0], quote)
        else:
            self.println(trimmed[0])
            for line in trimmed[1:-1]:
                self.println( indent, line )
            self.println(indent, trimmed[-1], quote)

    def n_return_stmt(self, node):
        self.write(self.indent, 'return')
        self.write(' ')
        self.preorder(node[0])
        self.println()
        self.prune() # stop recursing

    def n_return_if_stmt(self, node):
        self.write(self.indent, 'return')
        self.write(' ')
        self.preorder(node[0])
        self.println()
        self.prune() # stop recursing

    def n_yield(self, node):
        self.write('yield')
        self.write(' ')
        self.preorder(node[0])
        self.prune() # stop recursing

    # In Python 3.3+ only
    def n_yield_from(self, node):
        self.write('yield from')
        self.write(' ')
        self.preorder(node[0][0][0][0])
        self.prune() # stop recursing

    def n_buildslice3(self, node):
        if not node[0].isNone():
            self.preorder(node[0])
        self.write(':')
        if not node[1].isNone():
            self.preorder(node[1])
        self.write(':')
        if not node[2].isNone():
            self.preorder(node[2])
        self.prune() # stop recursing

    def n_buildslice2(self, node):
        if not node[0].isNone():
            self.preorder(node[0])
        self.write(':')
        if not node[1].isNone():
            self.preorder(node[1])
        self.prune() # stop recursing

    def n_ret_expr(self, node):
        if len(node) == 1 and node[0] == 'expr':
            self.n_expr(node[0])
        else:
            self.n_expr(node)

    def n_binary_expr(self, node):
        self.preorder(node[0])
        self.write(' ')
        self.preorder(node[-1])
        self.write(' ')
        self.preorder(node[1])
        self.prune()

    def n_LOAD_CONST(self, node):
        data = node.pattr; datatype = type(data)
        if isinstance(datatype, int) and data == minint:
            # convert to hex, since decimal representation
            # would result in 'LOAD_CONST; UNARY_NEGATIVE'
            # change:hG/2002-02-07: this was done for all negative integers
            # todo: check whether this is necessary in Python 2.1
            self.write( hex(data) )
        elif datatype is type(Ellipsis):
            self.write('...')
        elif data is None:
            # LOAD_CONST 'None' only occurs, when None is
            # implicit eg. in 'return' w/o params
            # pass
            self.write('None')
        else:
            self.write(repr(data))
        # LOAD_CONST is a terminal, so stop processing/recursing early
        self.prune()

    def n_delete_subscr(self, node):
        if node[-2][0] == 'build_list' and node[-2][0][-1].type.startswith('BUILD_TUPLE'):
            if node[-2][0][-1] != 'BUILD_TUPLE_0':
                node[-2][0].type = 'build_tuple2'
        self.default(node)

    n_store_subscr = n_binary_subscr = n_delete_subscr

#    'tryfinallystmt':	( '%|try:\n%+%c%-%|finally:\n%+%c%-', 1, 5 ),
    def n_tryfinallystmt(self, node):
        if len(node[1][0]) == 1 and node[1][0][0] == 'stmt':
            if node[1][0][0][0] == 'trystmt':
                node[1][0][0][0].type = 'tf_trystmt'
            if node[1][0][0][0] == 'tryelsestmt':
                node[1][0][0][0].type = 'tf_tryelsestmt'
        self.default(node)

    def n_exec_stmt(self, node):
        """
        exec_stmt ::= expr exprlist DUP_TOP EXEC_STMT
        exec_stmt ::= expr exprlist EXEC_STMT
        """
        self.write(self.indent, 'exec ')
        self.preorder(node[0])
        if not node[1][0].isNone():
            sep = ' in '
            for subnode in node[1]:
                self.write(sep); sep = ", "
                self.preorder(subnode)
        self.println()
        self.prune() # stop recursing

    def n_ifelsestmt(self, node, preprocess=0):
        n = node[3][0]
        if len(n) == 1 == len(n[0]) and n[0] == '_stmts':
            n = n[0][0][0]
        elif n[0].type in ('lastc_stmt', 'lastl_stmt'):
            n = n[0][0]
        else:
            if not preprocess:
                self.default(node)
            return

        if n.type in ('ifstmt', 'iflaststmt', 'iflaststmtl'):
            node.type = 'ifelifstmt'
            n.type = 'elifstmt'
        elif n.type in ('ifelsestmtr',):
            node.type = 'ifelifstmt'
            n.type = 'elifelsestmtr'
        elif n.type in ('ifelsestmt', 'ifelsestmtc', 'ifelsestmtl'):
            node.type = 'ifelifstmt'
            self.n_ifelsestmt(n, preprocess=1)
            if n == 'ifelifstmt':
                n.type = 'elifelifstmt'
            elif n.type in ('ifelsestmt', 'ifelsestmtc', 'ifelsestmtl'):
                n.type = 'elifelsestmt'
        if not preprocess:
            self.default(node)

    n_ifelsestmtc = n_ifelsestmtl = n_ifelsestmt

    def n_ifelsestmtr(self, node):
        if len(node[2]) != 2:
            self.default(node)

        if not (node[2][0][0][0] == 'ifstmt' and node[2][0][0][0][1][0] == 'return_if_stmts') \
                and not (node[2][0][-1][0] == 'ifstmt' and node[2][0][-1][0][1][0] == 'return_if_stmts'):
            self.default(node)
            return

        self.write(self.indent, 'if ')
        self.preorder(node[0])
        self.println(':')
        self.indentMore()
        self.preorder(node[1])
        self.indentLess()

        if_ret_at_end = False
        if len(node[2][0]) >= 3:
            if node[2][0][-1][0] == 'ifstmt' and node[2][0][-1][0][1][0] == 'return_if_stmts':
                if_ret_at_end = True

        past_else = False
        prev_stmt_is_if_ret = True
        for n in node[2][0]:
            if (n[0] == 'ifstmt' and n[0][1][0] == 'return_if_stmts'):
                if prev_stmt_is_if_ret:
                    n[0].type = 'elifstmt'
                prev_stmt_is_if_ret = True
            else:
                prev_stmt_is_if_ret = False
                if not past_else and not if_ret_at_end:
                    self.println(self.indent, 'else:')
                    self.indentMore()
                    past_else = True
            self.preorder(n)
        if not past_else or if_ret_at_end:
            self.println(self.indent, 'else:')
            self.indentMore()
        self.preorder(node[2][1])
        self.indentLess()
        self.prune()

    def n_elifelsestmtr(self, node):
        if len(node[2]) != 2:
            self.default(node)

        for n in node[2][0]:
            if not (n[0] == 'ifstmt' and n[0][1][0] == 'return_if_stmts'):
                self.default(node)
                return

        self.write(self.indent, 'elif ')
        self.preorder(node[0])
        self.println(':')
        self.indentMore()
        self.preorder(node[1])
        self.indentLess()

        for n in node[2][0]:
            n[0].type = 'elifstmt'
            self.preorder(n)
        self.println(self.indent, 'else:')
        self.indentMore()
        self.preorder(node[2][1])
        self.indentLess()
        self.prune()

    def n_importfrom(self, node):
        if node[0].pattr > 0:
            node[2].pattr = '.'*node[0].pattr+node[2].pattr
        self.default(node)

    n_importstar = n_importfrom

    def n_mklambda(self, node):
        self.make_function(node, isLambda=True)
        self.prune() # stop recursing

    def n_list_compr(self, node):
        """List comprehensions the way they are done in Python2.
        """
        n = node[-1]
        assert n == 'list_iter'
        # find innermost node
        while n == 'list_iter':
            n = n[0] # recurse one step
            if   n == 'list_for':	n = n[3]
            elif n == 'list_if':	n = n[2]
            elif n == 'list_if_not': n= n[2]
        assert n == 'lc_body'
        self.write( '[ ')
        self.preorder(n[0]) # lc_body
        self.preorder(node[-1]) # for/if parts
        self.write( ' ]')
        self.prune() # stop recursing

    def n_genexpr(self, node):
        self.write('(')
        code_index = -6 if self.version > 3.0 else -5
        self.comprehension_walk(node, iter_index=3, code_index=code_index)
        self.write(')')
        self.prune()

    def n_setcomp(self, node):
        self.write('{')
        self.comprehension_walk(node, iter_index=4)
        self.write('}')
        self.prune()

    def n_listcomp(self, node):
        self.write('[')
        if node[0].type == 'load_closure':
            self.listcomprehension_walk2(node)
        else:
            self.listcomprehension_walk3(node, 1, 0)
        self.write(']')
        self.prune()

    n_dictcomp = n_setcomp

    def n_classdef(self, node):
        # class definition ('class X(A,B,C):')
        cclass = self.currentclass

        if self.version > 3.0:
            currentclass = node[1][0].pattr
            buildclass = node[0]
            if buildclass[1][0] == 'kwargs':
                subclass = buildclass[1][1].attr
                subclass_info = node[0]
            elif buildclass[1][0] == 'load_closure':
                # Python 3 with closures not functions
                load_closure = buildclass[1]
                if hasattr(load_closure[-3], 'attr'):
                    # Python 3.3 classes with closures work like this.
                    # Note have to test before 3.2 case because
                    # index -2 also has an attr.
                    subclass = load_closure[-3].attr
                elif hasattr(load_closure[-2], 'attr'):
                    # Python 3.2 works like this
                    subclass = load_closure[-2].attr
                else:
                    raise 'Internal Error n_classdef: cannot find class body'
                if hasattr(buildclass[3], '__len__'):
                    subclass_info = buildclass[3]
                elif hasattr(buildclass[2], '__len__'):
                    subclass_info = buildclass[2]
                else:
                    raise 'Internal Error n_classdef: cannot superclass name'
            else:
                subclass = buildclass[1][0].attr
                subclass_info = node[0]
        else:
            buildclass = node if (node == 'classdefdeco2') else node[0]
            build_list = buildclass[1][0]
            if hasattr(buildclass[-3][0], 'attr'):
                subclass = buildclass[-3][0].attr
                currentclass = buildclass[0].pattr
            elif hasattr(node[0][0], 'pattr'):
                subclass = buildclass[-3][1].attr
                currentclass = node[0][0].pattr
            else:
                raise 'Internal Error n_classdef: cannot find class name'

        if (node == 'classdefdeco2'):
            self.write('\n')
        else:
            self.write('\n\n')

        self.currentclass = str(currentclass)
        self.write(self.indent, 'class ', self.currentclass)

        if self.version > 3.0:
            self.print_super_classes3(subclass_info)
        else:
            self.print_super_classes(build_list)
        self.println(':')

        # class body
        self.indentMore()
        self.build_class(subclass)
        self.indentLess()

        self.currentclass = cclass
        self.write('\n\n\n')

        self.prune()

    def print_super_classes(self, node):
        if not (node == 'build_list'):
            return

        self.write('(')
        line_separator = ', '
        sep = ''
        for elem in node[:-1]:
            value = self.traverse(elem)
            self.write(sep, value)
            sep = line_separator

        self.write(')')

    def print_super_classes3(self, node):
        n = len(node)-1
        if node.type != 'expr':
            assert node[n].type.startswith('CALL_FUNCTION')
            for i in range(n-2, 0, -1):
                if not node[i].type in ['expr', 'LOAD_CLASSNAME']:
                    break
                pass

            if i == n-2:
                return
            line_separator = ', '
            sep = ''
            self.write('(')
            i += 2
            while i < n:
                value = self.traverse(node[i])
                i += 1
                self.write(sep, value)
                sep = line_separator
                pass
            pass
        else:
            self.write('(')
            value = self.traverse(node[0])
            self.write(value)
            pass

        self.write(')')

    def n_mapexpr(self, node):
        """
        prettyprint a mapexpr
        'mapexpr' is something like k = {'a': 1, 'b': 42 }"
        """
        self.indentMore(INDENT_PER_LEVEL)
        line_seperator = ',\n' + self.indent
        sep = INDENT_PER_LEVEL[:-1]
        self.write('{')

        if self.version > 3.0:
            if node[0].type.startswith('kvlist'):
                # Python 3.5+ style key/value list in mapexpr
                kv_node = node[0]
                l = list(kv_node)
                i = 0
                while i < len(l):
                    name = self.traverse(l[i], indent='')
                    value = self.traverse(l[i+1], indent=self.indent+(len(name)+2)*' ')
                    self.write(sep, name, ': ', value)
                    sep = line_seperator
                    i += 2
                    pass
                pass
            elif node[1].type.startswith('kvlist'):
                # Python 3.0..3.4 style key/value list in mapexpr
                kv_node = node[1]
                l = list(kv_node)
                if len(l) > 0 and l[0].type == 'kv3':
                    # Python 3.2 does this
                    kv_node = node[1][0]
                    l = list(kv_node)
                i = 0
                while i < len(l):
                    name = self.traverse(l[i+1], indent='')
                    value = self.traverse(l[i], indent=self.indent+(len(name)+2)*' ')
                    self.write(sep, name, ': ', value)
                    sep = line_seperator
                    i += 3
                    pass
                pass
            pass
        else:
            # Python 2 style kvlist
            assert node[-1] == 'kvlist'
            kv_node = node[-1] # goto kvlist

            for kv in kv_node:
                assert kv in ('kv', 'kv2', 'kv3')
                # kv ::= DUP_TOP expr ROT_TWO expr STORE_SUBSCR
                # kv2 ::= DUP_TOP expr expr ROT_THREE STORE_SUBSCR
                # kv3 ::= expr expr STORE_MAP
                if kv == 'kv':
                    name = self.traverse(kv[-2], indent='')
                    value = self.traverse(kv[1], indent=self.indent+(len(name)+2)*' ')
                elif kv == 'kv2':
                    name = self.traverse(kv[1], indent='')
                    value = self.traverse(kv[-3], indent=self.indent+(len(name)+2)*' ')
                elif kv == 'kv3':
                    name = self.traverse(kv[-2], indent='')
                    value = self.traverse(kv[0], indent=self.indent+(len(name)+2)*' ')
                    self.write(sep, name, ': ', value)
                    sep = line_seperator
        self.write('}')
        self.indentLess(INDENT_PER_LEVEL)
        self.prune()

    def n_build_list(self, node):
        """
        prettyprint a list or tuple
        """
        lastnode = node.pop()
        lastnodetype = lastnode.type
        if lastnodetype.startswith('BUILD_LIST'):
            self.write('['); endchar = ']'
        elif lastnodetype.startswith('BUILD_TUPLE'):
            self.write('('); endchar = ')'
        elif lastnodetype.startswith('BUILD_SET'):
            self.write('{'); endchar = '}'
        elif lastnodetype.startswith('ROT_TWO'):
            self.write('('); endchar = ')'
        else:
            raise 'Internal Error: n_build_list expects list or tuple'

        flat_elems = []
        for elem in node:
            if elem == 'expr1024':
                for subelem in elem:
                        for subsubelem in subelem:
                            flat_elems.append(subsubelem)
            elif elem == 'expr32':
                for subelem in elem:
                    flat_elems.append(subelem)
            else:
                flat_elems.append(elem)

        self.indentMore(INDENT_PER_LEVEL)
        if lastnode.attr > 3:
            line_separator = ',\n' + self.indent
        else:
            line_separator = ', '
        sep = INDENT_PER_LEVEL[:-1]

        # FIXME:
        # if flat_elems > some_number, then group
        # do automatic wrapping
        for elem in flat_elems:
            if elem == 'ROT_THREE':
                continue
            assert elem == 'expr'
            value = self.traverse(elem)
            self.write(sep, value)
            sep = line_separator
        if lastnode.attr == 1 and lastnodetype.startswith('BUILD_TUPLE'):
            self.write(',')
        self.write(endchar)
        self.indentLess(INDENT_PER_LEVEL)

    def n_unpack(self, node):
        for n in node[1:]:
            if n[0].type == 'unpack':
                n[0].type = 'unpack_w_parens'
        self.default(node)

    n_unpack_w_parens = n_unpack

    def n_assign(self, node):
        # A horrible hack for Python 3.0 .. 3.2
        if 3.0 <= self.version <= 3.2 and len(node) == 2:
            if (node[0][0] == 'LOAD_FAST' and node[0][0].pattr == '__locals__' and
                node[1][0].type == 'STORE_LOCALS'):
                self.prune()
        self.default(node)

    def n_assign2(self, node):
        for n in node[-2:]:
            if n[0] == 'unpack':
                n[0].type = 'unpack_w_parens'
        self.default(node)

    def n_assign3(self, node):
        for n in node[-3:]:
            if n[0] == 'unpack':
                n[0].type = 'unpack_w_parens'
        self.default(node)

    def n_except_cond2(self, node):
        if node[5][0] == 'unpack':
            node[5][0].type = 'unpack_w_parens'
        self.default(node)

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
                # remaining = len(node[low:high])
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
            pass

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

    parser_debug = {'rules': False, 'transition': False, 'reduce': False,
                     'errorstack': True}
    parsed = parse_python2(python_stmts, show_tokens, parser_debug)
    assert parsed == 'file_input', 'Should have parsed grammar start'

    formatter = Python2Formatter()

    if showast:
        print(parsed)

    # What we've been waiting for: Generate source from AST!
    python2_formatted_str = formatter.format_python2(parsed)

    return python2_formatted_str

if __name__ == '__main__':
    def format_test(python2_stmts):
        "This is a docstring"
        formatted = format_python2_stmts(python2_stmts, show_tokens=False, showast=True)
        print('=' * 30)
        print(formatted)
        return
    format_test("from os import path")
    format_test("pass")
