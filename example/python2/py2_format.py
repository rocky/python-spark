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
    'global_stmt':	( '%|global %C\n', (1, maxint, '')),
    'pass_stmt':        ( '%|pass\n', ),
    'return_stmt':      ( '%|return %c\n', 1),
    'testlist':         ( '%C', (1, maxint, ', ') ),
    'import_from':      ( '%|from %c import %c\n', 1, 2 ),
    'import_name':      ( '%|import %c\n', 1 ),
    'newline_or_stmt':  ('%c', 0),
    'if_stmt':	        ( '%|if %c:\n%+%c%-%c%-%c', 1, 3, 4, 5),
    'elif_suites':	( '%|elif %c:\n%?%+%c%-', 2, 4),
    'comma_name':	( ', %c', 1),
    'comma_dotted_as_names': ('%C', (1, maxint, ', ') ),
    'while_stmt':	( '%|while %c:\n%+%c%-', 1, 3),
    'funcdef':          ( '%|def %c(%c):\n%+%c%-\n\n', 1, 2 , 4 ),


    'NAME':	( '%{attr}', ),
    'STRING':	( '%{attr}', ),
    'NUMBER':	( '%{attr}', ),
    'DOT':	( '.', ),

}

MAP_DIRECT = (TABLE_DIRECT, )
MAP_R0 = (TABLE_R0, -1, 0)
MAP_R = (TABLE_R, -1)

MAP = {
    'file_input':	MAP_R,
    'stmt':		MAP_R,
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

    def n_exprlist(self, node):
        self.preorder(node[0])
        self.preorder(node[1])
        self.preorder(node[2])
        self.prune() # stop recursing

    def n_yield(self, node):
        self.write('yield')
        self.write(' ')
        self.preorder(node[0])
        self.prune() # stop recursing

    def n_binary_expr(self, node):
        self.preorder(node[0])
        self.write(' ')
        self.preorder(node[-1])
        self.write(' ')
        self.preorder(node[1])
        self.prune()

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
            self.write(self.indent, 'elif ')
            self.preorder(node[2])
            self.println(':')
            self.indentMore()
            self.preorder(node[4])
            self.indentLess()
            self.prune()

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
            try:
                key = key[i]
            except:
                from trepan.api import debug; debug()
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
        "This is a docstring"
        formatted = format_python2_stmts(python2_stmts, show_tokens=False, showast=True)
        print('=' * 30)
        print(formatted)
        return
    # format_test("from os import path")
    # format_test("pass")
    format_test("""
while True:
    if False:
        continue

pass
""")
#     format_test("""
# if True:
#   if True:
#      pass
# pass

# """)
