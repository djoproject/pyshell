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

import os
import readline

from tries.exception import triesException

from pyshell.arg.accessor.environment import EnvironmentAccessor
from pyshell.arg.checker.boolean import BooleanValueArgChecker
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.command.command import MultiOutput
from pyshell.register.command import registerCommand
from pyshell.register.command import registerStopHelpTraversalAt
from pyshell.utils.constants import ENVIRONMENT_CONFIG_DIRECTORY_KEY
from pyshell.utils.constants import ENVIRONMENT_HISTORY_FILE_NAME_KEY
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.constants import ENVIRONMENT_TAB_SIZE_KEY
from pyshell.utils.constants import ENVIRONMENT_USE_HISTORY_KEY
from pyshell.utils.constants import TAB_SIZE
from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.exception import USER_ERROR
from pyshell.utils.exception import USER_WARNING
from pyshell.utils.exception import WARNING
from pyshell.utils.postprocess import listFlatResultHandler
from pyshell.utils.postprocess import listResultHandler

# # FUNCTION SECTION # #


def exitFun():
    "Exit the program"
    exit()


@shellMethod(args=ListArgChecker(DefaultChecker.getArg()))
def echo(args):
    "echo all the args"

    s = []
    for a in args:
        s.append(str(a))

    return listFlatResultHandler(s)


@shellMethod(args=ListArgChecker(DefaultChecker.getArg()))
def echo16(args):
    "echo all the args in hexa"

    s = []
    for a in args:
        try:
            s.append("0x%x" % int(a))
        except ValueError:
            s.append(str(a))

    return listFlatResultHandler(s)


@shellMethod(args=ListArgChecker(DefaultChecker.getInteger()))
def intToAscii(args):
    "echo all the args into chars"
    s = ""
    for a in args:
        try:
            # do not convert unicode, only ascii
            if a >= 0 and a < 128:
                s += chr(a)
            else:
                s += str(a)
        except ValueError:
            s += str(a)

    return listFlatResultHandler((s, ))


def _findCommand(args, mltries):
    try:
        search_result = mltries.getValue().advancedSearch(args, False)
    except triesException as te:
        excmsg = "failed to find the command '%s', reason: %s"
        excmsg %= (args, te,)
        raise DefaultPyshellException(excmsg)

    if search_result.isAmbiguous():
        token_index = len(search_result.existingPath) - 1
        tries = search_result.existingPath[token_index][1].localTries
        keylist = tries.getKeyList(args[token_index])

        excmsg = "ambiguity on command '%s', token '%s', possible value: %s"
        excmsg %= (" ".join(args), args[token_index], ", ".join(keylist),)
        raise DefaultPyshellException(excmsg, USER_WARNING)

    if not search_result.isPathFound():
        token_not_found = search_result.getNotFoundTokenList()
        excmsg = "command not found, unknown token '%s'"
        excmsg %= token_not_found[0]
        raise DefaultPyshellException(excmsg, USER_ERROR)

    if not search_result.isAvalueOnTheLastTokenFound():
        excmsg = ("incomplete command call, no usage information available, "
                  "try to complete the command name")
        raise DefaultPyshellException(excmsg, USER_WARNING)

    return search_result


@shellMethod(
    args=ListArgChecker(DefaultChecker.getArg(), 1),
    mltries=EnvironmentAccessor(ENVIRONMENT_LEVEL_TRIES_KEY))
def usageFun(args, mltries):
    "print the usage of a fonction"
    search_result = _findCommand(args, mltries)
    cmd = search_result.getLastTokenFoundValue()
    command_name = search_result.getFoundCompletePath()
    return " ".join(command_name) + " " + cmd.usage()


@shellMethod(
    args=ListArgChecker(DefaultChecker.getArg(), 1),
    mltries=EnvironmentAccessor(ENVIRONMENT_LEVEL_TRIES_KEY),
    tabsize=EnvironmentAccessor(ENVIRONMENT_TAB_SIZE_KEY))
def man(args, mltries, tabsize):
    """ manual for the command """
    search_result = _findCommand(args, mltries)
    cmd = search_result.getLastTokenFoundValue()
    command_name = search_result.getFoundCompletePath()
    description = cmd.help_message

    if tabsize is None:
        tabspace = " " * TAB_SIZE
    else:
        tabspace = " " * tabsize.getValue()

    return ("Command Name:",
            "%s%s" % (tabspace, " ".join(command_name),),
            "",
            "Description:",
            "%s%s" % (tabspace, description,),
            "",
            "Usage: ",
            "%s%s %s" % (tabspace, " ".join(command_name), cmd.usage(),),
            "",)


def _checkAmbiguity(mltries, full_args):
    # manage ambiguity cases
    advanced_result = mltries.advancedSearch(full_args, False)
    ambiguity_on_last_token = False
    if advanced_result.isAmbiguous():
        token_index = len(advanced_result.existingPath) - 1
        tries = advanced_result.existingPath[token_index][1].localTries
        keylist = tries.getKeyList(full_args[token_index])

        # don't care about ambiguity on last token
        ambiguity_on_last_token = token_index == len(full_args) - 1
        if not ambiguity_on_last_token:
            # if ambiguity occurs on an intermediate key, stop the search
            excmsg = ("Ambiguous value on key index <%s>, possible value: "
                      "%s")
            excmsg %= (token_index, ", ".join(keylist),)
            raise DefaultPyshellException(excmsg, USER_WARNING)

    # manage not found case
    if not ambiguity_on_last_token and not advanced_result.isPathFound():
        not_found_token = advanced_result.getNotFoundTokenList()
        excmsg = "unkwnon token %s: '%s'"
        excmsg %= (advanced_result.getTokenFoundCount(),
                   not_found_token[0],)
        raise DefaultPyshellException(excmsg, USER_ERROR)


