** STILL IN DEV ! **
The software is usable but there is no main/stable branch yet.

## Pyshell ##

This tool is an advanced shell completly writtent in python.
Compatible with Linux or MacOS, this tool is unfortunatly not compatible 
with Windows OS.  The software is only compatible with python 2 for the moment.

The main goal is the speed usage, at every level, from writting a new command 
to the call of an existant command.  To reach this goal, 
the algorithm [trie](http://en.wikipedia.org/wiki/Trie) is used at several 
level in the shell.  And an advanced system to register new command 
is provided

### Quick install ###

You are not sure this tool is what you want ? but you want to test it to 
be sure.  Just Download and execute the file `quick_install.sh`.
It will download the needed files in the current directory and prepare the 
local environment.  As soon as the tools become useless, all you have to do is 
removed the files and directories.  It is possible that the tool try and create
a configuration directory in your HOME directory, these data could also 
be deleted.  The path of this directory is `$HOME/.pyshell`

### Real install ###

To install the shell, execute the following command `make install`.
Be carefull, the normal installation does not manage dependancies yet.

The project has dependancies to the following libraries:
* [pytries](https://github.com/djo938/pytries)
* [apdu_builder](https://github.com/djo938/apdu_builder)

### Issues/TODO ###

To add an issue, a request, a bug or any change request, please use the
system provided by Github.

### Test ###

To test everything, use the command `make test`.  If a specific package is 
targeted, it is possible to specify it with the extra argument TEST_TARGET, 
e.g. `make TEST_TARGET=system test`.

To develop and test at the same time, use the command `make devtest`.
Each time a file will be updated, the tests will start again.

### Sources ###

Every source files are located in the subdirectory `pyshell`.

### Licence ###

This software is distributed under the GPLv3 licence, the licence is available
in the provided file `LICENCE`.

