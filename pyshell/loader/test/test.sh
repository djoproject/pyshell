export PYTHONPATH=$(pwd)/../../../:$PYTHONPATH
echo $PYTHONPATH

python -m pyshell.loader.test.utilsTest
python -m pyshell.loader.test.commandTest
python -m pyshell.loader.test.contextTest
python -m pyshell.loader.test.dependanciesTest
python -m pyshell.loader.test.environmentTest
python -m pyshell.loader.test.exceptionTest
python -m pyshell.loader.test.keystoreTest
python -m pyshell.loader.test.procedureTest
