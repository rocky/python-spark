import unittest
from spark_parser import (GenericParser, PYTHON3)

if PYTHON3:
    from io import StringIO
else:
    from StringIO import StringIO


class BadExpr(GenericParser):
    """Testing grammar_checking"""
    def p_bad_rules(self, args):
        """
        expr  ::= expr ADD_OP term
        expr  ::= term

        term ::= factor
        factor ::= INTEGER

        # right recursive
        factor ::= FLOAT factor

        # duplicate RHS
        factor ::= expr ADD_OP term

        # foo is not on RHS and not a start symbol
        foo   ::= BAR
        """
        return
    pass

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
        parser = BadExpr('expr')
        f = StringIO()
        assert parser.check_grammar() > 0

        parser = Expr('expr')
        f = StringIO()
        parser.dump_grammar(f)
        expect = """START ::= |- expr
expr ::= expr ADD_OP term
expr ::= term
factor ::= INTEGER
term ::= factor
term ::= term MULT_OP factor
"""
        self.assertEqual(expect, f.getvalue())
        assert parser.check_grammar() == 0

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
        parser.dump_grammar(f)
        self.assertEqual(expect, f.getvalue())
        assert parser.check_grammar() == 0

        parser.remove_rules("expr ::= expr ADD_OP term")
        expect = """START ::= |- expr
expr ::= expr SUB_OP term
expr ::= term
factor ::= INTEGER
term ::= factor
term ::= term MULT_OP factor
"""
        f = StringIO()
        parser.dump_grammar(f)
        self.assertEqual(expect, f.getvalue())
        assert parser.check_grammar() == 0


if __name__ == '__main__':
    unittest.main()
