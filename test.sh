#!/bin/bash
#this command will look after each test.sh in the project and execute them

export PYTHONPATH=$(pwd)/:$PYTHONPATH

for f in `find ./pyshell/ -name "test.sh"`;do
    echo $f
    bash $f || exit;
done
