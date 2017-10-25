# Compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

PHONY=check check-full clean dist distclean test
GIT2CL ?= git2cl
PYTHON ?= python
PYTHON3 ?= python3

#: the default target - same as running "check"
all: check

#: Run all tests with several Python versions via tox
check-full: check
	flake8 spark_parser && flake8 test \
	&& flake8 example \
	--exclude example/python2/test \

#: Run tests (one version of Python)
check:
	(cd test && nosetests -v *.py)
	$(MAKE) -C example/python2 check
#	$(MAKE) -C example/gdb-loc check

CLEAN_FILES= *.pyc *.so */*.pyc __pycache__ rm  */__pycache__/ */*/__pycache__ *~ */*~
#: Clean up temporary files
clean:
	$(PYTHON) ./setup.py $@
	-rm -fvr $(CLEAN_FILES) || true

#: Create source (tarball) and binary (egg) distribution
dist: README.rst
	$(PYTHON) ./setup.py sdist bdist

#: Create source tarball
sdist: README.rst
	$(PYTHON) ./setup.py sdist

#: Create binary egg distribution
bdist_egg: README.rst
	$(PYTHON) ./setup.py bdist_egg

#: Create Wheel distribution
wheel:
	$(PYTHON) ./setup.py bdist_wheel

# It is too much work to figure out how to add a new command to distutils
# to do the following. I'm sure distutils will someday get there.
DISTCLEAN_FILES = build dist *.egg-info

#: Remove ALL dervied files
distclean: clean
	-rm -fr $(DISTCLEAN_FILES) || true

#: Install package locally
install:
	$(PYTHON) ./setup.py install

#: Same as 'check' target
test: check

rmChangeLog:
	rm ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@

.PHONY: $(PHONY)
