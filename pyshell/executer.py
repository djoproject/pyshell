#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

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

import atexit
import getopt
import readline
import sys
from contextlib import contextmanager

from tries import multiLevelTries
from tries.exception import pathNotExistsTriesException

from pyshell.addons import addon
from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.arg.argchecker import FilePathArgChecker
from pyshell.arg.argchecker import IntegerArgChecker
from pyshell.arg.argchecker import ListArgChecker
from pyshell.system.container import ParameterContainer
from pyshell.system.context import ContextParameter
from pyshell.system.context import ContextParameterManager
from pyshell.system.context import GlobalContextSettings
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.environment import EnvironmentParameterManager
from pyshell.system.key import CryptographicKeyParameterManager
from pyshell.system.procedure import ProcedureFromFile
from pyshell.system.procedure import ProcedureFromList
from pyshell.system.settings import GlobalSettings
from pyshell.system.variable import VarParameter
from pyshell.system.variable import VariableParameterManager
from pyshell.utils.constants import ADDONLIST_KEY
from pyshell.utils.constants import CONTEXT_ATTRIBUTE_NAME
from pyshell.utils.constants import CONTEXT_COLORATION_DARK
from pyshell.utils.constants import CONTEXT_COLORATION_KEY
from pyshell.utils.constants import CONTEXT_COLORATION_LIGHT
from pyshell.utils.constants import CONTEXT_COLORATION_NONE
from pyshell.utils.constants import CONTEXT_EXECUTION_DAEMON
from pyshell.utils.constants import CONTEXT_EXECUTION_KEY
from pyshell.utils.constants import CONTEXT_EXECUTION_SCRIPT
from pyshell.utils.constants import CONTEXT_EXECUTION_SHELL
from pyshell.utils.constants import DEBUG_ENVIRONMENT_NAME
from pyshell.utils.constants import DEFAULT_PARAMETER_FILE
from pyshell.utils.constants import ENVIRONMENT_ADDON_TO_LOAD_DEFAULT
from pyshell.utils.constants import ENVIRONMENT_ADDON_TO_LOAD_KEY
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import ENVIRONMENT_HISTORY_FILE_NAME_KEY
from pyshell.utils.constants import ENVIRONMENT_HISTORY_FILE_NAME_VALUE
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.constants import ENVIRONMENT_PARAMETER_FILE_KEY
from pyshell.utils.constants import ENVIRONMENT_PROMPT_DEFAULT
from pyshell.utils.constants import ENVIRONMENT_PROMPT_KEY
from pyshell.utils.constants import ENVIRONMENT_SAVE_KEYS_DEFAULT
from pyshell.utils.constants import ENVIRONMENT_SAVE_KEYS_KEY
from pyshell.utils.constants import ENVIRONMENT_TAB_SIZE_KEY
from pyshell.utils.constants import ENVIRONMENT_USE_HISTORY_KEY
from pyshell.utils.constants import ENVIRONMENT_USE_HISTORY_VALUE
from pyshell.utils.constants import EVENT_AT_EXIT
from pyshell.utils.constants import EVENT_ON_STARTUP
from pyshell.utils.constants import EVENT__ON_STARTUP
from pyshell.utils.constants import KEY_ATTRIBUTE_NAME
from pyshell.utils.constants import TAB_SIZE
from pyshell.utils.constants import VARIABLE_ATTRIBUTE_NAME
from pyshell.utils.exception import ListOfException
from pyshell.utils.executing import execute
from pyshell.utils.misc import getTerminalSize
from pyshell.utils.parsing import Parser
from pyshell.utils.printing import Printer
from pyshell.utils.printing import error
from pyshell.utils.printing import printException
from pyshell.utils.printing import warning
from pyshell.utils.valuable import SimpleValuable


# TODO
#   there is no NoneCheck after .getParameter,
#   could be interesting to manage these case

#   use constant EVENT_TO_CREATE_ON_STARTUP to create the list of procedure
#   for these event at startup

