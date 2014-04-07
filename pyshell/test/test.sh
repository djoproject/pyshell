#!/bin/bash

#export PYTHONPATH=/home/jdv/development/tries_shell/pytries:$PYTHONPATH
export PYTHONPATH=$(pwd)/../../:$PYTHONPATH
echo $PYTHONPATH

#python engineInjectTest.py || exit
#python engineCommandTest.py || exit
python engineSplitMergeTest.py || exit
python engineDataTest.py || exit
python engineCoreTest.py || exit
python engineStackTest.py || exit
python engineUtilsTest.py || exit
python testCommand.py || exit
python argcheckerTest.py || exit
python argfeederTest.py || exit
python decoratorTest.py || exit

