import os.path as osp
import sys
mydir = osp.normpath(osp.dirname('__file__'))
sys.path.append(osp.normpath(osp.join(mydir, '..', '..')))
from gdbloc.parser import parse_bp_location

def test_parser():
    for s, expect in (
            ("/tmp/foo.py:12",
             ((0, 'FILENAME', '/tmp/foo.py'), (11, 'COLON', None), (12, 'NUMBER', 12),)),
            ('''/tmp/foo.py:12''',
             ((0, 'FILENAME', '/tmp/foo.py'), (11, 'COLON', None), (12, 'NUMBER', 12),)),
            ("12",
              ((17, 'NUMBER', 12),)),
            ('../foo.py:5',
             ((0, 'FILENAME', '../foo.py'), (9, 'COLON', ':'), (10, 'NUMBER', 5),)),
            ('gcd()',
             ((0, 'FUNCNAME', 'gcd()'),)),
            ('foo.py:2 if x > 1',
             ((0, 'FILENAME', 'foo.py'),
              (6, 'COLON', ' '),
              (7, 'NUMBER', 2),
              (8, 'SPACE', ' '),
              (9, 'IF', 'if'),
              (11, 'SPACE', ' '),
              (12, 'FILENAME', 'x'),
              (13, 'SPACE', ' '),
              (14, 'FILENAME', '>'),
              (15, 'SPACE', ' '),
              (16, 'NUMBER', 1),)),
            ):
        ast = parse_bp_location(s, show_tokens=True)
        print(ast)
        assert ast
        pass
