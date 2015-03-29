#!/bin/bash

export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

python -m pyshell.arg.test.argcheckerTest || exit 1
python -m pyshell.arg.test.argfeederTest || exit 1
python -m pyshell.arg.test.decoratorTest || exit 1
