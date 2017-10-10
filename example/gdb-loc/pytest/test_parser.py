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
            ("/tmp/foo.py line 12",
             ((0, 'FILENAME', "/tmp/foo.py's"),
              (11, 'SPACE', ' '),
              (12, 'FILENAME', "line"),
              (16, 'SPACE', ' '),
              (17, 'NUMBER', 12),)),
            ("12",
              ((17, 'NUMBER', 12),)),
            ('../foo.py:5',
             ((0, 'FILENAME', '../foo.py'), (9, 'COLON', ':'), (10, 'NUMBER', 5),)),
            ('gcd()',
             ((0, 'FUNCNAME', 'gcd()'),)),
            ('foo.py line 5 if x > 1',
             ((0, 'FILENAME', 'foo.py'),
              (6, 'SPACE', ' '),
              (7, 'FILENAME', 'line'),
              (11, 'SPACE', ' '),
              (12, 'NUMBER', 5),
              (13, 'SPACE', ' '),
              (14, 'IF', 'if'),
              (16, 'SPACE', ' '),
              (17, 'FILENAME', 'x'),
              (18, 'SPACE', ' '),
              (19, 'FILENAME', '>'),
              (20, 'SPACE', ' '),
              (21, 'NUMBER', 1),)),
            ):
        ast = parse_bp_location(s, show_tokens=True)
        print(ast)
        assert ast
        pass
