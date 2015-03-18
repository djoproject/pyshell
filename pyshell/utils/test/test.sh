#!/bin/bash

export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

python -m pyshell.utils.test.executingTest || exit
python -m pyshell.utils.test.parsingTest || exit
python -m pyshell.utils.test.postProcessTest || exit
python -m pyshell.utils.test.printingTest || exit
python -m pyshell.utils.test.solvingTest || exit
python -m pyshell.utils.test.miscTest || exit
python -m pyshell.utils.test.valuableTest || exit
python -m pyshell.utils.test.exceptionTest || exit
python -m pyshell.utils.test.keyTest || exit
python -m pyshell.utils.test.flushableTest || exit
