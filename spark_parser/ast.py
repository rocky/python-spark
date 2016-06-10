import sys

PYTHON3 = (sys.version_info >= (3, 0))

if PYTHON3:
    intern = sys.intern
    from collections import UserList
else:
    from UserList import UserList


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
        rv = str(self.type)
        for k in self:
            rv = rv + '\n' + str(k).replace('\n', '\n   ')
        return rv

class GenericASTTraversalPruningException(BaseException):
    pass

class GenericASTTraversal:
    '''
    GenericASTTraversal is a Visitor pattern according to Design Patterns.  For
    each node it attempts to invoke the method n_<node type>, falling
    back onto the default() method if the n_* can't be found.  The preorder
    traversal also looks for an exit hook named n_<node type>_exit (no default
    routine is called if it's not found).  To prematurely halt traversal
    of a subtree, call the prune() method -- this only makes sense for a
    preorder traversal.  Node type is determined via the typestring() method.
    '''
    def __init__(self, ast):
        self.ast = ast

    def typestring(self, node):
        return node.type

    def prune(self):
        raise GenericASTTraversalPruningException

    def preorder(self, node=None):
        """Walk the tree in preorder.
        For each node with typestring name *name* if the
        node has a method called n_*name*, call that before walking
        children. If there is no method define, call a
        self.default(node) instead. Subclasses of GenericASTTtraversal
        ill probably want to override this method.

        If the node has a method called *name*_exit, that is called
        after all children have been called.  So in this sense this
        function is both preorder and postorder combined.
        """
        if node is None:
            node = self.ast

        try:
            name = 'n_' + self.typestring(node)
            if hasattr(self, name):
                func = getattr(self, name)
                func(node)
            else:
                self.default(node)
        except GenericASTTraversalPruningException:
            return

        for kid in node:
            self.preorder(kid)

        name = name + '_exit'
        if hasattr(self, name):
            func = getattr(self, name)
            func(node)

    def postorder(self, node=None):
        """Walk the tree in postorder.
        For each node with typestring name *name* if the
        node has a method called n_*name*, call that before walking
        children. If there is no method define, call a
        self.default(node) instead. Subclasses of GenericASTTtraversal
        ill probably want to override this method.

        If the node has a method called *name*_exit, that is called
        after all children have been called.  So in this sense this
        function is both preorder and postorder combined.
        """
        if node is None:
            node = self.ast

        try:
            first = iter(node)
        except TypeError:
            first = None

        if first:
            for kid in node:
                self.postorder(kid)

        try:
            name = 'n_' + self.typestring(node)
            if hasattr(self, name):
                func = getattr(self, name)
                func(node)
            else:
                self.default(node)
        except GenericASTTraversalPruningException:
            return

        name = name + '_exit'
        if hasattr(self, name):
            func = getattr(self, name)
            func(node)

    def default(self, node):
        """Default acttion to take on an ASTNode. Our defualt is to do nothing.
        Subclasses will probably want to define this for other behavior."""
        pass
