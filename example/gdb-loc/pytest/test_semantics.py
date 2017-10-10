import os.path as osp
import sys
mydir = osp.normpath(osp.dirname('__file__'))
sys.path.append(osp.normpath(osp.join(mydir, '..', '..')))
from gdbloc.semantics import build_range, build_bp_expr, ListRange, Location, BPLocation

def test_semantics():
    for s, expect in (
            ("-",
             ListRange(first='.', last='-')),
            ("+",
             ListRange(first='.', last='+')),
            ("/tmp/foo.py:12",
             ListRange(first=Location(path='/tmp/foo.py', line_number=12, method=None), last='.')),
            (", 5",
             ListRange(first='.', last=Location(path=None, line_number=5, method=None))),
            (", foo.py:14",
             ListRange(first='.', last=Location(path='foo.py', line_number=14, method=None))),
            ):
        list_range = build_range(s)
        # print(list_range)
        assert list_range == expect
        pass
    for s, expect in (
            ("/tmp/foo.py:13",
             BPLocation(Location(path='/tmp/foo.py', line_number=13, method=None),
                        condition=None)),
            ("/tmp/foo.py:9 if x > 1",
             BPLocation(Location(path='/tmp/foo.py', line_number=9, method=None),
                        condition='if x > 1')),
            ):
        bp_expr = build_bp_expr(s)
        # print(bp_expr)
        assert bp_expr == expect
        pass
