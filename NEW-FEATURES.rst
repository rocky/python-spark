The original version of this Earley parser, circa 2000, was pretty awesome for its
age.  It was remarkably fast, and small: one Python file. Some care
was put into making it run fast.

That made it easy to embed in a project. In fact at one time it was
added to the Python distribution before it was removed in a later version.

But embedding the code was the only option for over a decade.  Nor
were there any automated tests for the program. And simple usuable
examples were lacking. (I'm not sure I have been totally successful at
addressing this, but what's here now is a much better start.)

Many of the changes I've added come from using the program. I list
features aside from the packaging, tests, and examples mentioned above.

The first thing I desired when working with a large complex grammar
and then sets of grammars that I found desirable was the ability to
comment the grammar. For example:

.. code-block::

    # This is a comment
    term := term MULT_OP atom


Next, I needed better AST tree display routines. For example:

.. code-block::

    expr
      term (3)
        0. term
          atom (3)
            0. type: LPAREN, value: '('
            1. expr (3)
              0. expr
                type: NUMBER, value: '1'
              1. type: ADD_OP, value: '+'
              2. term
                type: NUMBER, value: '3'
            2. type: RPAREN, value: ')'
        1. type: MULT_OP, value: '/'
        2. atom
          type: NUMBER, value: '2'

After that it was useful to have grammar checking routines,
specifically, the ability to find unused left-hand-side nonterminals
that are not either the start symbol or used on the right-hand side.
Likewise unused nonterminals (lower-case symbols) that appear on the
right-hand side that are not defined as a rule. Of course, tokens or
upper-case symbols are ok.

Checking for duplicate rules was also handy.

The original code showed you the how far you had parsed and that was
useful. But in production code you often want more. So I added the
list of rule states of the current state. I won't show that here.

However also added was the ability to dump rules as reductions
occurred. Here is an example of that from uncompyle6:

.. code-block::

    x = 1
    y = x + 5


    # This is the disassembly for the above
    L.   1       0  LOAD_CONST            0  1
                 3  STORE_NAME            0  'x'

    L.   2       6  LOAD_NAME             0  'x'
                 9  LOAD_CONST            1  5
                12  BINARY_ADD
                13  STORE_NAME            1  'y'
                16  LOAD_CONST            2  ''
                19  RETURN_VALUE


    # Here are grammar reductions:

                   expr ::= LOAD_CONST
                   ret_expr ::= expr
                   assert_expr ::= expr
             3     designator ::= STORE_NAME
                   assign ::= expr designator
                   stmt ::= assign
                   sstmt ::= stmt
                   stmts ::= sstmt
                   START ::= |- stmts
    L.  2:   6     expr ::= LOAD_NAME
    L.  2:   6     ret_expr ::= expr
    L.  2:   6     assert_expr ::= expr
             9     expr ::= LOAD_CONST
             9     exprlist ::= expr
            12     binary_op ::= BINARY_ADD
    L.  2:   6     binary_expr ::= expr expr binary_op
    L.  2:   6     expr ::= binary_expr
    L.  2:   6     ret_expr ::= expr
    L.  2:   6     assert_expr ::= expr
    ...


To be able to allow customization of the above to show line numbers
and token offsets which are part of uncompyle6's tokens but not the
generic one, the above is done by subclassing the reduction rule
printing program. The same can be done for duplicate-rule printing
and other things like that.

More recently, I the ability to callback before each reduction so
additional checks can be peformed before a reduction. In an ambiguous
grammar useful as it helps distinguish which rule should be used among
many.

Lastly, I've added a little syntactic sugar for the Kleene closure
operators `+`, `*` and optional suffix `?`. It is limited to only one
nonterminal on the right-hand side, but that does come up often and
helps a little. So you can now do things like:

.. code-block::

      stmts    ::= stmt+
      ratings  ::= STAR*
      opt_comma ::= COMMA?


These expand to:

.. code-block::

     stmts ::= stmts stmt
     stmts ::= stmt

and:

.. code-block::

     ratings ::= ratings STAR
     ratings ::=

and:

.. code-block::

     opt_comma ::= COMMA
     opt_comma ::=

respectively.
