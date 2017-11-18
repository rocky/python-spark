#!/usr/bin/env python
"""
SPARK unit unit test grammar checking
"""
import unittest
from spark_parser.spark import GenericParser


class RightRecursive(GenericParser):
    """A simple expression parser for numbers and arithmetic operators: +, , *, and /.

    Note: methods that begin p_ have docstrings that are grammar rules interpreted
    by SPARK.
    """

    def __init__(self, start='expr'):
        GenericParser.__init__(self, start)

    def p_expr_right(self, args):
        """
        expr ::= term ADD expr
        expr ::= term
        term ::= NUMBER
        """

class UnexpandedNonterminal(GenericParser):
    def __init__(self, start='expr'):
        GenericParser.__init__(self, start)

    def p_expr_unexpanded(self, args):
        """
        expr ::= expr ADD term
        expr ::= term2
        term ::= NUMBER
        """

class UnusedLHS(GenericParser):
    def __init__(self, start='expr'):
        GenericParser.__init__(self, start)

    def p_unused_lhs(self, args):
        """
        expr ::= expr ADD term
        expr ::= term
        factor ::= term
        term ::= NUMBER
        """

class TestChecker(unittest.TestCase):

    def test_right_recursive(self):
        parser = RightRecursive()
        (lhs, rhs, tokens, right_recursive,
             dup_rhs) = parser.check_sets()
        self.assertEqual(len(lhs), 0)
        self.assertEqual(len(rhs), 0)
        self.assertEqual(len(right_recursive), 1)
        return

    def test_unexpanded_nonterminal(self):
        parser = UnexpandedNonterminal()
        (lhs, rhs, tokens, right_recursive,
             dup_rhs) = parser.check_sets()
        self.assertEqual(len(lhs), 0)
        expect = set(['term2'])
        self.assertEqual(expect, rhs)
        self.assertEqual(len(right_recursive), 0)
        return

    def test_used_lhs(self):
        parser = UnusedLHS()
        (lhs, rhs, tokens, right_recursive,
             dup_rhs) = parser.check_sets()
        expect = set(['factor'])
        self.assertEqual(expect, lhs)
        self.assertEqual(len(rhs), 0)
        self.assertEqual(len(right_recursive), 0)
        return
    pass


if __name__ == '__main__':
    unittest.main()
