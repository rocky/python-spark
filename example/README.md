In this folder we have some of examples of using this Earley-Algorithm parser.

Two examples show off the classic expression
parsing. [`expr`](http://github.com/rocky/python-spark/tree/master/example/expr)
is the simpler of the two: it's everything all rolled into one file

[`expr2`](http://github.com/rocky/python-spark/tree/master/example/expr2)
has more complete grammar rules. And the scanner is split off from the
parser. The pytest program `test_grammar.py` shows off using the parser
*check_grammar()* function to make sure that there are no extraneous
nonterminals in left-hand or right-hand grammar rules.

[gdb-loc](http://github.com/rocky/python-spark/tree/master/example/gdb-loc)
has code for understanding gdb breakpoint locations (with optional
condition) and "list" command ranges. I use this in my [Python trepan
debugger](http://pypi.python.org/pypi/trepan3k)

A large example is
[`python2`](http://github.com/rocky/python-spark/tree/master/example/python2)
a somewhat lame formatter for Python 2.6. It reads in valid Python
2.6, parses it and builds an abstract syntax tree. Then it prints it
back out according to some table-driven formatting rules. It is left
incomplete.

After you've mastered this, consider going on to
[uncompyle6](http://pypi.python.org/pypi/uncompyle6) which turns
Python bytecode back into Python.

Another bytecode decompiler that might be used as an example is the
one I am working on to decompile [Emacs
Lisp](http://github.com/rocky/elisp-decompile).

There is plenty of room improvement for each the programs. Sometimes
it is somewhat deliberate. The hope is that you'll modify these to
improve them and understand how things work.

And if you have improvements or other examples, pass them along and
we'll add them.
