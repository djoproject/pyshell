#!/bin/bash

export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

python -m pyshell.utils.test.executingTest || exit

