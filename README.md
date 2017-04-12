## Pyshell ##

This tool is an advanced shell completly written in python.
Compatible with Linux and MacOS, it is unfortunatly not compatible
with the Microsoft operating systems.
The software can be run with python2 and python3.
Because of the apdu library some rfid addons are not fully python3 compatible.
It will be solved soon.

The main goal of this tool is the speed usage, at every level, from writting
a new command to the call of an existant one. To reach this goal,
the [trie](http://en.wikipedia.org/wiki/Trie) algorithm is widely used.
And an advanced system to register new command is also provided.

### Documentation ###

No documentation exists yet, only this readme. If you want to write your own
addons, just based your work on the existing ones.

### Quick install ###

Not sure this tool is what you are looking for ? Test it! Just Download and
execute the file `quick_install.sh`.
It will download the needed files in the current directory and prepare the
local environment. As soon as the tool becomes useless for you, all you
have to do is removed the files and directories.

The tool will also try to create a configuration directory in your HOME
directory, these data could also be wiped. The path of this directory is
`$HOME/.pyshell`.

### Real install ###

To install the shell, install the dependencies then execute the following
command `python setup.py install`.
Be carefull, the normal installation does not manage dependencies.

The project has dependencies to the following libraries:
* [pytries](https://github.com/djoproject/pytries)
* [apdu_builder](https://github.com/djoproject/apdu_builder)

### Issues/TODO ###

To add an issue, a request, a bug or ask a question, please use the
system [provided by Github](https://github.com/djoproject/pyshell/issues).

### Unit testing ###

The test suite use the [pytest](https://docs.pytest.org/en/latest/) framework,
be sure to have it installed before to run any test.

Each module directory hold a subdirectory named "test" that hold the test
files for this module level. The current coverage is above 90% and will
increase at each new release.

Refer to the [pytest](https://docs.pytest.org/en/latest/) documentation if you
want to run any advanced test. The simplest way to execute it is to use
the command `python -m pytest` in the source code directory.

### Sources ###

Every source files are located in the subdirectory `pyshell`.

The source code is fully [PEP8](https://www.python.org/dev/peps/pep-0008)
compliant and even goes further. The folowing style guides are also used:
* [import-order](https://pypi.python.org/pypi/import-order)
* [flake8-print](https://pypi.python.org/pypi/flake8-print)
* [custom naming](https://github.com/djoproject/pep8-naming)

### Licence ###

This software is distributed under the GPLv3 licence, the full licence is
available in the provided file `LICENCE`.

