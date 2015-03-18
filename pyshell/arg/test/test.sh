#!/bin/bash

export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

python -m pyshell.arg.test.argcheckerTest || exit
python -m pyshell.arg.test.argfeederTest || exit
python -m pyshell.arg.test.decoratorTest || exit
