export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

python -m pyshell.loader.test.exceptionTest || exit 1
python -m pyshell.loader.test.utilsTest || exit 1
python -m pyshell.loader.test.dependanciesTest || exit 1
python -m pyshell.loader.test.commandTest || exit 1
python -m pyshell.loader.test.parameterTest || exit 1
python -m pyshell.loader.test.environmentTest || exit 1
python -m pyshell.loader.test.contextTest || exit 1
python -m pyshell.loader.test.keystoreTest || exit 1
python -m pyshell.loader.test.variableTest || exit 1
python -m pyshell.loader.test.procedureTest || exit 1
