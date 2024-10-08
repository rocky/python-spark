#!/bin/bash
check_spark_24_owd=$(pwd)

cd $(dirname ${BASH_SOURCE[0]})
if ! source ./pyenv-2.4-2.7-versions ; then
    exit $?
fi
if ! source ./setup-python-2.4.sh ; then
    exit $?
fi
cd ..
for version in $PYVERSIONS; do
    echo --- $version ---
    if ! pyenv local $version ; then
	exit $?
    fi
    make clean && pip install -e .
    if ! make check; then
	exit $?
    fi
    echo === $version ===
done
cd $check_spark_24_owd
