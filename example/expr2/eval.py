#  Copyright (c) 2016 by Rocky Bernstein

"""Simple expression evaluator in SPARK
"""

from expr_parser import parse_expr
from spark_parser import GenericASTTraversal # , DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG

class ExprFormatterError(Exception):
    def __init__(self, errmsg):
        self.errmsg = errmsg

    def __str__(self):
        return self.errmsg

class ExprEvaluator(GenericASTTraversal, object):

    def __init__(self):
        GenericASTTraversal.__init__(self, ast=None)
        self.ERROR = None
        return

    def traverse(self, node):
        self.preorder(node)
        return node.value

    def n_NUMBER(self, node):
        node.value = complex(node.attr)
        self.prune()

    def n_atom(self, node):
        """atom ::= NUMBER | '(' expr ')' """
        length = len(node)
        if length == 1:
            self.preorder(node[0])
            node.value = node[0].value
            self.prune()
        elif length == 3:
            self.preorder(node[1])
            node.value = node[1].value
            self.prune()
        else:
            assert False, "Expecting atom to have length 1 or 3"

    def n_expr(self, node):
        """arith_expr ::= arith_expr ADD_OP term | term"""
        if len(node) == 1:
            self.preorder(node[0])
            node.value = node[0].value
            self.prune()
        else:
            self.preorder(node[0])
            self.preorder(node[2])
            if node[1].attr == '+':
                node.value = node[0].value + node[2].value
            elif node[1].attr == '-':
                node.value = node[0].value - node[2].value
            else:
                assert False, "Expecting operator to be '+' or '-'"
            self.prune()
        assert False, "Expecting atom to have length 1 or 3"

    def n_term(self, node):
        """term ::= term MULT_OP atom | atom"""
        if len(node) == 1:
            self.preorder(node[0])
            node.value = node[0].value
            self.prune()
        else:
            self.preorder(node[0])
            self.preorder(node[2])
            if node[1].attr == '*':
                node.value = node[0].value * node[2].value
            elif node[1].attr == '/':
                node.value = node[0].value / node[2].value
            else:
                assert False, "Expecting operator to be '*' or '/'"
            self.prune()
        assert False, "Expecting atom to have length 1 or 3"


def eval_expr(expr_str, show_tokens=False, showast=False,
              showgrammar=False, compile_mode='exec'):
    """
    evaluate simple expression
    """

    parser_debug = {'rules': False, 'transition': False,
                    'reduce': showgrammar,
                    'errorstack': True, 'context': True }
    parsed = parse_expr(expr_str, show_tokens=show_tokens,
                        parser_debug=parser_debug)
    if showast:
        print(parsed)

    assert parsed == 'expr', 'Should have parsed grammar start'

    evaluator = ExprEvaluator()

    # What we've been waiting for: Generate source from AST!
    return evaluator.traverse(parsed)


if __name__ == '__main__':
    def eval_test(eval_str):
        result = eval_expr(eval_str, show_tokens=False, showast=False,
                           showgrammar=False)
        print('%s = %s' % (eval_str, result))
        return
    eval_test("1")
    eval_test("1.0")
    eval_test("1 + 2")
    eval_test("1 * 2 + 3")
    eval_test("1 + 2 * 3")
    eval_test("(1 + 2) * 3")
