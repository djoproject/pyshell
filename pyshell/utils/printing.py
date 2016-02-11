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
import re
import threading
import traceback

from pyshell.system.container import ParameterContainer
from pyshell.system.parameter import ParameterManager
from pyshell.utils.constants import CONTEXT_COLORATION_DARK
from pyshell.utils.constants import CONTEXT_COLORATION_KEY
from pyshell.utils.constants import CONTEXT_COLORATION_LIGHT
from pyshell.utils.constants import CONTEXT_EXECUTION_KEY
from pyshell.utils.constants import CONTEXT_EXECUTION_SHELL
from pyshell.utils.constants import DEBUG_ENVIRONMENT_NAME
from pyshell.utils.constants import ENVIRONMENT_TAB_SIZE_KEY
from pyshell.utils.exception import ListOfException
from pyshell.utils.exception import NOTICE
from pyshell.utils.exception import PyshellException
from pyshell.utils.exception import WARNING
from pyshell.utils.valuable import DefaultValuable
from pyshell.utils.valuable import Valuable

_EMPTYSTRING = ""

# http://misc.flogisoft.com/bash/tip_colors_and_formatting
LIGHTMAUVE = '\033[95m'
LIGHTBLUE = '\033[94m'
LIGHTORANGE = '\033[93m'
LIGHTGREEN = '\033[92m'
LIGHTRED = '\033[91m'

DARKMAUVE = '\033[35m'
DARKBLUE = '\033[34m'
DARKORANGE = '\033[33m'
DARKGREEN = '\033[32m'
DARKRED = '\033[31m'

UNDERLINE = '\033[4m'
BOLT = '\033[1m'
ENDC = '\033[0m'

ANSI_ESCAPE = re.compile(r'\x1b[^m]*m')


class Printer(object):
    _printerLock = threading.RLock()
    _instance = None

    def __init__(self):
        if Printer._instance is not None:
            raise Exception("("+self.__class__.__name__+") __init__, Try to "
                            "create a new instance of printer, only one is "
                            "allowed for a whole instance of this application,"
                            " use getInstance method")

        self.replWriteFunction = None
        self.promptShowedContext = DefaultValuable(False)
        self.params = ParameterContainer()
        self.params.registerParameterManager("environment", ParameterManager())
        self.params.registerParameterManager("context", ParameterManager())

    def __enter__(self):
        return Printer._printerLock.__enter__()

    def __exit__(self, type, value, traceback):
        return Printer._printerLock.__exit__(type, value, traceback)

    def setReplFunction(self, fun):
        if not hasattr(fun, "__call__"):
            raise Exception("("+self.__class__.__name__+") setREPLFunction, "
                            "invalid repl function, must be a callable object")

        self.replWriteFunction = fun

    def setParameters(self, params):
        if not isinstance(params, ParameterContainer):
            raise Exception("("+self.__class__.__name__+") setParameters, "
                            "invalid params, a ParameterContainer was expected"
                            ", got '"+type(params)+"'")

        self.params = params

    def setPromptShowedContext(self, context):
        if not isinstance(context, Valuable):
            raise Exception("("+self.__class__.__name__+") "
                            "setPromptShowedContext, invalid running context, "
                            "must be an instance of Valuable")

        self.promptShowedContext = context

    def isDarkBackGround(self):
        param = self.params.context.getParameter(CONTEXT_COLORATION_KEY,
                                                 perfect_match=True)
        if param is not None:
            return param.getSelectedValue() == CONTEXT_COLORATION_DARK

        return False

    def isLightBackGround(self):
        param = self.params.context.getParameter(CONTEXT_COLORATION_KEY,
                                                 perfect_match=True)
        if param is not None:
            return param.getSelectedValue() == CONTEXT_COLORATION_LIGHT

        return False

    def isInShell(self):
        param = self.params.context.getParameter(CONTEXT_EXECUTION_KEY,
                                                 perfect_match=True)
        if param is not None:
            return param.getSelectedValue() == CONTEXT_EXECUTION_SHELL

        return False

    def isPromptShowed(self):
        return self.promptShowedContext.getValue()

    def isDebugEnabled(self):
        param = self.params.context.getParameter(DEBUG_ENVIRONMENT_NAME,
                                                 perfect_match=True)
        if param is not None:
            return param.getSelectedValue() > 0

        return False

    def getDebugLevel(self):
        param = self.params.context.getParameter(DEBUG_ENVIRONMENT_NAME,
                                                 perfect_match=True)
        if param is not None:
            return param.getSelectedValue()

        return 0

    def getSpacingSize(self):
        param = self.params.environment.getParameter(ENVIRONMENT_TAB_SIZE_KEY,
                                                     perfect_match=True)
        if param is not None:
            return param.getValue()

        return 0

    @staticmethod
    def getInstance():
        if Printer._instance is None:
            with Printer._printerLock:
                if Printer._instance is None:
                    Printer._instance = Printer()

        return Printer._instance

    def cprint(self, out):
        if out is None:
            return

        # remove ansi annotation if not in shell mode or if stdout is
        # redirected to a file
        if (not self.isInShell() or
           (not self.isDarkBackGround() and not self.isLightBackGround()) or
           not (os.fstat(0) == os.fstat(1))):
            out = ANSI_ESCAPE.sub('', str(out))

        out = self.indentString(out)

        with Printer._printerLock:
            if (self.isInShell() and self.isPromptShowed() and
               self.replWriteFunction is not None):
                self.replWriteFunction(out)
            else:
                print(out)  # noqa

    def indentListOfToken(self, token_list):
        if len(token_list) == 0:
            return ()

        to_ret = []

        for token in token_list:
            to_ret.append(self.indentString(str(token)))

        return to_ret

    def indentString(self, string):

        strings = string.split("\n")
        out = ""
        space = " " * self.getSpacingSize()

        for s in strings:
            out += space + s + "\n"

        out = out[:-1]

        return out

    def _formatColor(self, text, light, dark):
        if not self.isInShell():
            return text

        if self.isLightBackGround():
            return light+text+ENDC

        if self.isDarkBackGround():
            return dark+text+ENDC

        return text

    def _format(self, text, effect):
        if not self.isInShell():
            return text

        return effect+text+ENDC

    def formatRed(self, text):
        return self._formatColor(text, LIGHTRED, DARKRED)

    def formatBlue(self, text):
        return self._formatColor(text, LIGHTBLUE, DARKBLUE)

    def formatGreen(self, text):
        return self._formatColor(text, LIGHTGREEN, DARKGREEN)

    def formatOrange(self, text):
        return self._formatColor(text, LIGHTORANGE, DARKORANGE)

    def formatMauve(self, text):
        return self._formatColor(text, LIGHTMAUVE, DARKMAUVE)

    def formatBolt(self, text):
        return self._format(text, BOLT)

    def formatUnderline(self, text):
        return self._format(text, UNDERLINE)

    def info(self, string):
        self.cprint(string)

    def notice(self, string):
        self.cprint(self.formatGreen(string))

    def warning(self, string):
        self.cprint(self.formatOrange(string))

    def error(self, string):
        self.cprint(self.formatRed(string))

    def debug(self, level, string):
        if level > self.getDebugLevel():
            return

        self.cprint(self.formatOrange(string))


