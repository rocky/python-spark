#  Copyright (c) 2016, 2020 by Rocky Bernstein

"""Simple expression evaluator in SPARK
"""

from expr_parser import parse_expr
from spark_parser import GenericASTTraversal  # , DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG
import operator

BINARY_OPERATORS = {
    "**": pow,
    "*": operator.mul,
    "/": operator.truediv,
    "//": operator.floordiv,
    "%": operator.mod,
    "+": operator.add,
    "-": operator.sub,
    "<<": operator.lshift,
    ">>": operator.rshift,
    "&": operator.and_,
    "^": operator.xor,
    "|": operator.or_,
}

BINOP_SET = frozenset(BINARY_OPERATORS.keys())

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
        if node.attr.find("j") >= 0:
            node.value = complex(node.attr)
        elif node.attr.find(".") > 0:
            node.value = float(node.attr)
        else:
            node.value = int(node.attr)
        self.prune()

    def n_BOOL(self, node):
        node.value = node.attr
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
        """
        expr ::= expr ADD_OP term | term
        term ::= term MULT_OP term | atom
        """

        if len(node) == 1:
            self.preorder(node[0])
            node.value = node[0].value
            self.prune()
        else:
            self.preorder(node[0])
            self.preorder(node[2])
            op = node[1].attr
            assert op in BINOP_SET, "Expecting operator to be in %s" % op
            node.value = BINARY_OPERATORS[node[1].attr](node[0].value, node[2].value)
            self.prune()
        assert False, "Expecting atom to have length 1 or 3"
    n_factor = n_term = n_expr


def eval_expr(
    expr_str,
    show_tokens=False,
    show_parse_tree=False,
    showgrammar=False,
    compile_mode="exec",
):
    """
    evaluate simple expression
    """

    parser_debug = {
        "rules": False,
        "transition": False,
        "reduce": showgrammar,
        "errorstack": True,
        "context": True,
    }
    parsed = parse_expr(expr_str, show_tokens=show_tokens, parser_debug=parser_debug)
    if show_parse_tree:
        print(parsed)

    assert parsed == "expr", "Should have parsed grammar start"

    evaluator = ExprEvaluator()

    # What we've been waiting for: Generate source from AST!
    return evaluator.traverse(parsed)


if __name__ == "__main__":

    def eval_test(eval_str):
        result = eval_expr(
            eval_str, show_tokens=False, show_parse_tree=True, showgrammar=False,
        )
        print("%s = %s" % (eval_str, result))
        return

    eval_test("1")
    eval_test("1.0")
    eval_test("1 + 2")
    eval_test("1 * 2 + 3")
    eval_test("1 + 2 * 3")
    eval_test("(1 + 2) * 3")
    eval_test("(10.5 + 2 * 5) // (2 << 1) / 5")
