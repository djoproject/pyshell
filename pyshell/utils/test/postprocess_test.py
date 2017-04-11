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

from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.system.manager.parent import ParentManager
from pyshell.system.parameter.context import ContextParameter
from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.system.setting.context import ContextGlobalSettings
from pyshell.system.setting.environment import EnvironmentGlobalSettings
from pyshell.utils.constants import CONTEXT_COLORATION_DARK
from pyshell.utils.constants import CONTEXT_COLORATION_KEY
from pyshell.utils.constants import CONTEXT_COLORATION_LIGHT
from pyshell.utils.constants import CONTEXT_COLORATION_NONE
from pyshell.utils.constants import CONTEXT_EXECUTION_DAEMON
from pyshell.utils.constants import CONTEXT_EXECUTION_KEY
from pyshell.utils.constants import CONTEXT_EXECUTION_SHELL
from pyshell.utils.constants import DEBUG_ENVIRONMENT_NAME
from pyshell.utils.constants import ENVIRONMENT_TAB_SIZE_KEY
from pyshell.utils.postprocess import listFlatResultHandler
from pyshell.utils.postprocess import listResultHandler
from pyshell.utils.postprocess import printBytesAsString
from pyshell.utils.postprocess import printColumn
from pyshell.utils.postprocess import printColumnWithouHeader
from pyshell.utils.postprocess import printStringCharResult
from pyshell.utils.printing import Printer


