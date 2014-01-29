#!/bin/bash

#export PYTHONPATH=/home/jdv/development/tries_shell/pytries:$PYTHONPATH
export PYTHONPATH=$(pwd)/../../:$PYTHONPATH
echo $PYTHONPATH
python engineTest.py || exit
python argcheckerTest.py || exit
python argfeederTest.py || exit
python decoratorTest.py || exit

