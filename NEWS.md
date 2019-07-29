1.8.9 2018-07-28 S
======================================

- 3.8 change needed in Python 3.7.4

1.8.8 2018-07-28 Survived another year
======================================

- Changes for Python 3.8

1.8.7 2018-05-18 Paper Tiger
============================

* Show LHS in error stack dump

1.8.6 2018-04-06
================

* spark-parser-coverage: Canonicalize to reduce fallse-positoin
  unused rules. Specifically we remove epsilon
  transition marks


1.8.5 2017-12-10 Dr Gecko
=========================

* Create set of list-like and optional nonterminals
  Those are nonterminals used in *, +, and ? rules
* example/python2/py2_parser.py: Pull constant out of nonterminal
	function
* test/test_misc.py: Python 2.6 compatability
* example/gdb-loc/README.md, example/python2/README.md,
  example/python2/format-python.py, spark_parser/spark.py,
  test/test_misc.py: Create set of list-like nonterminals
  automatically


1.8.2-1.8.4 2017-11-27 johnnybamazing2
======================================

- Fixes for removing a rules

- remove_rules() improvements...
  * Allow comments in rules
  * Strip blank lines in rules
  * Remove rule from profiling
- Document postoder/preorder better

1.8.0 2017-11-18 Cairole
========================

- Improve grammar checking
  * Add another grammar check in check_sets(): same non-null RHS
  * check_grammar() now returns the number of warnings issued
  * Improve output formatting in check_grammar()
- Profiling improvements
  * Secondary key in bin/spark-parser-coverage is the rule
  * Do not profile epsilon productions, they don't go through reductions
- Remove some Python lint warnings. (Even though Python formatting is imbicile,
  and for imbiciles)

spark 1.7.2 2017-11-14
======================

- Fix bug when used with profiling introduced in version 1.7.0
- In python2 grammar example add check-nonterminal to template engine

spark 1.7.1 2017-10-24
======================

- Handle errorstack option when not set properly
- more complete gdb-loc demo including better tests

1.7.0 2017-10-10
================

A number of incompatible changes, but necessary in code this old...

- show the final token reduction tracing. This helps tracing a LOT
- Improve ability to do reduction checks with AST (reduce_is_invalid),
  we now store tokens in parse object
- xxx.type -> xxx.kind to reduce confusion with built-in type
- some camelCase methods made "pythonic", e.g. check_grammar(), check_reduce()
- Allow checK_grammar to take a list of start symbols.
- Add gdb-loc demo: gdb breakpoint and list expressions
- Update docs

1.6.1 2017-05-17
================

- parser.remove_rules is the same as remove_rule
- fix parser.remove_rules so that it works even if rule has been removed

spark 1.6.0 2017-01-30
======================

- Add ability to track grammar coverage
- Add ability to remove grammar rules

spark 1.5.2 2017-01-27
======================

- Fix bug in dumpGrammar()
- print routines take an optional I/O parameter
- Correct Jay Earley's name

1.5.1 2016-11-27 johnnybamazing
===============================

- Add add limited Kleene closure symbols *, +, and optional suffix ?
  in grammar rules.
- Use these to simplify Python2 grammar
- Improve coverage in tests of Python2 grammar
- Start a NEW-FEATURES file
- Error if start symbol is not on LHS of grammar
- Check for totally recursive rules

1.5.0 2016-11-26
================

- User-definable reduction check. This
  allows one to specify an additional check before
  a rediction is made. For example in uncompyle6 we
  check whether a SETUP_LOOP target jumps to the last
  token of the rule. Or that an augmented assignment statement
  doesn't have inplace-binary operators

- User defined reduce printing rule. For example, the uncompyle6 token
  class has line numbers and offsets associated with them. We can
  show these as part of the reduction rule.

- Go over python 2 grammar and improve, but some indentation things are slightly worse. Sigh.

- spark.py Fix small python2 print bug

1.4.3 2016-11-22
================

- handle Python 2.3 via the 2.4 branch
- change grammer dup debug switch from 'rules' (already used)
  to 'dup'

1.4.2 2016-11-22
================

- Fix botched release
- handle Python 2.5 via the 2.4 branch

1.4.1 2016-11-21
================

- Eliminate duplicate grammar rules
- Allow hook for additional reduction testing
- Fix up setup.py: tests_require not test_requires
- Python 2.5 tolerance
- update example doc

1.4.0 2016-06-22
=================

- Add a grammar checker
- Improve AST printing
- More complete examples
  * More complete Python 2 example
  * expr2 example does evaluation


1.3.0 2016-06-08
================

- Incompatible change: error now returns token stack
  and index rather than just the error token
- add debug options 'context' to show tokens around
  the error token
- More useful GenericToken class that works better with the
  table-driven AST routines often used.
- Add GenericParser().dumpgrammar to show grammar rules
- Add Python2 parser example


1.2.1 2016-05-14
================

- Allow full 'errorstack': 'full' and abbreviated 'errorstack': True
  to show error stack with full dotted rules or just the part up to the dot
- fix packaging

1.2.0 2016-05-10
================

- Add routine to find/show error stack
- Allow setting paring debug option on parse method
- Add an additional and longer example parsing expressions.

1.1.2 2016-05-05
================

- Add LICENSE to setup.py - this time for sure!

1.1.1 2016-05-03
================

- Add LICENSE and other administrivia

1.1.0 2016-04-28
================

- change module name to from spark to spark_parser to avoid conflict
  other python spark modules in existence

1.0.2 2016-04-27
=================

- Administrivia

1.0.1 2016-04-27
================

- Fix metadata for Python3 upload
- Fix module exports

1.0.0 2016-04-26
=================

- First Python package release: 8 years in the making