def _toLineString(args, kwargs):
    s = ' '.join(str(x) for x in args)
    s2 = ' '.join(str(k)+"="+str(v) for k, v in kwargs.items())

    if len(s) > 0:
        if len(s2) > 0:
            return s + " " + s2
        return s
    return s2


def formatRed(text):
    printer = Printer.getInstance()
    return printer.formatRed(text)


def formatBlue(text):
    printer = Printer.getInstance()
    return printer.formatBlue(text)


def formatGreen(text):
    printer = Printer.getInstance()
    return printer.formatGreen(text)


def formatOrange(text):
    printer = Printer.getInstance()
    return printer.formatOrange(text)


def formatMauve(text):
    printer = Printer.getInstance()
    return printer.formatMauve(text)


def formatBolt(text):
    printer = Printer.getInstance()
    return printer.formatBolt(text)


def formatUnderline(text):
    printer = Printer.getInstance()
    return printer.formatUnderline(text)


def printShell(*args, **kwargs):
    printer = Printer.getInstance()
    printer.info(_toLineString(args, kwargs))


def info(*args, **kwargs):
    printShell(_toLineString(args, kwargs))


def notice(*args, **kwargs):
    printer = Printer.getInstance()
    printer.notice(_toLineString(args, kwargs))


def warning(*args, **kwargs):
    printer = Printer.getInstance()
    printer.warning(_toLineString(args, kwargs))


def error(*args, **kwargs):
    printer = Printer.getInstance()
    printer.error(_toLineString(args, kwargs))


def debug(level, *args, **kwargs):
    printer = Printer.getInstance()
    printer.debug(level, _toLineString(args, kwargs))


def printException(exception, prefix=None, suffix=None):
    printShell(formatException(exception=exception,
                               prefix=prefix,
                               suffix=suffix))


def getPrinterFromExceptionSeverity(severity):  # TODO test it
    # TODO severity have to be an integer

    printer = Printer.getInstance()
    if severity >= NOTICE:
        return printer.formatGreen

    if severity >= WARNING:
        return printer.formatOrange

    return printer.formatRed


def formatException(exception,
                    prefix=None,
                    no_stack_trace_in_case_of_debug=True,
                    suffix=None):
    if exception is None:
        return _EMPTYSTRING

    printer = Printer.getInstance()

    if isinstance(exception, PyshellException):
        if isinstance(exception, ListOfException):
            if len(exception.exceptions) == 0:
                return _EMPTYSTRING

            toprint = ""
            print_fun = printer.formatRed

            if prefix is None:
                space = _EMPTYSTRING
            else:
                toprint += prefix
                space = " " * printer.getSpacingSize()

            if suffix is not None:
                toprint += suffix

            if len(toprint) > 0:
                toprint = printer.formatRed(toprint)
                toprint += "\n"

            for e in exception.exceptions:
                toprint += space
                toprint += formatException(
                    e,
                    no_stack_trace_in_case_of_debug=False)
                toprint += "\n"

            # remove last \n
            toprint = toprint[:-1]
        else:
            if prefix is None:
                prefix = _EMPTYSTRING

            print_fun = getPrinterFromExceptionSeverity(exception.severity)
            toprint = ""

            if prefix is not None:
                toprint += prefix

            toprint += str(exception)

            if suffix is not None:
                toprint += suffix

            toprint = print_fun(toprint)
    else:
        toprint = ""

        if prefix is not None:
            toprint += prefix

        toprint += str(exception)

        if suffix is not None:
            toprint += suffix

        toprint = printer.formatRed(toprint)
        print_fun = printer.formatRed

    if printer.isDebugEnabled() and no_stack_trace_in_case_of_debug:
        stacktrace = traceback.format_exc()
        if stacktrace is not None:
            toprint += print_fun("\n\n"+stacktrace)

    return toprint


def strLength(string):
    return len(ANSI_ESCAPE.sub('', str(string)))
