#!/bin/bash

#export PYTHONPATH=/home/jdv/development/tries_shell/pytries:$PYTHONPATH
export PYTHONPATH=$(pwd)/../../:$PYTHONPATH
echo $PYTHONPATH
python argcheckerTest.py
python argfeederTest.py