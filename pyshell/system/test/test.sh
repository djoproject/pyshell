#!/bin/bash

export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

#DO NOT UPDATE THE EXECUTION ORDER, tests are sorted in front of the inheritance and the dependance between object

python -m pyshell.system.test.containerTest || exit 1
python -m pyshell.system.test.settingsTest || exit 1
python -m pyshell.system.test.procedureTest || exit 1
python -m pyshell.system.test.parameterTest || exit 1
python -m pyshell.system.test.environmentTest || exit 1
python -m pyshell.system.test.contextTest || exit 1
python -m pyshell.system.test.keyTest || exit 1
python -m pyshell.system.test.variableTest || exit 1
