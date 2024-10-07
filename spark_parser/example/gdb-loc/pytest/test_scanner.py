import os.path as osp
import sys
mydir = osp.normpath(osp.dirname('__file__'))
sys.path.append(osp.normpath(osp.join(mydir, '..', '..')))
from gdbloc.scanner import LocationScanner
from gdbloc.tok import Token

def test_scanner():
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
            ('11',
             ((0, 'NUMBER', 11), )),
            ('2 ,',
             ((0, 'NUMBER', 2),
              (1, 'SPACE', ' '),
              (2, 'COMMA', ','),)),
            (',3',
             ((0, 'COMMA', ','),
              (1, 'NUMBER', '3'),)),
            ('4,10',
             ((0, 'NUMBER', 4),
              (1, 'COMMA', ','),
              (2, 'NUMBER', 10),)),
            ):
        tokens = LocationScanner().tokenize(s)
        for i, t in enumerate(tokens):
            e = Token(kind=expect[i][1], value=expect[i][2], offset=expect[i][0])
            assert t == e, i
            print(t)
            pass
        pass
