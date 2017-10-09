#  Copyright (c) 2017 by Rocky Bernstein
from __future__ import print_function

from gdbloc.parser import parse_bp_location
from spark_parser import GenericASTTraversal # , DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG
from spark_parser.ast import GenericASTTraversalPruningException

from collections import namedtuple
Location = namedtuple("Location", "path line_number method condition")
ListRange = namedtuple("ListRange", "location end_number")


class LocationError(Exception):
    def __init__(self, errmsg):
        self.errmsg = errmsg

    def __str__(self):
        return self.errmsg

class LocationGrok(GenericASTTraversal, object):

    def __init__(self, text):
        GenericASTTraversal.__init__(self, None)
        self.text = text
        self.location = None
        return

    def n_location(self, node):
        path, line_number, method = None, None, None
        if node[0] == 'FILENAME':
            path = node[0].value
            # If there is a line number, it is the last token of a location
            if len(node) > 1 and node[-1] == 'NUMBER':
                line_number = node[-1].value
        elif node[0] == 'FUNCNAME':
            method = node[0].value[:-2]
        elif node[0] == 'NUMBER':
            line_number = node[0].value
        else:
            assert True, "n_location: Something's is wrong; node[0] is %s" % node[0]
        self.location = Location(path, line_number, method, None)
        self.prune()

    def n_NUMBER(self, node):
        self.location = Location(None, node.value, None, None)

    def n_FUNCNAME(self, node):
        self.location = Location(None, None, node.value[:-2], None)

    def n_location_if(self, node):
        if node[0] == 'location':
            try:
                self.n_location(node[0])
            except GenericASTTraversalPruningException:
                pass

        if len(node) == 1:
            return
        if node[1] == 'IF':
            if_node = node[1]
        elif node[2] == 'IF':
            if_node = node[2]
        elif node[3] == 'IF':
            if_node = node[3]
        else:
            assert False, 'location_if: Something is wrong; cannot find "if"'

        condition = self.text[if_node.offset:]

        # Pick out condition from string and location inside "IF" token
        self.location = Location(self.location.path, self.location.line_number,
                                 self.location.method, condition)
        self.prune()

    def n_range(self, node):
        # FIXME: start here
        self.location = ListRange(None, None)

    def default(self, node):
        if node not in frozenset(("""opt_space tokens token bp_start range_start
                                  IF FILENAME COLON SPACE""".split())):
            assert False, ("Something's wrong: you missed a rule for %s" % node.kind)

    def traverse(self, node, ):
        return self.preorder(node)


def main(string, show_tokens=False, show_ast=False, show_grammar=False):
    parser_debug = {'rules': False, 'transition': False,
                    'reduce': show_grammar,
                    'errorstack': True, 'context': True, 'dups': True }
    parsed = parse_bp_location(string, show_tokens=show_tokens,
                               parser_debug=parser_debug)
    assert parsed == 'bp_start'
    walker = LocationGrok(string)
    walker.traverse(parsed)
    location = walker.location
    assert location.line_number is not None or location.method
    return location

if __name__ == '__main__':
    lines = """
    /tmp/foo.py:12
    /tmp/foo.py line 12
    12
    ../foo.py:5
    gcd()
    foo.py line 5 if x > 1
    """.splitlines()
    for line in lines:
        if not line.strip():
            continue
        print("=" * 30)
        print(line)
        print("+" * 30)
        location = main(line)
        print(location)