class TestPostProcess(object):

    def setup_method(self, method):
        p = Printer.getInstance()
        self.params = ParentManager()

        ##

        checker = DefaultChecker.getInteger()
        self.debugContext = ContextParameter(
            value=tuple(range(0, 91)),
            settings=ContextGlobalSettings(checker=checker))
        self.params.getContextManager().setParameter(DEBUG_ENVIRONMENT_NAME,
                                                     self.debugContext,
                                                     local_param=True)
        self.debugContext.settings.setRemovable(False)
        self.debugContext.settings.tryToSetDefaultIndex(0)
        self.debugContext.settings.setReadOnly(True)
        self.debugContext.settings.tryToSetIndex(0)

        ##

        checker = DefaultChecker.getString()
        self.shellContext = ContextParameter(
            value=(CONTEXT_EXECUTION_SHELL,
                   CONTEXT_EXECUTION_DAEMON,),
            settings=ContextGlobalSettings(checker=checker))
        self.params.getContextManager().setParameter(CONTEXT_EXECUTION_KEY,
                                                     self.shellContext,
                                                     local_param=True)
        self.shellContext.settings.setRemovable(False)
        self.shellContext.settings.tryToSetDefaultIndex(0)
        self.shellContext.settings.setReadOnly(True)

        ##

        checker = DefaultChecker.getString()
        self.backgroundContext = ContextParameter(
            value=(CONTEXT_COLORATION_LIGHT,
                   CONTEXT_COLORATION_DARK,
                   CONTEXT_COLORATION_NONE,),
            settings=ContextGlobalSettings(checker=checker))
        self.params.getContextManager().setParameter(CONTEXT_COLORATION_KEY,
                                                     self.backgroundContext,
                                                     local_param=True)
        self.backgroundContext.settings.setRemovable(False)
        self.backgroundContext.settings.tryToSetDefaultIndex(0)
        self.backgroundContext.settings.setReadOnly(True)

        ##

        self.spacingContext = EnvironmentParameter(
            value=5,
            settings=EnvironmentGlobalSettings(
                checker=IntegerArgChecker(0)))
        self.params.getEnvironmentManager().setParameter(
            ENVIRONMENT_TAB_SIZE_KEY,
            self.spacingContext,
            local_param=True)
        self.spacingContext.settings.setRemovable(False)
        self.spacingContext.settings.setReadOnly(False)

        p.setParameters(self.params)

    def test_listResultHandler1(self, capsys):
        listResultHandler(())
        out, err = capsys.readouterr()
        assert out == ""

    def test_listResultHandler2(self, capsys):
        listResultHandler(("aa",))
        out, err = capsys.readouterr()
        assert out == "     aa\n"

    def test_listResultHandler3(self, capsys):
        listResultHandler(("aa", 42,))
        out, err = capsys.readouterr()
        assert out == "     aa\n     42\n"

    ###

    def test_listFlatResultHandler1(self, capsys):
        listFlatResultHandler(())
        out, err = capsys.readouterr()
        assert out == "     \n"

    def test_listFlatResultHandler2(self, capsys):
        listFlatResultHandler(("aa",))
        out, err = capsys.readouterr()
        assert out == "     aa\n"

    def test_listFlatResultHandler3(self, capsys):
        listFlatResultHandler(("aa", 42,))
        out, err = capsys.readouterr()
        assert out == "     aa 42\n"

    ###

    def test_printStringCharResult1(self, capsys):
        printStringCharResult(())
        out, err = capsys.readouterr()
        assert out == "     \n"

    def test_printStringCharResult2(self, capsys):
        printStringCharResult((60,))
        out, err = capsys.readouterr()
        assert out == "     <\n"

    def test_printStringCharResult3(self, capsys):
        printStringCharResult((60, 42,))
        out, err = capsys.readouterr()
        assert out == "     <*\n"

    ###

    def test_printBytesAsString1(self, capsys):
        printBytesAsString(())
        out, err = capsys.readouterr()
        assert out == "     \n"

    def test_printBytesAsString2(self, capsys):
        printBytesAsString((0x25,))
        out, err = capsys.readouterr()
        assert out == "     25\n"

    def test_printBytesAsString3(self, capsys):
        printBytesAsString((0x25, 0x42,))
        out, err = capsys.readouterr()
        assert out == "     2542\n"

    ###

    def test_printColumnWithouHeader1(self, capsys):
        printColumnWithouHeader(())
        out, err = capsys.readouterr()
        assert out == ""

    def test_printColumnWithouHeader2(self, capsys):
        printColumnWithouHeader(("TOTO",))
        out, err = capsys.readouterr()
        assert out == "     TOTO\n"

    def test_printColumnWithouHeader3(self, capsys):
        printColumnWithouHeader(("TOTO", "TUTUTU",))
        out, err = capsys.readouterr()
        assert out == "     TOTO\n     TUTUTU\n"

    def test_printColumnWithouHeader4(self, capsys):
        printColumnWithouHeader(("TOTO", "TUTUTU", "tata",))
        out, err = capsys.readouterr()
        assert out == "     TOTO\n     TUTUTU\n     tata\n"

    def test_printColumnWithouHeader5(self, capsys):
        printColumnWithouHeader((("TOTO", "tata"), "TUTUTU",))
        out, err = capsys.readouterr()
        assert out == "     TOTO    tata\n     TUTUTU\n"

    def test_printColumnWithouHeader6(self, capsys):
        printColumnWithouHeader((("TOTO", "tata"),
                                 "TUTUTU",
                                 ("aaaaaaaaaa", "bbbbbbbb", "cccccc",),))
        out, err = capsys.readouterr()
        assert out == ("     TOTO        tata\n     TUTUTU\n     aaaaaaaaaa"
                       "  bbbbbbbb  cccccc\n")

    ###

    def test_printColumn1(self, capsys):
        printColumn(())
        out, err = capsys.readouterr()
        assert out == ""

    def test_printColumn2(self, capsys):
        printColumn(("TOTO",))
        out, err = capsys.readouterr()
        assert out == "     TOTO\n"

    def test_printColumn3(self, capsys):
        printColumn(("TOTO", "TUTUTU",))
        out, err = capsys.readouterr()
        assert out == "     TOTO\n      TUTUTU\n"

    def test_printColumn4(self, capsys):
        printColumn(("TOTO", "TUTUTU", "tata",))
        out, err = capsys.readouterr()
        assert out == "     TOTO\n      TUTUTU\n      tata\n"

    def test_printColumn5(self, capsys):
        printColumn((("TOTO", "tata"), "TUTUTU",))
        out, err = capsys.readouterr()
        assert out == "     TOTO    tata\n      TUTUTU\n"

    def test_printColumn6(self, capsys):
        printColumn((("TOTO", "tata"),
                     "TUTUTU",
                     ("aaaaaaaaaa", "bbbbbbbb", "cccccc",),))
        out, err = capsys.readouterr()
        assert out == ("     TOTO         tata\n      TUTUTU\n      aaaaaaaaaa"
                       "   bbbbbbbb   cccccc\n")

    def test_printColumn7(self, capsys):
        printColumn((("TOTO", "tata", "plapplap"),
                     "TUTUTU",
                     ("aaaaaaaaaa", "bbbbbbbb", "cccccc",),
                     ("lalala", "lulu"),))
        out, err = capsys.readouterr()
        assert out == ("     TOTO         tata       plapplap\n      TUTUTU\n"
                       "      aaaaaaaaaa   bbbbbbbb   cccccc\n      lalala"
                       "       lulu\n")
