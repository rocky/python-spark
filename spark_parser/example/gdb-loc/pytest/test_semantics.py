import os.path as osp
import sys
mydir = osp.normpath(osp.dirname('__file__'))
sys.path.append(osp.normpath(osp.join(mydir, '..', '..')))
from gdbloc.semantics import build_range, build_bp_expr, ListRange, Location, BPLocation

def test_semantics():
    for s, expect in (
            ( "/tmp/foo.py:12",
              ListRange(first=Location(path='/tmp/foo.py', line_number=12, is_address=False, method=None),
                       last=None) ),
            (", 5",
              ListRange(first=None, last=Location(path=None, line_number=5, is_address=False,
                                                 method=None))),
            (", foo.py:14",
             ListRange(first=None, last=Location(path='foo.py', line_number=14, is_address=False,
                                                method=None))),
            ):
        list_range = build_range(s)
        # print(list_range)
        assert list_range == expect
        pass
    for s, expect in (
            ("/tmp/foo.py:13",
             BPLocation(Location(path='/tmp/foo.py', line_number=13, is_address=False, method=None),
                        condition=None)),
            ("/tmp/foo.py:9 if x > 1",
             BPLocation(Location(path='/tmp/foo.py', line_number=9, is_address=False, method=None),
                        condition='if x > 1')),
            ):
        bp_expr = build_bp_expr(s)
        # print(bp_expr)
        assert bp_expr == expect
        pass
