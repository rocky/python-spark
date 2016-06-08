Some of examples of using SPARK.

Two both show off the classic expression parsing. `expr` is the simpler:
it's everything all rolled into one file

`expr2` has more complete grammar rules. And the scanner is split off
from the parser.

The largest and more complete example is a formatter for Python
2.6. It reads in valid Python 2.6, parses it and builds an abstract
syntax tree. Then it prints it back out according to some table-driven
formatting rules. It is left incomplete.

After you've mastered this, consider going onto uncompyle2 which
turne Python bytecode (many versions) into Python.

There is plenty of room improvement for each program, but that is
somewhat deliberate. The hope is that you'll modify these to
improve them and understand how things work.

And if you have improvements or other examples, pass them along and
we'll add them.
