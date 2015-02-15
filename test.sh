#!/bin/bash
#this command will look after each test.sh in the project and execute them

export PYTHONPATH=$(pwd)/:$PYTHONPATH

for f in `find ./pyshell -name "test.sh" -print0 | xargs -0 -n1 dirname | sort --unique`;do
    echo "####### $f #######"
    cd $f
    ./test.sh || exit
    cd -
done
