Here we parse breakpoint positions with optional conditions as are
found in gdb or some of my trepanning debuggers.

In fact most of this could be done with a very complicated regular expression.
However breaking it up into two levels I think helps clarity a lot.

In the parsing part using a reduction check we can distinguish context
when an identifier is used as a filename or as a separator word like
"line" or "if". Again one could imagine fancy regular expression
engines that may be able to handle this, but I think it is simpler
as a two-level parse.

Examples of breakpoint positions:

    /tmp/foo.py:12          # file foo.py line 12
	/tmp/foo.py line 12     # same thing
	foo.py 12               # same thing if the current directory is /tmp
	../foo.py               # same thing if the current directory is /tmp/bar
	gcd()                   # method gcd
	gcd() if x > 1          # method breakpoint with a condition
	foo.py line 5 if x > 1  # file breakpoint with a condition
	foo.py:5 if x > 1       # same as above
