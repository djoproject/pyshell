#!/bin/bash

export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

python -m pyshell.utils.test.procedureTest || exit
python -m pyshell.utils.test.keystoreTest || exit
python -m pyshell.utils.test.parameterTest || exit
