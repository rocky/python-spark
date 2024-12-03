#!/bin/bash
PYTHON_VERSION=2.4.6

spark_owd=$(pwd)
bs=${BASH_SOURCE[0]}
if [[ $0 == $bs ]] ; then
    echo "This script should be *sourced* rather than run directly through bash"
    exit 1
fi
mydir=$(dirname $bs)
cd $mydir/..
git checkout python-2.4-to-2.7 &&  pyenv local $PYTHON_VERSION
cd $spark_owd
