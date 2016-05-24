import sys

PYTHON3 = (sys.version_info >= (3, 0))

if PYTHON3:
    intern = sys.intern
    from collections import UserList
else:
    from UserList import UserList

indent_symbols = ['\xb7','|','*','+',':','!'] #STRANIKS_SCAN 04/04/2016
current_indsym = indent_symbols[:]

class AST(UserList):
    def __init__(self, kind, kids=[]):
        self.type = intern(kind)
        UserList.__init__(self, kids)

    def __getslice__(self, low, high):
        return self.data[low:high]

    def __eq__(self, o):
        if isinstance(o, AST):
            return (self.type == o.type and
                    UserList.__eq__(self, o))
        else:
            return self.type == o

    def __hash__(self):
        return hash(self.type)

    def __repr__(self, indent=''):
        global current_indsym #STRANIKS_SCAN 04/04/2016
        rv = str(self.type)
        if not current_indsym:
            current_indsym = indent_symbols[:]
        indsym = current_indsym.pop(0)
        for k in self:
            rv = rv + '\n' + str(k).lstrip(' \t').replace('\n', '\n%s   ' % indsym)
        return rv
