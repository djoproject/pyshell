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
import readline
import sys
import threading
from contextlib import contextmanager

from tries.exception import pathNotExistsTriesException

from pyshell.addons import parameter
from pyshell.addons import std
from pyshell.addons import system
from pyshell.system.container import ParameterContainer
from pyshell.system.context import ContextParameterManager
from pyshell.system.environment import EnvironmentParameterManager
from pyshell.system.key import CryptographicKeyParameterManager
from pyshell.system.procedure import ProcedureFromFile
from pyshell.system.variable import VarParameter
from pyshell.system.variable import VariableParameterManager
from pyshell.utils.constants import ADDONLIST_KEY
from pyshell.utils.constants import CONTEXT_ATTRIBUTE_NAME
from pyshell.utils.constants import CONTEXT_EXECUTION_KEY
from pyshell.utils.constants import CONTEXT_EXECUTION_SCRIPT
from pyshell.utils.constants import CONTEXT_EXECUTION_SHELL
from pyshell.utils.constants import DEBUG_ENVIRONMENT_NAME
from pyshell.utils.constants import ENVIRONMENT_ADDON_TO_LOAD_KEY
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import ENVIRONMENT_HISTORY_FILE_NAME_KEY
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.constants import ENVIRONMENT_PARAMETER_FILE_KEY
from pyshell.utils.constants import ENVIRONMENT_PROMPT_KEY
from pyshell.utils.constants import ENVIRONMENT_USE_HISTORY_KEY
from pyshell.utils.constants import KEY_ATTRIBUTE_NAME
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
#   there is no None check after call to any getParameter,
#   could be interesting to manage these case

# TODO
#   the second part of the __init__ is not an init part
#   it is more like the first part of the running.
#   So it could move in the main loop method or in another method.

class CommandExecuter():
    def __init__(self, param_file=None, outside_args=None):
        self.params = ParameterContainer()
        self._initContainers()

        self.promptWaitingValuable = SimpleValuable(False)
        self._initPrinter()

        # load addon system (if not loaded, can't do anything)
        loaded = False
        with self.exceptionManager("fail to load addon "
                                   "'pyshell.addons.system'"):
            system._loaders.load(self.params)
            loaded = True

        if not loaded:
            print("fail to load system addon, can not do anything with"  # noqa
                  " the application without this loader")
            exit(-1)

        self._initParams(param_file, outside_args, system._loaders)
        self._startUp()
        atexit.register(self._atExit)

    def _initContainers(self):
        env = EnvironmentParameterManager(self.params)
        self.params.registerParameterManager(ENVIRONMENT_ATTRIBUTE_NAME, env)

        con = ContextParameterManager(self.params)
        self.params.registerParameterManager(CONTEXT_ATTRIBUTE_NAME, con)

        var = VariableParameterManager(self.params)
        self.params.registerParameterManager(VARIABLE_ATTRIBUTE_NAME, var)

        key = CryptographicKeyParameterManager(self.params)
        self.params.registerParameterManager(KEY_ATTRIBUTE_NAME, key)

    def _initParams(self, param_file, outside_args, system_loader):
        env = self.params.environment

        loaded_addon = env.getParameter(ADDONLIST_KEY, perfect_match=True)
        loaded_addon.getValue()["pyshell.addons.system"] = system_loader

        if param_file is not None:
            parameter_file = env.getParameter(ENVIRONMENT_PARAMETER_FILE_KEY,
                                              perfect_match=True)

            parameter_file.setValue(param_file)

        # init local level
        # TODO remove me as soon as level has been removed
        self.params.pushVariableLevelForThisThread()

        # these variable has to be defined here, because they have to be
        # local type.  So it is not possible to declare them in an addon
        # because only global variable are allowed there
        # TODO this operation will occur at each thread creation
        #   it could be interresting to have a generic method
        var = self.params.variable
        if outside_args is None:
            outside_args = ()

        all_in_one = ' '.join(str(x) for x in outside_args)

        # all outside argument in one string
        args_string = VarParameter(all_in_one)
        args_string.settings.setTransient(True)
        var.setParameter("*", args_string,)

        # outside argument count
        arg_count = VarParameter(len(outside_args))
        arg_count.settings.setTransient(True)
        var.setParameter("#", arg_count)

        # all outside argument
        all_args = VarParameter(outside_args)
        all_args.settings.setTransient(True)
        var.setParameter("@", all_args)

        # last pid started in background
        last_pid_var = VarParameter("")
        last_pid_var.settings.setTransient(True)
        var.setParameter("!", last_pid_var)

        # current process id
        current_pid_var = VarParameter(threading.current_thread().ident)
        current_pid_var.settings.setTransient(True)
        var.setParameter("$", current_pid_var)

        # value from last command
        last_result_var = VarParameter(())
        last_result_var.settings.setTransient(True)
        var.setParameter("?", last_result_var)

    def _initPrinter(self):
        # # prepare the printing system # #
        printer = Printer.getInstance()
        printer.setReplFunction(self.printAsynchronousOnShellV2)
        printer.setPromptShowedContext(self.promptWaitingValuable)
        printer.setParameters(self.params)

    def _startUp(self):
        env = self.params.environment

        # load parameter addon
        loaded_addons = env.getParameter(ADDONLIST_KEY,
                                         perfect_match=True)

        # load parameter
        parameter_file = env.getParameter(ENVIRONMENT_PARAMETER_FILE_KEY,
                                          perfect_match=True)

        with self.exceptionManager("fail to load parameter file"):
            system.loadAddonFun("pyshell.addons.parameter",
                                self.params,
                                None,
                                loaded_addons)
            parameter.loadParameter(parameter_file, self.params)

        # load addon
        addon_to_load = env.getParameter(ENVIRONMENT_ADDON_TO_LOAD_KEY,
                                         perfect_match=True)

        with self.exceptionManager("An error occurred during startup addon"
                                   "loading"):
            system.loadAddonOnStartUp(addon_to_load,
                                      self.params,
                                      loaded_addons)

        # load history
        use_history = env.getParameter(ENVIRONMENT_USE_HISTORY_KEY,
                                       perfect_match=True)
        history_file = env.getParameter(ENVIRONMENT_HISTORY_FILE_NAME_KEY,
                                        perfect_match=True)

        with self.exceptionManager("fail to load history file"):
            std.historyLoad(use_history, history_file)

    def _atExit(self):
        env = self.params.environment

        # parameter save
        parameter_file = env.getParameter(ENVIRONMENT_PARAMETER_FILE_KEY,
                                          perfect_match=True)

        with self.exceptionManager("fail to save parameters"):
            parameter.saveParameter(parameter_file, self.params)

        # history save
        use_history = env.getParameter(ENVIRONMENT_USE_HISTORY_KEY,
                                       perfect_match=True)
        history_file = env.getParameter(ENVIRONMENT_HISTORY_FILE_NAME_KEY,
                                        perfect_match=True)

        with self.exceptionManager("fail to save history"):
            std.historySave(use_history, history_file)

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
