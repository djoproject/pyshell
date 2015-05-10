#!/bin/bash

export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

python -m pyshell.utils.test.executingTest || exit 1
python -m pyshell.utils.test.parsingTest || exit 1
python -m pyshell.utils.test.postProcessTest || exit 1
python -m pyshell.utils.test.printingTest || exit 1
python -m pyshell.utils.test.solvingTest || exit 1
python -m pyshell.utils.test.miscTest || exit 1
python -m pyshell.utils.test.valuableTest || exit 1
python -m pyshell.utils.test.exceptionTest || exit 1
python -m pyshell.utils.test.keyTest || exit 1
python -m pyshell.utils.test.flushableTest || exit 1
python -m pyshell.utils.test.synchronizedTest || exit 1
