#!/bin/bash

export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

python -m pyshell.system.test.containerTest || exit
python -m pyshell.system.test.contextTest || exit
python -m pyshell.system.test.environmentTest || exit
python -m pyshell.system.test.keyTest || exit
python -m pyshell.system.test.parameterTest || exit
python -m pyshell.system.test.procedureTest || exit
python -m pyshell.system.test.variableTest || exit

