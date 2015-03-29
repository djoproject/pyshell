#!/bin/bash

export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

python -m pyshell.command.test.engineInjectTest || exit 1
python -m pyshell.command.test.engineCommandTest || exit 1
python -m pyshell.command.test.engineSplitMergeTest || exit 1
python -m pyshell.command.test.engineDataTest || exit 1
python -m pyshell.command.test.engineCoreTest || exit 1
python -m pyshell.command.test.engineStackTest || exit 1
python -m pyshell.command.test.engineUtilsTest || exit 1
python -m pyshell.command.test.testCommand || exit 1
