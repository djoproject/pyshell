#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2016  Jonathan Delvaux <pyshell@djoproject.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import getopt
import sys

from pyshell.executer import CommandExecuter


def usage():
    print("\nexecuter.py [-h -p <parameter file> -i <script file> -s]")  # noqa


def help():
    usage()
    print("\nPython Custom Shell Executer v1.0\n\n"  # noqa
          "-h, --help:        print this help message\n"
          "-p, --parameter:   define a custom parameter file\n"
          "-s, --script:      define a script to execute\n"
          "-n, --no-exit:     start the shell after the script\n"
          "-g, --granularity: set the error granularity for file script\n")

if __name__ == "__main__":
    # manage args
    opts = ()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:s:ng:", ["help",
                                                              "parameter=",
                                                              "script=",
                                                              "no-exit",
                                                              "granularity="])
    except getopt.GetoptError as err:
        # print help information and exit:
        # will print something like "option -a not recognized"
        print(str(err))  # noqa
        usage()
        print("\nto get help: executer.py -h\n")  # noqa
        sys.exit(2)

    ParameterFile = None
    ScriptFile = None
    ExitAfterScript = True
    Granularity = float("inf")

    for o, a in opts:  # TODO test every args
        if o in ("-h", "--help"):
            help()
            exit()
        elif o in ("-p", "--parameter"):
            ParameterFile = a
        elif o in ("-s", "--script"):
            ScriptFile = a
        elif o in ("-n", "--no-exit"):
            ExitAfterScript = False
        elif o in ("-g", "--granularity"):
            try:
                Granularity = int(a)
            except ValueError as ve:
                print("invalid value for granularity: "+str(ve))  # noqa
                usage()
                exit(-1)
        else:
            print("unknown parameter: "+str(o))  # noqa

    # run basic instance
    executer = CommandExecuter(ParameterFile, args)

    if ScriptFile is not None:
        executer.executeFile(ScriptFile, Granularity)
    else:
        ExitAfterScript = False

    if not ExitAfterScript:
        executer.mainLoop()
