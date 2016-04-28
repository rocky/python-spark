#!/usr/bin/env python
"""
SPARK example to parse simple arithmetic expressions
"""
import re, sys
from spark_parser import GenericParser, GenericASTTraversal
from spark_parser import AST
from spark_parser.scanner import GenericScanner, GenericToken

class ExprScanner(GenericScanner):

    def __init__(self):
        GenericScanner.__init__(self)

    def tokenize(self, input):
        self.rv = []
        GenericScanner.tokenize(self, input)
        return self.rv

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
        r'[+-]'
        t = GenericToken(type='add_op', attr=s)
        self.rv.append(t)

    def t_mult(self, s):
        r'[/*]'
        t = GenericToken(type='mult_op', attr=s)
        self.rv.append(t)

    # Recognize integers
    def t_integer(self, s):
        r'\d+'
        t = GenericToken(type='integer', attr=s)
        self.rv.append(t)

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

    # Below are methods for the grammar rules and the AST tree-building
    # action to take

    def p_expr_add_term(self, args):
        ' expr ::= expr add_op term '
        op = 'add' if args[1].attr ==  '+' else 'subtract'
        return AST(op, [args[0], args[2]])

    def p_expr2term2(self, args):
        ' expr ::= term '
        return AST('single', [args[0]])

    def p_term_mult_factor(self, args):
        ' term ::= term mult_op factor '
        op = 'multiply' if args[1].attr ==  '*' else 'divide'
        return AST(op, [args[0], args[2]])

    def p_term2single(self, args):
        ' term ::= factor '
        return AST('single', [args[0]])

    def p_factor2integer(self, args):
        ' factor ::= integer '
        return AST('single', [args[0]])

class Interpret(GenericASTTraversal):

    def __init__(self, ast):
        GenericASTTraversal.__init__(self, ast)
        self.postorder(ast)
        self.value = ast.value

    # Rules for interpreting nodes based on their AST node type
    def n_integer(self, node):
        node.value = int(node.attr)

    def n_single(self, node):
        node.value = node.data[0].value

    def n_multiply(self, node):
        node.value = node[0].value * node[1].value

    def n_divide(self, node):
        node.value = node[0].value / node[1].value

    def n_add(self, node):
        node.value = node[0].value + node[1].value

    def n_subtract(self, node):
        node.value = node[0].value - node[1].value

    def default(self, node):
        pass

def scan_expression(data):
    """
    Tokenize *filename* into integers, numbers, and operators
    """
    scanner = ExprScanner()
    return scanner.tokenize(data)

def parse_expression(tokens):
    parser = ExprParser()
    return parser.parse(tokens)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        filename = 'expr1.txt'
        data = open(filename).read()
    elif len(sys.argv) == 2:
        if sys.argv[1] in ['-h', '--help']:
            print(""""usage: %s [filename | expression ]""" %
                      sys.argv[0])
            sys.exit(1)
        filename = sys.argv[1]
        data = open(filename).read()
    else:
        data = ' '.join(sys.argv[1:])
    print(data)
    tokens = scan_expression(data)
    print(tokens)
    tree = parse_expression(tokens)
    print(tree)
    i = Interpret(tree)
    print("Final value is: %d" % i.value)
