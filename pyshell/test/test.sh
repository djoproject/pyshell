#!/bin/bash

#export PYTHONPATH=/home/jdv/development/tries_shell/pytries:$PYTHONPATH
export PYTHONPATH=$(pwd)/../../:$PYTHONPATH
echo $PYTHONPATH
#TODO python engineTest.py || exit
#TODO python engineCoreTest.py || exit
python engineStackTest.py || exit
python engineUtilsTest.py || exit
python testCommand.py || exit
python argcheckerTest.py || exit
python argfeederTest.py || exit
python decoratorTest.py || exit

