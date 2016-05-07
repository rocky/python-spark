This directory contains a more complete example of using SPARK to parse,
generate an abstract tree, and then use that to evaluate simple arithmetic
expressions of integers with binary operators:
  '+', '-', '*', '/', '%', '^', '|', '&'

As is customary, the precidence of multiplication operatiors '*' and
'/' binds more strongly thatn addition operators.

Therefore:
   1 + 2 * 3
is interpreted as 1 + (2 * 3) rather than:
   (1 + 2) * 3.

However you can add explicit parenthesis to get to the latter interpretation

If you extend this example and you think you have a good clean example
for cases, make a github pull request and perhaps I'll include it.

Alternatively, if you have another good example to use for
demonstration of SPARK, again make a github pull request for
inclusion.

This is a little more fully worked out (and thus longer) than the expr example.
