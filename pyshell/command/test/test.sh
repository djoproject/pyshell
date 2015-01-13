#!/bin/bash

export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

python -m pyshell.command.test.engineInjectTest || exit
python -m pyshell.command.test.engineCommandTest || exit
python -m pyshell.command.test.engineSplitMergeTest || exit
python -m pyshell.command.test.engineDataTest || exit
python -m pyshell.command.test.engineCoreTest || exit
python -m pyshell.command.test.engineStackTest || exit
python -m pyshell.command.test.engineUtilsTest || exit
python -m pyshell.command.test.testCommand || exit
