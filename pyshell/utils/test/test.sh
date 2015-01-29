#!/bin/bash

export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

python -m pyshell.utils.test.aliasTest || exit
python -m pyshell.utils.test.executingTest || exit
python -m pyshell.utils.test.keystoreTest || exit
python -m pyshell.utils.test.parameterTest || exit
python -m pyshell.utils.test.parsingTest || exit
python -m pyshell.utils.test.postProcessTest || exit
python -m pyshell.utils.test.printingTest || exit
python -m pyshell.utils.test.solvingTest || exit
python -m pyshell.utils.test.utilsTest || exit
python -m pyshell.utils.test.valuableTest || exit