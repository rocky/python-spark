import collections, sys, unittest
from spark_parser.spark import GenericParser

class Rules(GenericParser):
    """Testing duplicate rules"""
    def p_rules(self, args):
        """
        x ::= TOKEN
        x ::= TOKEN

        stmts ::= stmt+
        """
        pass

    def duplicate_rule(self, rule):
        if not hasattr(self, 'dups'):
            self.dups = []
        self.dups.append(rule)
    pass

class TestMisc(unittest.TestCase):

    def test_basic(self):
        # Check duplicate rule detection
        parser = Rules('x', debug={'dups': True})
        self.assertTrue(hasattr(parser, 'dups'))
        self.assertEqual(parser.dups, [('x', ('TOKEN',))])

        # Check "+" expansion
        if sys.version_info[0] + (sys.version_info[1] / 10.0) >= 2.7:
            rules = collections.OrderedDict(sorted(parser.rule2name.items()))
            self.assertEqual(rules,
                             collections.OrderedDict([(('START', ('|-', 'x')), 'ambda>'),
                                                      (('stmts', ('stmt',)), 'rules'),
                                                      (('stmts', ('stmts', 'stmt')), 'rules'),
                                                      (('x', ('TOKEN',)), 'rules')]))

if __name__ == '__main__':
    unittest.main()
