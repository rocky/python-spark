import os.path as osp
import sys

mydir = osp.normpath(osp.dirname("__file__"))
sys.path.append(osp.normpath(osp.join(mydir)))
import expr_parser


def test_grammar():
    """Show off check_sets to check a grammar"""
    p = expr_parser.ExprParser()
    missing_lhs, missing_rhs, token_set, right_recursive, dup_rhs = p.check_sets()
    print("LHS nonterminals missing from the RHS of some rule:", missing_lhs)
    print("RHS nonterminals that aren't the LHS of some rule:", missing_rhs)
    print("set of tokens:", token_set)
    print("Rules which have the same RHS (so might be combined):", dup_rhs)
    print(
        "Right recursive rules which aren't (yet) handled efficiently", right_recursive
    )
    assert token_set == set("NUMBER LPAREN ADD_OP RPAREN MULT_OP".split())
    assert missing_lhs == set([])
    assert missing_rhs == set([])
    assert right_recursive == set([])


if __name__ == "__main__":
    test_grammar()
