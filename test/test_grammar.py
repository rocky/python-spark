import unittest
from spark_parser.spark import GenericParser

from StringIO import StringIO


class Expr(GenericParser):
    """Testing DumpGrammar, adding a rule and removing a rule"""
    def p_rules(self, args):
        """
        expr ::= expr ADD_OP term
        expr ::= term
        term ::= term MULT_OP factor
        term ::= factor
        factor ::= INTEGER
        """
        return
    pass

nop_func = lambda self, args: None

class TestGrammar(unittest.TestCase):

    def test_basic(self):
        parser = Expr('expr')
        f = StringIO()
        parser.dumpGrammar(f)
        expect = """START ::= |- expr
expr ::= expr ADD_OP term
expr ::= term
factor ::= INTEGER
term ::= factor
term ::= term MULT_OP factor
"""
        self.assertEqual(expect, f.getvalue())

        parser.addRule("expr ::= expr SUB_OP term", nop_func)
        expect = """START ::= |- expr
expr ::= expr ADD_OP term
expr ::= expr SUB_OP term
expr ::= term
factor ::= INTEGER
term ::= factor
term ::= term MULT_OP factor
"""
        f = StringIO()
        parser.dumpGrammar(f)
        self.assertEqual(expect, f.getvalue())

        parser.remove_rule("expr ::= expr ADD_OP term")
        expect = """START ::= |- expr
expr ::= expr SUB_OP term
expr ::= term
factor ::= INTEGER
term ::= factor
term ::= term MULT_OP factor
"""
        f = StringIO()
        parser.dumpGrammar(f)
        self.assertEqual(expect, f.getvalue())


if __name__ == '__main__':
    unittest.main()