#   create an endless "shell" procedure
#       use object ProcedureFromList
#           need some new command before to do that
#               GOTO or LOOP
#               command to readline and execute

# TODO does not work if we import it in a python shell and try to
# instanciate it without args
class CommandExecuter():
    def __init__(self, param_file=None, outside_args=None):
        self._initParams(param_file, outside_args)
        self._initPrinter()

        # load addon addon (if not loaded, can't do anything)
        loaded = False
        with self.exceptionManager("fail to load addon "
                                   "'pyshell.addons.addon'"):
            addon.loadAddonFun("pyshell.addons.addon", self.params)
            loaded = True

        if not loaded:
            print("fail to load addon loader, can not do anything with"  # noqa
                  " the application without this loader")
            exit(-1)

        # TODO create default event here (see list of event in constant file)

        self._initStartUpEvent()
        self._initExitEvent()

        # # execute atStartUp # #
        execute(EVENT__ON_STARTUP, self.params, "__startup__")

    def _initParams(self, param_file, outside_args):
        # create param manager
        self.params = ParameterContainer()

        env = EnvironmentParameterManager(self.params)
        self.params.registerParameterManager(ENVIRONMENT_ATTRIBUTE_NAME, env)

        con = ContextParameterManager(self.params)
        self.params.registerParameterManager(CONTEXT_ATTRIBUTE_NAME, con)

        var = VariableParameterManager(self.params)
        self.params.registerParameterManager(VARIABLE_ATTRIBUTE_NAME, var)

        key = CryptographicKeyParameterManager(self.params)
        self.params.registerParameterManager(KEY_ATTRIBUTE_NAME, key)

        # init local level
        # TODO remove me as soon as shell has its own procedure
        self.params.pushVariableLevelForThisThread()
        self.promptWaitingValuable = SimpleValuable(False)

        default_global_setting = GlobalSettings(transient=False,
                                                read_only=False,
                                                removable=False)

        default_string_arg_checker = DefaultInstanceArgChecker.\
            getStringArgCheckerInstance()
        default_arg_checker = DefaultInstanceArgChecker.\
            getArgCheckerInstance()
        default_boolean_arg_checker = DefaultInstanceArgChecker.\
            getBooleanValueArgCheckerInstance()
        default_integer_arg_checker = DefaultInstanceArgChecker.\
            getIntegerArgCheckerInstance()

        # # init original params # #
        param = EnvironmentParameter(value=param_file,
                                     typ=FilePathArgChecker(exist=None,
                                                            readable=True,
                                                            writtable=None,
                                                            is_file=True),
                                     settings=GlobalSettings(transient=True,
                                                             read_only=False,
                                                             removable=False))
        env.setParameter(ENVIRONMENT_PARAMETER_FILE_KEY,
                         param,
                         local_param=False)

        param = EnvironmentParameter(value=ENVIRONMENT_PROMPT_DEFAULT,
                                     typ=default_string_arg_checker,
                                     settings=default_global_setting.clone())
        env.setParameter(ENVIRONMENT_PROMPT_KEY,
                         param,
                         local_param=False)

        param = EnvironmentParameter(value=TAB_SIZE,
                                     typ=IntegerArgChecker(0),
                                     settings=default_global_setting.clone())
        env.setParameter(ENVIRONMENT_TAB_SIZE_KEY,
                         param,
                         local_param=False)

        param = EnvironmentParameter(value=multiLevelTries(),
                                     typ=default_arg_checker,
                                     settings=GlobalSettings(transient=True,
                                                             read_only=True,
                                                             removable=False))
        env.setParameter(ENVIRONMENT_LEVEL_TRIES_KEY,
                         param,
                         local_param=False)

        param = EnvironmentParameter(value=ENVIRONMENT_SAVE_KEYS_DEFAULT,
                                     typ=default_boolean_arg_checker,
                                     settings=default_global_setting.clone())
        env.setParameter(ENVIRONMENT_SAVE_KEYS_KEY,
                         param,
                         local_param=False)

        param = EnvironmentParameter(value=ENVIRONMENT_HISTORY_FILE_NAME_VALUE,
                                     typ=FilePathArgChecker(exist=None,
                                                            readable=True,
                                                            writtable=None,
                                                            is_file=True),
                                     settings=default_global_setting.clone())
        env.setParameter(ENVIRONMENT_HISTORY_FILE_NAME_KEY,
                         param,
                         local_param=False)

        param = EnvironmentParameter(value=ENVIRONMENT_USE_HISTORY_VALUE,
                                     typ=default_boolean_arg_checker,
                                     settings=default_global_setting.clone())
        env.setParameter(ENVIRONMENT_USE_HISTORY_KEY,
                         param,
                         local_param=False)

        typ = ListArgChecker(default_string_arg_checker)
        param = EnvironmentParameter(value=ENVIRONMENT_ADDON_TO_LOAD_DEFAULT,
                                     typ=typ,
                                     settings=default_global_setting.clone())
        env.setParameter(ENVIRONMENT_ADDON_TO_LOAD_KEY,
                         param,
                         local_param=False)

        param = EnvironmentParameter(value={},
                                     typ=default_arg_checker,
                                     settings=GlobalSettings(transient=True,
                                                             read_only=True,
                                                             removable=False))
        env.setParameter(ADDONLIST_KEY,
                         param,
                         local_param=False)

        default_context_setting = GlobalContextSettings(removable=False,
                                                        read_only=True,
                                                        transient=False,
                                                        transient_index=False)

        param = ContextParameter(value=tuple(range(0, 5)),
                                 typ=default_integer_arg_checker,
                                 default_index=0,
                                 index=1,
                                 settings=default_context_setting.clone())
        con.setParameter(DEBUG_ENVIRONMENT_NAME,
                         param,
                         local_param=False)

        settings = GlobalContextSettings(removable=False,
                                         read_only=True,
                                         transient=True,
                                         transient_index=True)
        values = (CONTEXT_EXECUTION_SHELL,
                  CONTEXT_EXECUTION_SCRIPT,
                  CONTEXT_EXECUTION_DAEMON,)
        param = ContextParameter(value=values,
                                 typ=default_string_arg_checker,
                                 default_index=0,
                                 settings=settings)
        con.setParameter(CONTEXT_EXECUTION_KEY,
                         param,
                         local_param=False)

        values = (CONTEXT_COLORATION_LIGHT,
                  CONTEXT_COLORATION_DARK,
                  CONTEXT_COLORATION_NONE,)
        param = ContextParameter(value=values,
                                 typ=default_string_arg_checker,
                                 default_index=0,
                                 settings=default_context_setting.clone())
        con.setParameter(CONTEXT_COLORATION_KEY,
                         param,
                         local_param=False)

        # mapped outside argument
        if outside_args is not None:
            # all in one string
            args_string = VarParameter(' '.join(str(x) for x in outside_args))
            var.setParameter("*", args_string, local_param=False)
            args_string.settings.setTransient(True)

            # arg count
            arg_count = VarParameter(len(outside_args))
            var.setParameter("#", arg_count, local_param=False)
            arg_count.settings.setTransient(True)

            # all args
            all_args = VarParameter(outside_args)
            var.setParameter("@", all_args, local_param=False)
            all_args.settings.setTransient(True)
            # last pid started in background
            # TODO var = self.params.variable.setParameter("!",
            #            VarParameter(outside_args), local_param = False)
            # var.settings.setTransient(True)

        # current process id
        # TODO id is not enought, need level
        current_id_var = VarParameter(self.params.getCurrentId())
        var = self.params.variable.setParameter("$",
                                                current_id_var,
                                                local_param=False)
        var.settings.setTransient(True)

        # value from last command
        # TODO remove me as soon as shell will be in its self procedure
        var = self.params.variable.setParameter("?",
                                                VarParameter(()),
                                                local_param=True)
        var.settings.setTransient(True)

    def _initPrinter(self):
        # # prepare the printing system # #
        printer = Printer.getInstance()
        printer.setReplFunction(self.printAsynchronousOnShellV2)
        printer.setPromptShowedContext(self.promptWaitingValuable)
        printer.setParameters(self.params)

    def _initStartUpEvent(self):
        # # prepare atStartUp # #
        env = self.params.environment
        mltries = env.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY,
                                   perfect_match=True).getValue()
        _atstartup = ProcedureFromList(EVENT__ON_STARTUP,
                                       settings=GlobalSettings(read_only=False,
                                                               removable=False,
                                                               transient=True))
        _atstartup.neverStopIfErrorOccured()

        _atstartup.addCommand("addon load pyshell.addons.parameter")
        _atstartup.addCommand("parameter load")

        # TODO don't unload it if in addon to load on startup
        _atstartup.addCommand("addon unload pyshell.addons.parameter")

        # TODO don't load parameter if already loaded
        _atstartup.addCommand("addon onstartup load")
        _atstartup.addCommand(EVENT_ON_STARTUP)

        _atstartup.settings.setReadOnly(True)
        mltries.insert((EVENT__ON_STARTUP,),
                       _atstartup,
                       stopTraversalAtThisNode=True)

        atstartup = ProcedureFromList(EVENT_ON_STARTUP,
                                      settings=GlobalSettings(read_only=False,
                                                              removable=False,
                                                              transient=True))
        atstartup.neverStopIfErrorOccured()
        atstartup.addCommand("history load")
        # atstartup.addCommand( "key load" )
        mltries.insert((EVENT_ON_STARTUP,),
                       atstartup,
                       stopTraversalAtThisNode=True)

    def _initExitEvent(self):
        env = self.params.environment
        mltries = env.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY,
                                   perfect_match=True).getValue()

        # # prepare atExit # #
        at_exit = ProcedureFromList(EVENT_AT_EXIT,
                                    settings=GlobalSettings(read_only=False,
                                                            removable=False,
                                                            transient=True))
        at_exit.neverStopIfErrorOccured()

        # TODO need to have parameters addons parameter loaded before to save
        at_exit.addCommand("parameter save")

        # TODO load parameter addon but do not print any error if already
        # loaded, add a parameter to addon load
        at_exit.addCommand("history save")
        # at_exit.addCommand( "key save" )

        at_exit.settings.setReadOnly(True)
        mltries.insert((EVENT_AT_EXIT,), at_exit, stopTraversalAtThisNode=True)
        atexit.register(self.atExit)

    def atExit(self):
        # TODO provide args from outside
        execute(EVENT_AT_EXIT, self.params, "__atexit__")

    def mainLoop(self):
        # enable autocompletion
        if 'libedit' in readline.__doc__:
            import rlcompleter  # NOQA
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

        readline.set_completer(self.complete)

        context = self.params.context
        exec_type = context.getParameter(CONTEXT_EXECUTION_KEY,
                                         perfect_match=True)
        exec_type.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)

        # mainloop
        while True:
            # read prompt
            self.promptWaitingValuable.setValue(True)
            try:
                env = self.params.environment
                prompt = env.getParameter(ENVIRONMENT_PROMPT_KEY,
                                          perfect_match=True).getValue()
                cmd = raw_input(prompt)
            except SyntaxError as se:
                error(se, "syntax error")
                continue
            except EOFError:
                warning("\n   end of stream")
                break
            finally:
                self.promptWaitingValuable.setValue(False)

            # TODO provide processName AND processArg from the outside
            # of the sofware
            execute(cmd, self.params, "__shell__")

    def printAsynchronousOnShellV2(self, message):
        env = self.params.environment
        prompt = env.getParameter(ENVIRONMENT_PROMPT_KEY,
                                  perfect_match=True).getValue()
        # this is needed because after an input,
        # the readline buffer isn't always empty
        if len(readline.get_line_buffer()) == 0 or \
           readline.get_line_buffer()[-1] == '\n':
            size = len(prompt)
            toprint = prompt
        else:
            size = len(prompt) + len(readline.get_line_buffer())
            toprint = prompt + readline.get_line_buffer()

        width, height = getTerminalSize()
        offset = int(size/width)

        # http://ascii-table.com/ansi-escape-sequences-vt-100.php
        # message = EventToPrint +" "+str(width)+" "+str(size)+" "+str(offset)
        if offset > 0:
            message = "\r\033["+str(offset)+"A\033[2K" + message  # + "\033[s"
        else:
            message = "\r\033[K" + message  # + "\033[s"

        sys.stdout.write(message + "\n" + toprint)
        sys.stdout.flush()

    def complete(self, suffix, index):
        parser = Parser(readline.get_line_buffer())
        parser.parse()
        env = self.params.environment
        ltries = env.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY,
                                  perfect_match=True).getValue()
        try:
            # # special case, empty line # #
                # only print root tokens
            if len(parser) == 0:
                fullline = ()
                dic = ltries.buildDictionnary(fullline, True, True, False)

                toret = {}
                for k in dic.keys():
                    toret[k[0]] = None

                toret = toret.keys()[:]
                toret.append(None)
                return toret[index]

            fullline = parser[-1][0]

            # # manage ambiguity # #
            advanced_result = ltries.advancedSearch(fullline, False)
            if advanced_result.isAmbiguous():
                token_index = len(advanced_result.existingPath) - 1

                if token_index != (len(fullline)-1):
                    return None   # ambiguity on an inner level

                tries = advanced_result.existingPath[token_index][1].localTries
                keylist = tries.getKeyList(fullline[token_index])

                keys = []
                for key in keylist:
                    tmp = list(fullline[:])
                    tmp.append(key)
                    keys.append(tmp)
            else:
                try:
                    dic = ltries.buildDictionnary(fullline, True, True, False)
                except pathNotExistsTriesException:
                    return None

                keys = dic.keys()

            # build final result
            final_keys = []
            for k in keys:

                # special case to complete the last token if needed
                if len(k) >= len(fullline) and \
                   len(k[len(fullline)-1]) > len(fullline[-1]):
                    toappend = k[len(fullline)-1]

                    if len(k) > len(fullline):
                        toappend += " "

                    final_keys.append(toappend)
                    break

                # normal case, the last token on the line is complete,
                # only add its child tokens
                final_keys.append(" ".join(k[len(fullline):]))

            # if no other choice than the current value, return the
            # current value
            if "" in final_keys and len(final_keys) == 1:
                return (fullline[-1], None,)[index]

            final_keys.append(None)
            return final_keys[index]

        except Exception as ex:
            context = self.params.context
            debug_level = context.getParameter(DEBUG_ENVIRONMENT_NAME,
                                               perfect_match=True)
            if debug_level.getSelectedValue() > 0:
                printException(ex)

        return None

    @contextmanager
    def exceptionManager(self, msg_prefix=None):
        try:
            yield
        except ListOfException as loe:
            if msg_prefix is None:
                msg_prefix = "List of exception: "

            printException(loe, msg_prefix)

        except Exception as pex:
            if msg_prefix is not None:
                msg_prefix += ": "

            printException(pex, msg_prefix)

    def executeFile(self, filename, granularity=None):
        context = self.params.context
        exec_type = context.getParameter(CONTEXT_EXECUTION_KEY,
                                         perfect_match=True)
        exec_type.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        afile = ProcedureFromFile(filename)
        afile.stopIfAnErrorOccuredWithAGranularityLowerOrEqualTo(granularity)

        with self.exceptionManager("An error occured during the script "
                                   "execution: "):
            afile.execute(args=(), parameters=self.params)

# TODO this part should be in an other file, e.g. exec ########################
# no need to use printing system on the following function because shell is
# not yet running


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
    Granularity = sys.maxint

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

    if ParameterFile is None:
        ParameterFile = DEFAULT_PARAMETER_FILE

    # run basic instance
    executer = CommandExecuter(ParameterFile, args)

    if ScriptFile is not None:
        executer.executeFile(ScriptFile, Granularity)
    else:
        ExitAfterScript = False

    if not ExitAfterScript:
        executer.mainLoop()
