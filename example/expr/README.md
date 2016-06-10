This directory contains a simple example of using SPARK to parse,
generate an Abstract Syntax Tree (or AST), and then use that to evaluate simple arithmetic
expressions of integers with operators `+`, `-`, `*`, and `/`.

As is customary, the precedence of multiplication operators `*` and
`/` bind more strongly than addition operators.

Therefore:

    1 + 2 * 3

is interpreted as `1 + (2 * 3)` rather than
`(1 + 2) * 3`.

See [expr2](http://github.com/rocky/python-spark/tree/master/example/expr2) for a more fully worked out example.
