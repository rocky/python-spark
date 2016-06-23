This directory contains a more complete example of using SPARK to scan, parse,
generate an abstract tree, and do something what that tree.

Specifically, here we handle the Python 2.6 grammar. File
[python26.gr](http://github.com/rocky/python-spark/tree/master/example/python2/python26.gr)
is the grammar as we found it in the Python 2.6.9 distribution.

Although this is woefully incomplete, the structure for how to proceed
is straightforward.

The individual Python modules:

## Scanner

`py_scan.py` is a Python scanner. The docstrings for methods that
start `t_` give regular expressions are matched against the input
string. When there is a match that method is called with the string as
a parameter. Python is weird in that you need to parse newlines as
tokens. In contrast to Python's scanner, we also want to keep track of
comments.

## Parser

`py_parse.py` is a SPARK parser recognizing Python 2.6. The
docstrings for methods that start `p_` are read as grammar rules. In
contrast to Python's parser, we want to save and _count_ newline
information, as well as save comments that appear at the end of a
line or are the only thing on a line. At the end of successful
parsing and Abstract Syntax Tree (AST) is created. Some rules are
used to tidy the tree up by removing

* epsilon reductions
* singleton derivations (used mostly in lists and for precidence)
* flattening out list of items such statements or argument lists.

## Formatter

`py_format.py` are semantic actions that are performed on the abstrict
is a SPARK parser recognizing Python 2.6. The methods that start `n_`
and whose suffix is the same name as a non-terminal is called in
traversing the AST. However the code in note-traversal method can

* decide how to process its child nodes. `self.preorder(n)` will
cause node _n_ to be processed.
* stop its parent from further traversal of sibling nodes. This is done by calling `self.prune()`.

Since a lot of the semantic actions is repetitive, there various patterns
can be dictated by table-driven rules. The method `engine` handles this.
