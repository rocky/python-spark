import os.path as osp
import sys
mydir = osp.normpath(osp.dirname('__file__'))
sys.path.append(osp.normpath(osp.join(mydir, '..', '..')))
from gdbloc.parser import parse_bp_location, parse_range, parse_arange

def test_parser():
    for s in (
            "/tmp/foo.py:12",
            '''/tmp/foo.py:12''',
            '../foo.py:5',
            'gcd()',
            'foo.py:2 if x > 1',
            ):
        ast = parse_bp_location(s, show_tokens=True)
        print(ast)
        assert ast == 'bp_start'
        pass
    for s in (
            "10",
            "11 ,",
            "2 , 12",
            "2, 13",
            "3,  10",
            "sys.exit() , 20"
            ):
        ast = parse_range(s, show_tokens=True)
        print(ast)
        assert ast == 'range_start'
        pass
    for s in (
            "*0",
            "*1 ,",
            "2 , *14",
            "2, 15",
            "*3,  16",
            "sys.exit() , *20"
            ):
        ast = parse_arange(s, show_tokens=True)
        print(ast)
        assert ast == 'arange_start'
        pass
