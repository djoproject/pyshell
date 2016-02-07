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

# TODO implements these commands
#   shift args
#       info in param.var
#   set args
#       info in param.var
#   goto (procedure line)
#       get procedure from parameterContainer
#   soft kill (thread id) (level or None)
#       get procedure from parameterContainer
#   hard kill
#       HOWTO ? is it reallistic to implement ?
#           just manage to kill the thread immediatelly
#               what about lock in this case ?
#   list process
#       get procedure list from parameterContainer
#   command to startreadline then execute
#   HOWTO ?

import readline

from pyshell.arg.argchecker import IntegerArgChecker
from pyshell.arg.argchecker import booleanValueArgChecker
from pyshell.arg.argchecker import defaultInstanceArgChecker
from pyshell.arg.argchecker import environmentParameterChecker
from pyshell.arg.argchecker import listArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.command.command import MultiOutput
from pyshell.loader.command import registerCommand
from pyshell.loader.command import registerStopHelpTraversalAt
from pyshell.utils.constants import ENVIRONMENT_HISTORY_FILE_NAME_KEY
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.constants import ENVIRONMENT_USE_HISTORY_KEY
from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.exception import USER_ERROR
from pyshell.utils.exception import USER_WARNING
from pyshell.utils.exception import WARNING
from pyshell.utils.misc import createParentDirectory
from pyshell.utils.postProcess import listFlatResultHandler
from pyshell.utils.postProcess import listResultHandler

from tries.exception import triesException

# # FUNCTION SECTION # #


def exitFun():
    "Exit the program"
    exit()


@shellMethod(args=listArgChecker(
    defaultInstanceArgChecker.getArgCheckerInstance()))
def echo(args):
    "echo all the args"

    s = []
    for a in args:
        s.append(str(a))

    return listFlatResultHandler(s)


@shellMethod(args=listArgChecker(
    defaultInstanceArgChecker.getArgCheckerInstance()))
def echo16(args):
    "echo all the args in hexa"

    s = []
    for a in args:
        try:
            s.append("0x%x" % int(a))
        except ValueError:
            s.append(str(a))

    return listFlatResultHandler(s)


@shellMethod(args=listArgChecker(
    defaultInstanceArgChecker.getIntegerArgCheckerInstance()))
def intToAscii(args):
    "echo all the args into chars"
    s = ""
    for a in args:
        try:
            s += chr(a)
        except ValueError:
            s += str(a)

    return listFlatResultHandler((s, ))


@shellMethod(
    args=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(), 1),
    mltries=environmentParameterChecker(ENVIRONMENT_LEVEL_TRIES_KEY))
def usageFun(args, mltries):
    "print the usage of a fonction"

    try:
        searchResult = mltries.getValue().advancedSearch(args, False)
    except triesException as te:
        raise DefaultPyshellException(
            "failed to find the command '" +
            str(args) +
            "', reason: " +
            str(te))

    if searchResult.isAmbiguous():
        tokenIndex = len(searchResult.existingPath) - 1
        tries = searchResult.existingPath[tokenIndex][1].localTries
        keylist = tries.getKeyList(args[tokenIndex])

        raise DefaultPyshellException("ambiguity on command '" +
                                      " ".join(args) +
                                      "', token '" +
                                      str(args[tokenIndex]) +
                                      "', possible value: " +
                                      ", ".join(keylist), USER_WARNING)

    if not searchResult.isPathFound():
        tokenNotFound = searchResult.getNotFoundTokenList()
        raise DefaultPyshellException(
            "command not found, unknown token '" +
            tokenNotFound[0] +
            "'",
            USER_ERROR)

    if not searchResult.isAvalueOnTheLastTokenFound():
        raise DefaultPyshellException("incomplete command call, no usage "
                                      "information available, try to complete "
                                      "the command name",
                                      USER_WARNING)

    cmd = searchResult.getLastTokenFoundValue()

    # TODO the command name has been removed, need to add complete command
    # path + usage
    return cmd.usage()