def _buildHelp(mltries, args, suffix=None, full_args=None):
    dic = mltries.buildDictionnary(args,
                                   ignoreStopTraversal=True,
                                   addPrexix=True,
                                   onlyPerfectMatch=False)

    stops = {}
    string_keys = []
    for k in dic.keys():
        # the last corresponding token in k must start with the last token of
        # args => suffix
        index = len(full_args) - 1
        if index >= 0 and index < len(k) and not k[index].startswith(suffix):
            continue

        # is there a disabled token ?
        for i in range(1, len(k)+1):
            # the path k[0:i] is disabled, not the first occurence, just save
            #   the next token to create the stop informations.
            if k[0:i] in stops:
                if i < len(k) and k[i] not in stops[k[0:i]]:
                    stops[k[0:i]].append(k[i])

                break

            # is the path k[0:i] disabled?
            if i > len(full_args) and mltries.isStopTraversal(k[0:i]):
                if i == len(k):
                    stops[k[0:i]] = []
                else:
                    stops[k[0:i]] = ([k[i]])

                break
        else:
            # this path is not disabled and is a full path, build help line
            _helpAddLine(string_keys, k, dic[k])

    # build stop path help
    for stopPath, sub_child in stops.items():
        if len(sub_child) == 0:
            continue

        sub_child = sorted(sub_child)

        if len(sub_child) > 3:
            string = "%s: {%s, ...}"
        else:
            string = "%s: {%s}"

        string %= (" ".join(stopPath), ", ".join(sub_child[0:3]),)
        string_keys.append(string)

    return string_keys


def _helpAddLine(strings, key, command):
    line = " ".join(key)
    hmess = command.help_message
    if hmess is not None and len(hmess) > 0:
        line += ": " + hmess

    strings.append(line)


@shellMethod(
    mltries=EnvironmentAccessor(ENVIRONMENT_LEVEL_TRIES_KEY),
    args=ListArgChecker(DefaultChecker.getArg()))
def helpFun(mltries, args=None):
    "print the help"

    mltries = mltries.getValue()
    suffix = ""
    full_args = ()

    if args is None:
        args = ()

    # little hack to be able to get help for a function that has another
    # function path as suffix
    if len(args) > 0:
        full_args = args[:]
        suffix = args[-1]
        args = args[:-1]
        _checkAmbiguity(mltries, full_args)

    strings = _buildHelp(mltries, args, suffix, full_args)

    # build the "real" help
    if len(strings) == 0:
        raise DefaultPyshellException("no help available", WARNING)

    return sorted(strings)


@shellMethod(start=IntegerArgChecker(),
             stop=IntegerArgChecker(),
             step=IntegerArgChecker(),
             multi_output=BooleanValueArgChecker())
def generator(start=0, stop=100, step=1, multi_output=True):
    "generate a list of integer"
    if multi_output:
        return MultiOutput(list(range(start, stop, step)))
    else:
        return list(range(start, stop, step))


@shellMethod(
    use_history=EnvironmentAccessor(ENVIRONMENT_USE_HISTORY_KEY),
    parameter_directory=EnvironmentAccessor(ENVIRONMENT_CONFIG_DIRECTORY_KEY),
    history_file=EnvironmentAccessor(ENVIRONMENT_HISTORY_FILE_NAME_KEY))
def historyLoad(use_history, parameter_directory, history_file):
    "save readline history"

    if (use_history is None or
       parameter_directory is None or
       history_file is None or
       not use_history.getValue()):
        return

    file_name = history_file.getValue()
    directory_path = parameter_directory.getValue()
    file_path = os.path.join(directory_path, file_name)

    try:
        readline.read_history_file(file_path)
    except IOError:
        pass


@shellMethod(
    use_history=EnvironmentAccessor(ENVIRONMENT_USE_HISTORY_KEY),
    parameter_directory=EnvironmentAccessor(ENVIRONMENT_CONFIG_DIRECTORY_KEY),
    history_file=EnvironmentAccessor(ENVIRONMENT_HISTORY_FILE_NAME_KEY))
def historySave(use_history, parameter_directory, history_file):
    "load readline history"

    if (use_history is None or
       parameter_directory is None or
       history_file is None or
       not use_history.getValue()):
        return

    file_name = history_file.getValue()
    directory_path = parameter_directory.getValue()
    file_path = os.path.join(directory_path, file_name)
    readline.write_history_file(file_path)

# # REGISTER SECTION # #

registerCommand(("exit",), pro=exitFun)
registerCommand(("quit",), pro=exitFun)
registerStopHelpTraversalAt(("quit",))

registerCommand(("echo",), post=echo)
registerCommand(("echo16",), post=echo16)
registerCommand(("toascii",), post=intToAscii)

registerCommand(("usage",), pro=usageFun, post=listFlatResultHandler)
registerCommand(("man",), pro=man, post=listResultHandler)
registerCommand(("help",), pro=helpFun, post=listResultHandler)
registerCommand(("?",), pro=helpFun, post=listResultHandler)
registerStopHelpTraversalAt(("?",))
registerCommand(("range",), pre=generator)
registerCommand(("history", "load",), pro=historyLoad)
registerCommand(("history", "save",), pro=historySave)
registerStopHelpTraversalAt(("history",))
