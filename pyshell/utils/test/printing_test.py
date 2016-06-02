#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

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

import sys

import pytest

from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.arg.argchecker import IntegerArgChecker
from pyshell.system.container import ParameterContainer
from pyshell.system.context import ContextParameter
from pyshell.system.context import ContextParameterManager
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.environment import EnvironmentParameterManager
from pyshell.utils.constants import CONTEXT_COLORATION_DARK
from pyshell.utils.constants import CONTEXT_COLORATION_KEY
from pyshell.utils.constants import CONTEXT_COLORATION_LIGHT
from pyshell.utils.constants import CONTEXT_COLORATION_NONE
from pyshell.utils.constants import CONTEXT_EXECUTION_DAEMON
from pyshell.utils.constants import CONTEXT_EXECUTION_KEY
from pyshell.utils.constants import CONTEXT_EXECUTION_SCRIPT
from pyshell.utils.constants import CONTEXT_EXECUTION_SHELL
from pyshell.utils.constants import DEBUG_ENVIRONMENT_NAME
from pyshell.utils.constants import ENVIRONMENT_TAB_SIZE_KEY
from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.exception import ListOfException
from pyshell.utils.exception import NOTICE
from pyshell.utils.exception import WARNING
from pyshell.utils.printing import BOLT
from pyshell.utils.printing import DARKRED
from pyshell.utils.printing import ENDC
from pyshell.utils.printing import LIGHTGREEN
from pyshell.utils.printing import LIGHTORANGE
from pyshell.utils.printing import LIGHTRED
from pyshell.utils.printing import Printer
from pyshell.utils.printing import _toLineString
from pyshell.utils.printing import formatException
from pyshell.utils.valuable import SimpleValuable

try:
    from collections import OrderedDict
except:
    from pyshell.utils.ordereddict import OrderedDict

PY3 = sys.version_info[0] == 3