@shellMethod(
    mltries=environmentParameterChecker(ENVIRONMENT_LEVEL_TRIES_KEY),
    args=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def helpFun(mltries, args=None):
    "print the help"

    if args is None:
        args = ()

    # little hack to be able to get help about for a function who has another
    # function as suffix
    if len(args) > 0:
        fullArgs = args[:]
        suffix = args[-1]
        args = args[:-1]
    else:
        suffix = None
        fullArgs = None

    # manage ambiguity cases
    if fullArgs is not None:
        advancedResult = mltries.getValue().advancedSearch(fullArgs, False)
        ambiguityOnLastToken = False
        if advancedResult.isAmbiguous():
            tokenIndex = len(advancedResult.existingPath) - 1
            tries = advancedResult.existingPath[tokenIndex][1].localTries
            keylist = tries.getKeyList(fullArgs[tokenIndex])

            # don't care about ambiguity on last token
            ambiguityOnLastToken = tokenIndex == len(fullArgs) - 1
            if not ambiguityOnLastToken:
                # if ambiguity occurs on an intermediate key, stop the search
                raise DefaultPyshellException(
                    "Ambiguous value on key index <" +
                    str(tokenIndex) +
                    ">, possible value: " +
                    ", ".join(keylist),
                    USER_WARNING)

        # manage not found case
        if not ambiguityOnLastToken and not advancedResult.isPathFound():
            notFoundToken = advancedResult.getNotFoundTokenList()
            excmsg = ("unkwnon token " +
                      str(advancedResult.getTokenFoundCount()) +
                      ": '"+notFoundToken[0]+"'")
            raise DefaultPyshellException(excmsg, USER_ERROR)

    found = []
    stringKeys = []
    # cmd with stop traversal, this will retrieve every tuple path/value
    dic = mltries.getValue().buildDictionnary(
        args,
        ignoreStopTraversal=False,
        addPrexix=True,
        onlyPerfectMatch=False)
    for k in dic.keys():
        # if (fullArgs is None and len(k) < len(args)) or
        # (fullArgs is not None and len(k) < len(fullArgs)):
        #    continue

        # the last corresponding token in k must start with the last token of
        # args => suffix
        if suffix is not None and len(k) >= (
                len(args) + 1) and not k[len(args)].startswith(suffix):
            continue

        # is it a hidden cmd ?
        if mltries.getValue().isStopTraversal(k):
            continue

        line = " ".join(k)
        hmess = dic[k].helpMessage
        if hmess is not None and len(hmess) > 0:
            line += ": " + hmess

        found.append((k, hmess,))
        stringKeys.append(line)

    # cmd without stop traversal (parent category only)
    dic2 = mltries.getValue().buildDictionnary(
        args, ignoreStopTraversal=True, addPrexix=True, onlyPerfectMatch=False)
    stop = {}
    for k in dic2.keys():
        # if k is in dic, already processed
        if k in dic:
            continue

        # if (fullArgs is None and len(k) < len(args))
        #   or (fullArgs is not None and len(k) < len(fullArgs)):
        #    continue

        # the last corresponding token in k must start with the last token of
        # args => suffix
        if suffix is not None and len(k) >= (
                len(args) + 1) and not k[len(args)].startswith(suffix):
            continue

        # is it a hidden cmd ? only for final node, because they don't
        # appear in dic2
        # useless, "k in dic" is enough
        # if mltries.getValue().isStopTraversal(k):
        #    continue

        # is there a disabled token ?
        for i in range(1, len(k)):
            # this level of k is disabled, not the first occurence
            if k[0:i] in stop:
                if i == len(k):
                    break

                if k[i] not in stop[k[0:i]]:
                    stop[k[0:i]].append(k[i])

                break

            # this level of k is disabled, first occurence
            if mltries.getValue().isStopTraversal(k[0:i]):

                # if the disabled string token is in the args to print, it is
                # equivalent to enabled
                equiv = False
                if fullArgs is not None and len(fullArgs) >= len(k[0:i]):
                    equiv = True
                    for j in range(0, min(len(fullArgs), len(k))):
                        if not k[j].startswith(fullArgs[j]):
                            equiv = False

                # if the args are not a prefix for every corresponding key, is
                # is disabled
                if not equiv:
                    if i == len(k):
                        stop[k[0:i]] = []
                    else:
                        stop[k[0:i]] = ([k[i]])

                    break

            # this path is not disabled and it is the last path, occured with a
            # not disabled because in the path
            if i == (len(k) - 1):
                line = " ".join(k)
                hmess = dic2[k].helpMessage
                if hmess is not None and len(hmess) > 0:
                    line += ": " + hmess

                found.append((k, hmess,))
                stringKeys.append(line)

    # build the "real" help
    if len(stop) == 0:
        if len(found) == 0:
            if len(fullArgs) > 0:
                raise DefaultPyshellException(
                    "unkwnon token 0: '" + fullArgs[0] + "'", USER_ERROR)
            else:
                raise DefaultPyshellException("no help available", WARNING)

            return ()
        elif len(found) == 1:
            if found[0][1] is None:
                description = "No description"
            else:
                description = found[0][1]

            return ("Command Name:", "       " +
                    " ".join(found[0][0]), "", "Description:",
                    "       " + description, "", "Usage: ", "       " +
                    usageFun(found[0][0], mltries), "",)

    for stopPath, subChild in stop.items():
        if len(subChild) == 0:
            continue

        string = " ".join(stopPath) + ": {" + ",".join(subChild[0:3])
        if len(subChild) > 3:
            string += ",..."

        stringKeys.append(string + "}")

    return sorted(stringKeys)


@shellMethod(start=IntegerArgChecker(),
             stop=IntegerArgChecker(),
             step=IntegerArgChecker(),
             multiOutput=booleanValueArgChecker())
def generator(start=0, stop=100, step=1, multiOutput=True):
    "generate a list of integer"
    if multiOutput:
        return MultiOutput(range(start, stop, step))
    else:
        return range(start, stop, step)


@shellMethod(
    useHistory=environmentParameterChecker(ENVIRONMENT_USE_HISTORY_KEY),
    historyFile=environmentParameterChecker(ENVIRONMENT_HISTORY_FILE_NAME_KEY))
def historyLoad(useHistory, historyFile):
    "save readline history"

    if not useHistory.getValue():
        return

    try:
        readline.read_history_file(historyFile.getValue())
    except IOError:
        pass


@shellMethod(
    useHistory=environmentParameterChecker(ENVIRONMENT_USE_HISTORY_KEY),
    historyFile=environmentParameterChecker(ENVIRONMENT_HISTORY_FILE_NAME_KEY))
def historySave(useHistory, historyFile):
    "load readline history"

    if not useHistory.getValue():
        return

    path = historyFile.getValue()
    createParentDirectory(path)
    readline.write_history_file(path)

"""@shellMethod(data = ,
            from = ,
            to = )
def filter(data, from = 0, to=None):
    pass #TODO"""

# # REGISTER SECTION # #

registerCommand(("exit",), pro=exitFun)
registerCommand(("quit",), pro=exitFun)
registerStopHelpTraversalAt(("quit",))

# TODO bof bof d'avoir ces trois là en post, ça crée des trucs bizarres
# genre: echo16 | prox test -expected 5 1 2 3 4 | pcsc transmit
# see BRAINSTORMING file

registerCommand(("echo",), post=echo)
registerCommand(("echo16",), post=echo16)
registerCommand(("toascii",), post=intToAscii)

registerCommand(("usage",), pro=usageFun, post=listFlatResultHandler)
registerCommand(("help",), pro=helpFun, post=listResultHandler)
registerCommand(("?",), pro=helpFun, post=listResultHandler)
registerStopHelpTraversalAt(("?",))
registerCommand(("range",), pre=generator)
registerCommand(("history", "load",), pro=historyLoad)
registerCommand(("history", "save",), pro=historySave)
registerStopHelpTraversalAt(("history",))
