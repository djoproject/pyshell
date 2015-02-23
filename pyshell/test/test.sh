#!/bin/bash

export PYTHONPATH=$(pwd)/../../:$PYTHONPATH
echo $PYTHONPATH

python -m pyshell.test.executerTest || exit
