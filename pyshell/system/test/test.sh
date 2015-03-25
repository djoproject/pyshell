#!/bin/bash

export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

#DO NOT UPDATE THE EXECUTION ORDER, tests are sorted in front of the inheritance and the dependance between object

python -m pyshell.system.test.containerTest || exit
python -m pyshell.system.test.settingsTest || exit
python -m pyshell.system.test.procedureTest || exit
python -m pyshell.system.test.parameterTest || exit
python -m pyshell.system.test.environmentTest || exit
python -m pyshell.system.test.contextTest || exit
python -m pyshell.system.test.keyTest || exit
python -m pyshell.system.test.variableTest || exit
