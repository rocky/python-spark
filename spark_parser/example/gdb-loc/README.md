Here we parse and canocialize data for some gdb-like concepts that are
found in gdb or my Python [trepan](http://pypi.python.org/pypi/trepan3k) [debuggers](http://pypi.python.org/pypi/trepan2).

Specifically:

* "breakpoint" command positions with optional conditions
* "list" comand source text ranges

This could be done with a very complicated regular expression: there
is nothing in the way of nesting here. However breaking it up into two
levels I think helps clarity a lot.  And even what I have here is a
little bit complicated.

In the parsing, we use a reduction check so we can distinguish context
when an identifier is used as a filename or as a separator word like
"line" or "if". Again one could imagine fancy regular expression
engines that may be able to handle this, but I think it is simpler as
a two-level parse.

Here are examples of breakpoint positions:

    /tmp/foo.py:12          # file foo.py line 12
	/tmp/foo.py line 12     # same thing
	foo.py 12               # same thing if the current directory is /tmp
	../foo.py               # same thing if the current directory is /tmp/bar
	gcd()                   # method gcd
	"""MacOSX Folder/foo.py""" line 5   # Note space in directory name
	"""c:\My Documents\program.py""":5  # This is how we can specify a Windows drive

Breakpoint positions can have conditions attached as well:

	gcd() if x > 1          # method breakpoint with a condition
	foo.py line 5 if x > 1  # file breakpoint with a condition
	foo.py:5 if x > 1       # same as above


Here are examples of list ranges:

    /tmp/foo.py:12 , 5    # Start at line 12 of /tmp/foo.py and list 5 lines
    -                     # list before where we last listed
    +                     # list after where we last listed
    ../foo.py:5           # list
    ../foo.py:5 ,
    , 5                   # list ending at line 5
    ,5                    # Same as above
    ,/foo.py:5


Note that when something isn't a symbol like "+", or "-" it is a
location. Of course, there can't be a condition here because that is
meaningless.

The result of walking the tree is a named tuple structure that
contains the information extracted and canonicalized.

Here are the structures we parse the above into:

    Location = namedtuple("Location", "path line_number method")
    BPLocation = namedtuple("BPLocation", "location condition")
    ListRange = namedtuple("ListRange", "first last")

The way we fill in information for the structure `ListRange` is
perhaps a bit odd. We don't do any really check whether a filename or
or method name exits. We also don't know where a function starts, just
that the user indicated that the value was a function.

Likewise we don't know where the next default line to list would be
when it is not explictly given. In cases where a line number needs to
be filled out by the debugger, the string "."  is used.  Otherwise the
value for first or last in a `ListRange` should be a `Location` type
which has this information.

Similarly exactly how many lines are listed in the forward or backward
direction when "+' and "-" is given or when it is not explictly
specified is computed here, but in the application or debugger that
uses this.


Side note: note how much attention is put into mimicking gdb's command
interface in the trepan debuggers.
