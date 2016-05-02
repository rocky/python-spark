This directory contains a simple example of using SPARK to parse,
generate an abstract tree, and then use that to evaluate simple arithmetic
expressions of integers with operators "+', '-', '*', and '/'.

As is customary, the precidence of multiplication operatiors '*' and
'/' binds more strongly thatn addition operators.

Therefore:
   1 + 2 * 3
is interpreted as 1 + (2 * 3) rather than
   (1 + 2) * 3.

Omitted here for simplicity are parenthesis in expressions. For that you might
add grammar rule method like:

```
    def p_expr_3(self, args):
        """ expr ::= lparen expr rparen """
        return AST('single', [args[0]])
```

along with tokenization methods for '(', ')'.

Another extension to try might to be to recognize floating-pont numbers by
adding a tokenization method like this:

```
    def t_float(self, s):
        """r'\d+.\d+'"""
        t = Token(type='float, attr=s)
        self.rv.append(t)
```

A grammar rule like this:

    def p_number(self, args):
        """
			expr ::= float
			expr ::= integer
		"""
        return AST('number, [args[0]])

might be useful.

If you extend this example and you think you have a good clean example
for others, make a github pull request and perhaps I'll include it.

Alternatively, if you have another good example to use for
demonstration of SPARK, again make a github pull request for
inclusion.
