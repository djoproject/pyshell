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
from contextlib import contextmanager

from tries import multiLevelTries
from tries.exception import pathNotExistsTriesException

from pyshell.addons import std
from pyshell.addons import system
from pyshell.command.procedure import FileProcedure
from pyshell.control import ControlCenter
from pyshell.utils.constants import CONTEXT_EXECUTION_KEY
from pyshell.utils.constants import CONTEXT_EXECUTION_SHELL
from pyshell.utils.constants import DEBUG_ENVIRONMENT_NAME
from pyshell.utils.constants import ENVIRONMENT_ADDON_TO_LOAD_KEY
from pyshell.utils.constants import ENVIRONMENT_CONFIG_DIRECTORY_KEY
from pyshell.utils.constants import ENVIRONMENT_HISTORY_FILE_NAME_KEY
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.constants import ENVIRONMENT_PROMPT_DEFAULT
from pyshell.utils.constants import ENVIRONMENT_PROMPT_KEY
from pyshell.utils.constants import ENVIRONMENT_USE_HISTORY_KEY
from pyshell.utils.exception import ListOfException
from pyshell.utils.executing import execute
from pyshell.utils.misc import getTerminalSize
from pyshell.utils.parsing import Parser
from pyshell.utils.printing import Printer
from pyshell.utils.printing import error
from pyshell.utils.printing import printException
from pyshell.utils.printing import warning
from pyshell.utils.setargs import setArgs
from pyshell.utils.valuable import SimpleValuable

try:
    input = raw_input
except:
    pass

# TODO 1: the second part of the __init__ is not an init part
#   it is more like the first part of the running.
#   So it could move in the main loop method or in another method.

# TODO 2: it should be possible to choose the profile to load wiht system
#   there is no choice by default.


class CommandExecuter():
    def __init__(self, param_directory_path=None, outside_args=None):
        self.params = ControlCenter()
        self.promptWaitingValuable = SimpleValuable(False)
        self._initPrinter()
        atexit.register(self._atExit)

        self._loadSystemAddon()
        self._initParams(param_directory_path, outside_args)
        self._startUp()

    def _loadSystemAddon(self):
        # because the system addon is loaded manually, need to register it
        addon_dico = self.params.getAddonManager()
        addon_dico["pyshell.addons.system"] = system._loaders

        loaded = False
        with self.exceptionManager("fail to load addon "
                                   "'pyshell.addons.system'"):
            system._loaders.load(container=self.params, profile_name=None)
            loaded = True

        # load addon system (if not loaded, can't do anything)
        if not loaded:
            print("without this addon, the application can not do anything"
                  " ==> exit.")  # noqa
            exit(-1)

    def _initParams(self, param_directory_path, outside_args):
        env = self.params.getEnvironmentManager()

        # set the parameter directory
        if param_directory_path is not None:
            parameter_directory = env.getParameter(
                ENVIRONMENT_CONFIG_DIRECTORY_KEY,
                perfect_match=True)

            if parameter_directory is not None:
                parameter_directory.setValue(param_directory_path)

        # these variable has to be defined here, because they have to be
        # local type.  So it is not possible to declare them in an addon
        # because only global variable are allowed there
        setArgs(self.params, outside_args or ())

    def _initPrinter(self):
        # # prepare the printing system # #
        printer = Printer.getInstance()
        printer.setReplFunction(self.printAsynchronousOnShellV2)
        printer.setPromptShowedContext(self.promptWaitingValuable)
        printer.setParameters(self.params)

    def _startUp(self):
        env = self.params.getEnvironmentManager()

        # load startup addon
        addon_to_load = env.getParameter(ENVIRONMENT_ADDON_TO_LOAD_KEY,
                                         perfect_match=True)

        with self.exceptionManager("An error occurred during startup addon "
                                   "loading"):
            system.loadAddonOnStartUp(addon_to_load, self.params)

        # load history
        use_history = env.getParameter(ENVIRONMENT_USE_HISTORY_KEY,
                                       perfect_match=True)
        parameter_directory = env.getParameter(
            ENVIRONMENT_CONFIG_DIRECTORY_KEY,
            perfect_match=True)
        history_file = env.getParameter(ENVIRONMENT_HISTORY_FILE_NAME_KEY,
                                        perfect_match=True)

        with self.exceptionManager("fail to load history file"):
            std.historyLoad(use_history, parameter_directory, history_file)

    def _atExit(self):
        env = self.params.getEnvironmentManager()

        # history save
        use_history = env.getParameter(ENVIRONMENT_USE_HISTORY_KEY,
                                       perfect_match=True)
        parameter_directory = env.getParameter(
            ENVIRONMENT_CONFIG_DIRECTORY_KEY,
            perfect_match=True)
        history_file = env.getParameter(ENVIRONMENT_HISTORY_FILE_NAME_KEY,
                                        perfect_match=True)

        with self.exceptionManager("fail to save history"):
            std.historySave(use_history, parameter_directory, history_file)

        # unload every addon to trigger config file saving
        addon_dico = self.params.getAddonManager()
        addon_system = None
        for addon_name, addon_loader in addon_dico.items():
            if addon_name == "pyshell.addons.system":
                addon_system = addon_loader
                continue

            error_msg = "fail to unload addon '%s'" % addon_name
            with self.exceptionManager(error_msg):
                addon_loader.unload(container=self.params,
                                    profile_name=None)

        # TODO (issue #90) addon system has to be the last to be unloaded
        # because it contains the commands tries.  It will be solved when
        # commands will have their own manager.
        if addon_system is not None:
            error_msg = "fail to unload addon 'pyshell.addons.system'"
            with self.exceptionManager(error_msg):
                addon_system.unload(container=self.params,
                                    profile_name=None)

    def _getPrompt(self):
        env = self.params.getEnvironmentManager()
        prompt_param = env.getParameter(ENVIRONMENT_PROMPT_KEY,
                                        perfect_match=True)

        if prompt_param is None:
            return ENVIRONMENT_PROMPT_DEFAULT
        return prompt_param.getValue()

    def mainLoop(self):
        # enable autocompletion
        if 'libedit' in readline.__doc__:
            import rlcompleter  # NOQA
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

        readline.set_completer(self.complete)

        context = self.params.getContextManager()
        exec_type = context.getParameter(CONTEXT_EXECUTION_KEY,
                                         perfect_match=True)
        if exec_type is not None:
            exec_type.setSelectedValue(CONTEXT_EXECUTION_SHELL)

        # mainloop
        while True:
            # read prompt
            prompt = self._getPrompt()
            self.promptWaitingValuable.setValue(True)
            try:
                cmd = input(prompt)
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
        prompt = self._getPrompt()
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
        env = self.params.getEnvironmentManager()
        ltries_param = env.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY,
                                        perfect_match=True)

        if ltries_param is None:
            ltries = multiLevelTries()
        else:
            ltries = ltries_param.getValue()

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
            context = self.params.getContextManager()
            debug_level = context.getParameter(DEBUG_ENVIRONMENT_NAME,
                                               perfect_match=True)
            if debug_level is None or debug_level.getSelectedValue() > 0:
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
        # TODO bug, CONTEXT_EXECUTION_KEY is no more defined when this is
        #   executed, because an app can only be in shell or daemon mode.
        #   Script execution is detectable with the execution level.
        #   And the method executeFile is executed in __main__ before to
        #   know if it is daemon or shell...

        with self.exceptionManager("An error occured during the script "
                                   "execution: "):
            afile = FileProcedure(filename, granularity=granularity)
            afile.execute(args=(), parameter_container=self.params)
