import unittest
from spark_parser.spark import GenericParser

from StringIO import StringIO

class Rules(GenericParser):
    """Testing duplicate rules"""
    def p_rules(self, args):
        """
        x ::= TOKEN
        x ::= TOKEN

        stmts ::= stmt+
        ratings ::= STARS*
        """
        pass

    def duplicate_rule(self, rule):
        if not hasattr(self, 'dups'):
            self.dups = []
        self.dups.append(rule)
    pass

class RulesPeriod(GenericParser):
    """Testing ? extended rule"""
    def p_rules(self, args):
        """
        opt_period ::= PERIOD?
        """
        pass
    pass

class InvalidRule(GenericParser):
    """Testing illegal recursive rule"""
    def p_rules(self, args):
        """
        foo ::= foo
        """
        pass
    pass

class TestMisc(unittest.TestCase):

    def test_basic(self):
        # Check duplicate rule detection
        parser = Rules('x', debug={'dups': True})
        self.assertEqual(True, hasattr(parser, 'dups'))
        self.assertEqual(parser.dups, [('x', ('TOKEN',))])

        # Check "+", and "*", expansion
        rules = parser.rule2name.items()
        rules.sort()
        self.assertEqual(rules,
                         [(('START', ('|-', 'x')), 'ambda>'),
                          (('ratings', ()), 'rules'),
                          (('ratings', ('ratings', 'STARS')), 'rules'),
                          (('stmts', ('stmt',)), 'rules'),
                          (('stmts', ('stmts', 'stmt')), 'rules'),
                          (('x', ('TOKEN',)), 'rules')])
        f = StringIO()
        expect = \
"""START ::= |- x
ratings ::=
ratings ::= ratings STARS
stmts ::= stmt
stmts ::= stmts stmt
x ::= TOKEN
"""
        parser.dump_grammar(f)
        self.assertEqual(f.getvalue(), expect)

        # Check Invalid rule
        try:
            InvalidRule('foo', debug={'dups': True})
            self.assertTrue(False)
        except TypeError:
            self.assertEqual(True, True)

        self.assertEqual(set(['stmts', 'ratings']),  parser.list_like_nt)
        self.assertEqual(set(),  parser.optional_nt)

        # Check erroneous start symbol
        try:
            parser = Rules('bad-start')
            self.assertEqual(False, True)
        except TypeError:
            self.assertEqual(True, True)

    def test_period(self):
        parser = RulesPeriod('opt_period', debug={'dups': True})

        # Check "?" expansion
        rules = parser.rule2name.items()
        rules.sort()
        self.assertEqual(rules,
                         [(('START', ('|-', 'opt_period')), 'ambda>'),
                          (('opt_period', ()), 'rules'),
                          (('opt_period', ('PERIOD',)), 'rules'), ])
        self.assertEqual(set(['opt_period']),  parser.optional_nt)


if __name__ == '__main__':
    unittest.main()