class TestPrinting(object):

    def setup_method(self, method):
        p = Printer.getInstance()

        self.promptShowedContext = SimpleValuable(True)  # True or False
        p.setPromptShowedContext(self.promptShowedContext)

        self.params = ParameterContainer()
        manager = EnvironmentParameterManager(self.params)
        self.params.registerParameterManager("environment", manager)
        manager = ContextParameterManager(self.params)
        self.params.registerParameterManager("context", manager)

        self.debugContext = ContextParameter(
            value=tuple(range(0, 91)),
            typ=DefaultInstanceArgChecker.getIntegerArgCheckerInstance(),
            default_index=0,
            index=0)
        self.params.context.setParameter(DEBUG_ENVIRONMENT_NAME,
                                         self.debugContext,
                                         local_param=False)
        self.debugContext.settings.setTransient(False)
        self.debugContext.settings.setTransientIndex(False)
        self.debugContext.settings.setRemovable(False)
        self.debugContext.settings.setReadOnly(True)

        self.shellContext = ContextParameter(
            value=(CONTEXT_EXECUTION_SHELL,
                   CONTEXT_EXECUTION_SCRIPT,
                   CONTEXT_EXECUTION_DAEMON,),
            typ=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
            default_index=0)
        self.params.context.setParameter(CONTEXT_EXECUTION_KEY,
                                         self.shellContext,
                                         local_param=False)
        self.shellContext.settings.setTransient(True)
        self.shellContext.settings.setTransientIndex(True)
        self.shellContext.settings.setRemovable(False)
        self.shellContext.settings.setReadOnly(True)

        self.backgroundContext = ContextParameter(
            value=(CONTEXT_COLORATION_LIGHT,
                   CONTEXT_COLORATION_DARK,
                   CONTEXT_COLORATION_NONE,),
            typ=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
            default_index=0)
        self.params.context.setParameter(CONTEXT_COLORATION_KEY,
                                         self.backgroundContext,
                                         local_param=False)
        self.backgroundContext.settings.setTransient(False)
        self.backgroundContext.settings.setTransientIndex(False)
        self.backgroundContext.settings.setRemovable(False)
        self.backgroundContext.settings.setReadOnly(True)

        self.spacingContext = EnvironmentParameter(value=5,
                                                   typ=IntegerArgChecker(0))
        self.params.environment.setParameter(ENVIRONMENT_TAB_SIZE_KEY,
                                             self.spacingContext,
                                             local_param=False)
        self.spacingContext.settings.setTransient(False)
        self.spacingContext.settings.setRemovable(False)
        self.spacingContext.settings.setReadOnly(False)

        p.setParameters(self.params)

    def test_getInstance(self):
        p = Printer.getInstance()
        p2 = Printer.getInstance()
        assert p == p2

    def test_setPromptShowedContext(self):
        with pytest.raises(Exception):
            Printer.getInstance().setPromptShowedContext(("plop",))

    def test_isDarkBackGround(self):
        p = Printer.getInstance()
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_DARK)
        assert p.isDarkBackGround()

    def test_isDarkBackGround2(self):
        p = Printer.getInstance()
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_LIGHT)
        assert not p.isDarkBackGround()

    def test_isDarkBackGround3(self):
        p = Printer.getInstance()
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_NONE)
        assert not p.isDarkBackGround()

    def test_isLightBackGround(self):
        p = Printer.getInstance()
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_DARK)
        assert not p.isLightBackGround()

    def test_isLightBackGround2(self):
        p = Printer.getInstance()
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_LIGHT)
        assert p.isLightBackGround()

    def test_isLightBackGround3(self):
        p = Printer.getInstance()
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_NONE)
        assert not p.isLightBackGround()

    def test_shellContext(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        assert p.isInShell()

    def test_shellContext2(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        assert not p.isInShell()

    def test_shellContext3(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_DAEMON)
        assert not p.isInShell()

    def test_promptShowedContext(self):
        p = Printer.getInstance()
        self.promptShowedContext.setValue(True)
        assert p.isPromptShowed()

    def test_promptShowedContext2(self):
        p = Printer.getInstance()
        self.promptShowedContext.setValue(False)
        assert not p.isPromptShowed()

    def test_debugContext(self):
        p = Printer.getInstance()
        self.debugContext.settings.setIndexValue(0)
        assert not p.isDebugEnabled()
        assert p.getDebugLevel() == 0

    def test_debugContext2(self):
        p = Printer.getInstance()
        self.debugContext.settings.setIndexValue(1)
        assert p.isDebugEnabled()
        assert p.getDebugLevel() == 1

    def test_debugContext3(self):
        p = Printer.getInstance()
        self.debugContext.settings.setIndexValue(90)
        assert p.isDebugEnabled()
        assert p.getDebugLevel() == 90

    def test_formatColor(self):
        p = Printer.getInstance()

        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        assert p.formatRed("plop") == LIGHTRED+"plop"+ENDC

    def test_formatColor2(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        assert p.formatRed("plop") == "plop"

    def test_formatColor3(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_DARK)
        assert p.formatRed("plop") == DARKRED+"plop"+ENDC

    def test_formatColor4(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        assert p.formatRed("plop") == "plop"

    def test_formatColor5(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_NONE)
        assert p.formatRed("plop") == "plop"

    def test_formatColor6(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        assert p.formatRed("plop") == "plop"

    def test_format(self):
        p = Printer.getInstance()

        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        assert p.formatBolt("plop") == BOLT+"plop"+ENDC

    def test_format2(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        assert p.formatBolt("plop") == "plop"

    def test_cprint(self, capsys):
        p = Printer.getInstance()
        p.cprint(None)
        out, err = capsys.readouterr()
        assert out == ""

    def test_cprint2(self, capsys):
        p = Printer.getInstance()

        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        txt = p.formatRed("plop")
        p.cprint(txt)
        out, err = capsys.readouterr()
        assert out == "     "+LIGHTRED+"plop"+ENDC+"\n"

    def test_cprint3(self, capsys):
        p = Printer.getInstance()

        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        txt = p.formatRed("plop")
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        p.cprint(txt)
        out, err = capsys.readouterr()
        assert out == "     plop\n"

    def test_cprint4(self, capsys):
        p = Printer.getInstance()

        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        txt = p.formatRed("plop\nplop")
        p.cprint(txt)
        out, err = capsys.readouterr()
        assert out == "     "+LIGHTRED+"plop"+"\n     "+"plop"+ENDC+"\n"

    def test_cprint5(self, capsys):
        p = Printer.getInstance()

        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        txt = p.formatRed("plop")
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_NONE)
        p.cprint(txt)
        out, err = capsys.readouterr()
        assert out == "     plop\n"

    def test_toLineString(self):
        assert _toLineString((), {}) == ""

    def test_toLineString2(self):
        assert _toLineString(("a",), {}) == "a"

    def test_toLineString3(self):
        assert _toLineString((), {"b": "42"}) == "b=42"

    def test_toLineString4(self):
        assert _toLineString(("a",), {"b": "42"}) == "a b=42"

    def test_toLineString5(self):
        ordered_dict = OrderedDict([("e", "42",), ("f", 23,), ("g", 96)])
        assert _toLineString(("a", "b", "c",),
                             ordered_dict) == "a b c e=42 f=23 g=96"

    def test_formatException(self):
        assert formatException(Exception("toto")) == LIGHTRED+"toto"+ENDC

    def test_formatException2(self):
        expected = LIGHTRED+"toto"+ENDC
        assert formatException(DefaultPyshellException("toto")) == expected

    def test_formatException3(self):
        expected = LIGHTORANGE+"toto"+ENDC
        formated = formatException(DefaultPyshellException("toto", WARNING))
        assert formated == expected

    def test_formatException4(self):
        expected = LIGHTGREEN+"toto"+ENDC
        formated = formatException(DefaultPyshellException("toto", NOTICE))
        assert formated == expected

    def test_formatException4b(self):
        expected = LIGHTGREEN+"plop: toto"+ENDC
        formated = formatException(DefaultPyshellException("toto", NOTICE),
                                   "plop: ")
        assert formated == expected

    def test_formatException5(self):
        l = ListOfException()
        l.addException(Exception("plop"))
        l.addException(DefaultPyshellException("plip", WARNING))
        l.addException(DefaultPyshellException("toto", NOTICE))

        expected = (LIGHTRED+"plop"+ENDC+"\n"+LIGHTORANGE+"plip"+ENDC+"\n" +
                    LIGHTGREEN+"toto"+ENDC)
        assert formatException(l) == expected

    def test_formatException6(self):
        l = ListOfException()
        l.addException(Exception("plop"))
        l.addException(DefaultPyshellException("plip", WARNING))
        l.addException(DefaultPyshellException("toto", NOTICE))

        expected = (LIGHTRED+"plap"+ENDC+"\n"+"     "+LIGHTRED+"plop"+ENDC +
                    "\n"+"     "+LIGHTORANGE+"plip"+ENDC+"\n"+"     " +
                    LIGHTGREEN+"toto"+ENDC)
        assert formatException(l, "plap") == expected

    def test_formatException7(self):
        self.debugContext.settings.setIndexValue(1)

        prefix = (LIGHTORANGE+"toto"+ENDC+LIGHTORANGE+"\n\n"
                  "Traceback (most recent call last):\n"
                  "  File \"")
        if PY3:
            suffix = ("in test_formatException7\n"
                      "    raise DefaultPyshellException(\"toto\", WARNING)\n"
                      "pyshell.utils.exception.DefaultPyshellException: toto\n"
                      ""+ENDC)
        else:
            suffix = ("in test_formatException7\n"
                      "    raise DefaultPyshellException(\"toto\", WARNING)\n"
                      "DefaultPyshellException: toto\n"
                      ""+ENDC)

        try:
            raise DefaultPyshellException("toto", WARNING)
        except Exception as ex:
            formated = formatException(ex)
            assert formated.startswith(prefix)
            assert formated.endswith(suffix)
            assert "printing_test.py" in formated

    def test_formatException8(self):
        self.debugContext.settings.setIndexValue(1)

        l = ListOfException()
        l.addException(Exception("plop"))
        l.addException(DefaultPyshellException("plip", WARNING))
        l.addException(DefaultPyshellException("toto", NOTICE))

        prefix = (LIGHTRED+"plop"+ENDC+"\n"+LIGHTORANGE+"plip"+ENDC +
                  "\n"+LIGHTGREEN+"toto"+ENDC+LIGHTRED+"\n\n"
                  "Traceback (most recent call last):\n"
                  "  File \"")

        if PY3:
            suffix = ("in test_formatException8\n"
                      "    raise l\n"
                      "pyshell.utils.exception.ListOfException: 3 exception(s)"
                      " in list\n"+ENDC)
        else:
            suffix = ("in test_formatException8\n"
                      "    raise l\n"
                      "ListOfException: 3 exception(s) in list\n"
                      ""+ENDC)

        try:
            raise l
        except Exception as ex:
            formated = formatException(ex)
            assert formated.startswith(prefix)
            assert formated.endswith(suffix)
            assert "printing_test.py" in formated

    def test_formatException9(self):
        self.debugContext.settings.setIndexValue(1)

        l = ListOfException()
        l.addException(Exception("plop"))
        l.addException(DefaultPyshellException("plip", WARNING))
        l.addException(DefaultPyshellException("toto", NOTICE))

        prefix = (LIGHTRED+"plap"+ENDC+"\n     "+LIGHTRED+"plop"+ENDC +
                  "\n"+"     "+LIGHTORANGE+"plip"+ENDC+"\n"+"     " +
                  LIGHTGREEN+"toto"+ENDC+LIGHTRED+"\n\n"
                  "Traceback (most recent call last):\n"
                  "  File \"")

        if PY3:
            suffix = ("in test_formatException9\n"
                      "    raise l\n"
                      "pyshell.utils.exception.ListOfException: 3 exception(s)"
                      " in list\n"+ENDC)
        else:
            suffix = ("in test_formatException9\n"
                      "    raise l\n"
                      "ListOfException: 3 exception(s) in list\n"
                      ""+ENDC)

        try:
            raise l
        except Exception as ex:
            formated = formatException(ex, "plap")
            assert formated.startswith(prefix)
            assert formated.endswith(suffix)
            assert "printing_test.py" in formated

    def test_formatException10(self):  # exception with suffix
        formated = formatException(Exception("toto"),
                                   prefix="plop: ",
                                   suffix=" (burg)")
        assert formated == LIGHTRED+"plop: toto (burg)"+ENDC

    def test_formatException11(self):  # DefaultPyshellException with suffix
        formated = formatException(DefaultPyshellException("toto"),
                                   prefix="plop: ",
                                   suffix=" (burg)")
        assert formated == LIGHTRED+"plop: toto (burg)"+ENDC

    def test_formatException12(self):  # ListOfException with suffix
        l = ListOfException()
        l.addException(Exception("plop"))
        l.addException(DefaultPyshellException("plip", WARNING))
        l.addException(DefaultPyshellException("toto", NOTICE))

        formated = formatException(l, prefix="plop:", suffix=" (burg)")
        expected = (LIGHTRED+"plop: (burg)"+ENDC+"\n     "+LIGHTRED+"plop" +
                    ENDC+"\n     "+LIGHTORANGE+"plip"+ENDC+"\n     " +
                    LIGHTGREEN+"toto"+ENDC)
        assert formated == expected

    def test_indentString(self):
        p = Printer.getInstance()
        assert p.indentString("plop") == "     plop"
        expected = "     plop\n     plip\n     plap\n     "
        assert p.indentString("plop\nplip\nplap\n") == expected

    def test_indentTokenList(self):
        p = Printer.getInstance()
        expected = ["     plop", "     plop\n     plip\n     plap\n     "]
        assert p.indentListOfToken(("plop", "plop\nplip\nplap\n")) == expected
