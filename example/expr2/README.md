This directory contains a more complete example of using SPARK to parse,
generate an Abstract Syntax Tree (or AST), and then use that to evaluate simple arithmetic
expressions of integers with binary operators:
  `+`, `-`, `*`, `/`

As is customary, the precedence of multiplication operators `*` and
`/` bind more strongly than addition operators.

Therefore:

    1 + 2 * 3

is interpreted as `1 + (2 * 3)` rather than: `(1 + 2) * 3`.

However you can add explicit parenthesis to get to the latter interpretation

If you extend this example and you think you have a good clean example
for cases, make a github pull request and perhaps I'll include it.

Alternatively, if you have another good example to use for
demonstration of SPARK, again make a github pull request for
inclusion.

This is a little more fully worked out (and thus longer) than the [`expr`](http://github.com/rocky/python-spark/tree/master/example/expr) example.

See
[python2](http://github.com/rocky/python-spark/tree/master/example/python2)
for the most elaborate example showing Python 2.6.
