Some of examples of using SPARK.

Two both show off the classic expression parsing. `expr` is the simpler:
it's everything all rolled into one file

`expr2` has more complete grammar rules. And the scanner is split off
from the parser. Down the line we'll probably add a fancier ast evaluation
mechanism distilled from uncompyle6.

The largest and more complete example is a formatter for Python
2.6. It reads in valid Python 2.6, parses it and builds an abstract
syntax try. Then it prints it back out according to some table-driven
formatting rules. After you've mastered this, consider going onto
uncompyle2 which turnes Python bytecode (many versions) into Python.

There is plenty of room improvement for each program, but that is
somewhat deliberate. The hope is that you'll modify these to
understand how things work.

And if you have improvements or other examples, pass them along and
we'll add them.
