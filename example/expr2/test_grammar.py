import os.path as osp
import sys
mydir = osp.normpath(osp.dirname('__file__'))
sys.path.append(osp.normpath(osp.join(mydir)))
import expr_parser

def test_grammar():
    """Show off check_sets to check a grammar"""
    p = expr_parser.ExprParser()
    lhs, rhs, tokens, right_recursive = p.check_sets()
    print(lhs)
    print(rhs)
    print(tokens)
    print(right_recursive)
    assert tokens == set("NUMBER LPAREN ADD_OP RPAREN MULT_OP".split())
    assert lhs == set([])
    assert rhs == set([])
    assert right_recursive == set([])
