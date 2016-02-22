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

import pytest

from tries import multiLevelTries

from pyshell.arg.argchecker import ArgChecker
from pyshell.arg.argchecker import BooleanValueArgChecker
from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.arg.argchecker import ListArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.command.command import MultiCommand
from pyshell.command.command import UniCommand
from pyshell.system.variable import VarParameter
from pyshell.system.variable import VariableParameterManager
from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.parsing import Parser
from pyshell.utils.solving import Solver
from pyshell.utils.solving import _addValueToIndex
from pyshell.utils.solving import _isValidBooleanValueForChecker
from pyshell.utils.solving import _removeEveryIndexUnder


@shellMethod(
    param=ListArgChecker(DefaultInstanceArgChecker.getArgCheckerInstance()))
def plopMeth(param):
    pass


class TestSolving(object):

    def setup_method(self, method):
        self.mltries = multiLevelTries()

        m = UniCommand(plopMeth)
        self.mltries.insert(("plop",), m)

        self.var = VariableParameterManager()

    # ## INIT ## #

    def test_initSolving1(self):
        s = Solver()
        with pytest.raises(DefaultPyshellException):
            s.solve("plop", self.mltries, self.var)

    def test_initSolving2(self):
        p = Parser("plop")
        s = Solver()
        with pytest.raises(DefaultPyshellException):
            s.solve(p, self.mltries, self.var)

    def test_initSolving3(self):
        p = Parser("plop")
        p.parse()
        s = Solver()
        with pytest.raises(DefaultPyshellException):
            s.solve(p, "toto", self.var)

    def test_initSolving4(self):
        p = Parser("plop")
        p.parse()
        s = Solver()
        with pytest.raises(DefaultPyshellException):
            s.solve(p, self.mltries, "plap")

    # ## VAR SOLVING ## #

    # existing var (size 0)
    def test_var1(self):
        p = Parser("plop $plop")
        p.parse()
        s = Solver()

        self.var.setParameter("plop", VarParameter(()))

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plop",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plop",)).getValue()

        assert len(argList) == 1
        assert len(argList[0]) == 0

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 0
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

    # existing var (size 0) with parameter, and so update of the parameter
    # spotted index
    def test_var2(self):
        p = Parser("plop $plop -param aa bb cc")
        p.parse()
        s = Solver()

        self.var.setParameter("plop", VarParameter(()))

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plop",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plop",)).getValue()

        assert len(argList) == 1
        assert len(argList[0]) == 0

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 1
        assert mappedArgsList[0][0]["param"] == ("aa", "bb", "cc",)

        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

    # existing var (size 1)
    def test_var3(self):
        p = Parser("plop $plop")
        p.parse()
        s = Solver()

        self.var.setParameter("plop", VarParameter(("uhuh",)))

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plop",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plop",)).getValue()

        assert len(argList) == 1
        assert len(argList[0]) == 1
        assert argList[0] == ["uhuh"]

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 0
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

    # existing var (size bigger than 1)
    def test_var4(self):
        p = Parser("plop $plop")
        p.parse()
        s = Solver()

        self.var.setParameter("plop", VarParameter(("uhuh", "ihih", "ohoho",)))

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plop",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plop",)).getValue()

        assert len(argList) == 1
        assert len(argList[0]) == 3
        assert argList[0] == ["uhuh", "ihih", "ohoho"]

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 0
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

    # existing var (size bigger than 1) with parameter spotted or not
    # (check the index)
    def test_var5(self):
        p = Parser("plop $plop -param aa bb cc")
        p.parse()
        s = Solver()

        self.var.setParameter("plop", VarParameter(("uhuh", "ihih", "ohoho",)))

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plop",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plop",)).getValue()

        assert len(argList) == 1
        assert len(argList[0]) == 3
        assert argList[0] == ["uhuh", "ihih", "ohoho"]

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 1
        assert mappedArgsList[0][0]["param"] == ("aa", "bb", "cc",)

        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

    # not existing var
    def test_var6(self):
        p = Parser("plop $plop")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plop",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plop",)).getValue()

        assert len(argList) == 1
        assert len(argList[0]) == 0

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 0
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

    # existing var (size 1) #var resolution with prefix name (no need to
    # check every case of tries case, it is tested in parameter unitest)
    def test_var7(self):
        p = Parser("plop $pl")
        p.parse()
        s = Solver()

        self.var.setParameter("plop", VarParameter(("uhuh",)))

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plop",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plop",)).getValue()

        assert len(argList) == 1
        assert len(argList[0]) == 1
        assert argList[0] == ["uhuh"]

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 0
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

    # ## SOLVING COMMAND ## #

    def test_solving1(self):  # ambiguous command
        m = UniCommand(plopMeth)
        self.mltries.insert(("plap",), m)

        p = Parser("pl")
        p.parse()
        s = Solver()

        with pytest.raises(DefaultPyshellException):
            s.solve(p, self.mltries, self.var)

    # all token used and no command found
    def test_solving2(self):
        m = UniCommand(plopMeth)
        self.mltries.insert(("plap", "plup", "plip",), m)

        p = Parser("plap plup")
        p.parse()
        s = Solver()

        with pytest.raises(DefaultPyshellException):
            s.solve(p, self.mltries, self.var)

    # no token found at all
    def test_solving3(self):
        p = Parser("titi")
        p.parse()
        s = Solver()

        with pytest.raises(DefaultPyshellException):
            s.solve(p, self.mltries, self.var)

    # at least first token found
    def test_solving4(self):
        m = UniCommand(plopMeth)
        self.mltries.insert(("plap", "plup", "plip",), m)

        p = Parser("plap toto")
        p.parse()
        s = Solver()

        with pytest.raises(DefaultPyshellException):
            s.solve(p, self.mltries, self.var)

    # command found without arg
    def test_solving5(self):
        s = Solver()
        p = Parser("plop")
        p.parse()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plop",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plop",)).getValue()

        assert len(argList) == 1
        assert len(argList[0]) == 0

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 0
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

    # command found with arg
    def test_solving6(self):
        s = Solver()
        p = Parser("plop aaa bbb ccc ddd")
        p.parse()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plop",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plop",)).getValue()

        assert len(argList) == 1
        assert len(argList[0]) == 4
        assert argList[0] == ["aaa", "bbb", "ccc", "ddd"]

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 0
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

    # ## SOLVING DASHED PARAM ## #

    # no param
    def test_solvingParams1(self):
        p = Parser("plop")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plop",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plop",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 0
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

    # no command in command
    def test_solvingParams2(self):
        self.mltries.insert(("tata",), MultiCommand())

        p = Parser("tata")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("tata",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("tata",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 0
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

    # checker on pre OR pro OR post
    def test_solvingParams3a(self):
        m = UniCommand(pre_process=plopMeth)
        self.mltries.insert(("plapA",), m)

        p = Parser("plapA -param aa bb cc")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plapA",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plapA",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 1
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "param" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["param"] == ("aa", "bb", "cc",)

    # checker on pre OR pro OR post
    def test_solvingParams3b(self):
        m = UniCommand(process=plopMeth)
        self.mltries.insert(("plapB",), m)

        p = Parser("plapB -param aa bb cc")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plapB",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plapB",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 0
        assert len(mappedArgsList[0][1]) == 1
        assert len(mappedArgsList[0][2]) == 0

        assert "param" in mappedArgsList[0][1]
        assert mappedArgsList[0][1]["param"] == ("aa", "bb", "cc",)

    # checker on pre OR pro OR post
    def test_solvingParams3c(self):
        m = UniCommand(post_process=plopMeth)
        self.mltries.insert(("plapC",), m)

        p = Parser("plapC -param aa bb cc")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plapC",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plapC",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 0
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 1

        assert "param" in mappedArgsList[0][2]
        assert mappedArgsList[0][2]["param"] == ("aa", "bb", "cc",)

    # valid param but not in the existing param of the command
    def test_solvingParams4(self):
        p = Parser("plop -toto 1 2 3")
        p.parse()

        assert p == [(('plop', '-toto', '1', '2', '3',), (), (1,),)]

        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("plop",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("plop",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 0
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert len(argList) == 1
        assert len(argList[0]) == 4
        assert argList[0] == ["-toto", "1", "2", "3"]

    # stop to collect token for a param because a second valid one has
    # been identified #and we have more token available than the limit
    # of the current param
    def test_solvingParams5(self):
        @shellMethod(
            param1=ListArgChecker(
                DefaultInstanceArgChecker.getArgCheckerInstance(),
                maximum_size=3),
            param2=ListArgChecker(
                DefaultInstanceArgChecker.getArgCheckerInstance()))
        def tutu(param1, param2):
            pass

        m = UniCommand(tutu)
        self.mltries.insert(("tutu",), m)

        p = Parser("tutu -param1 1 2 3 4 5 6 -param2 aa bb cc")
        p.parse()
        s = Solver()
        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("tutu",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("tutu",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 2
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "param1" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["param1"] == ("1", "2", "3",)

        assert "param2" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["param2"] == ("aa", "bb", "cc",)

        assert len(argList) == 1
        assert len(argList[0]) == 3
        assert argList[0] == ["4", "5", "6"]

    # stop to collect token for a param because a second valid one has been
    # identified #and we have exactly enought token available than the limit
    # of the current param
    def test_solvingParams6(self):
        @shellMethod(
            param1=ListArgChecker(
                DefaultInstanceArgChecker.getArgCheckerInstance(),
                maximum_size=3),
            param2=ListArgChecker(
                DefaultInstanceArgChecker.getArgCheckerInstance()))
        def tutu(param1, param2):
            pass

        m = UniCommand(tutu)
        self.mltries.insert(("tutu",), m)

        p = Parser("tutu -param1 1 2 3 -param2 aa bb cc")
        p.parse()
        s = Solver()
        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("tutu",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("tutu",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 2
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "param1" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["param1"] == ("1", "2", "3",)

        assert "param2" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["param2"] == ("aa", "bb", "cc",)

        assert len(argList) == 1
        assert len(argList[0]) == 0

    # stop to collect token for a param because a second valid one has been
    # identified #and we have less token available than the limit of
    # the current param
    def test_solvingParams7(self):
        @shellMethod(
            param1=ListArgChecker(
                DefaultInstanceArgChecker.getArgCheckerInstance(),
                maximum_size=3),
            param2=ListArgChecker(
                DefaultInstanceArgChecker.getArgCheckerInstance()))
        def tutu(param1, param2):
            pass

        m = UniCommand(tutu)
        self.mltries.insert(("tutu",), m)

        p = Parser("tutu -param1 1 -param2 aa bb cc")
        p.parse()
        s = Solver()
        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("tutu",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("tutu",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 2
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "param1" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["param1"] == ("1",)

        assert "param2" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["param2"] == ("aa", "bb", "cc",)

        assert len(argList) == 1
        assert len(argList[0]) == 0

    # stop to collect token for a param because we reach the end of the
    # available tokens #and we have more token available than the limit
    # of the current param
    def test_solvingParams8(self):
        @shellMethod(
            param1=ListArgChecker(
                DefaultInstanceArgChecker.getArgCheckerInstance(),
                maximum_size=3))
        def tutu(param1):
            pass

        m = UniCommand(tutu)
        self.mltries.insert(("tutu",), m)

        p = Parser("tutu -param1 1 2 3 4 5 6")
        p.parse()
        s = Solver()
        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("tutu",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("tutu",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 1
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "param1" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["param1"] == ("1", "2", "3",)

        assert len(argList[0]) == 3
        assert argList[0] == ["4", "5", "6"]

    # stop to collect token for a param because we reach the end of the
    # available tokens #and we have exactly enought token available than
    # the limit of the current param
    def test_solvingParams9(self):
        @shellMethod(
            param1=ListArgChecker(
                DefaultInstanceArgChecker.getArgCheckerInstance(),
                maximum_size=3))
        def tutu(param1):
            pass

        m = UniCommand(tutu)
        self.mltries.insert(("tutu",), m)

        p = Parser("tutu -param1 1 2 3")
        p.parse()
        s = Solver()
        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("tutu",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("tutu",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 1
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "param1" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["param1"] == ("1", "2", "3",)

        assert len(argList[0]) == 0

    # stop to collect token for a param because we reach the end of the
    # available tokens #and we have less token available than the limit of
    # the current param
    def test_solvingParams10(self):
        @shellMethod(
            param1=ListArgChecker(
                DefaultInstanceArgChecker.getArgCheckerInstance(),
                maximum_size=3))
        def tutu(param1):
            pass

        m = UniCommand(tutu)
        self.mltries.insert(("tutu",), m)

        p = Parser("tutu -param1 1 2")
        p.parse()
        s = Solver()
        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("tutu",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("tutu",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 1
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "param1" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["param1"] == ("1", "2",)

        assert len(argList[0]) == 0

    # boolean without token after #because of the end of token
    def test_solvingParams11(self):
        @shellMethod(boolean=BooleanValueArgChecker(), anything=ArgChecker())
        def boo(boolean=False, anything=None):
            pass

        m = UniCommand(boo)
        self.mltries.insert(("boo",), m)

        p = Parser("boo -boolean")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("boo",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("boo",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 1
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "boolean" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["boolean"] == ("true",)

        assert len(argList[0]) == 0

    # boolean without token after #because another param start immediatelly
    # after boolean param
    def test_solvingParams12(self):
        @shellMethod(boolean=BooleanValueArgChecker(), anything=ArgChecker())
        def boo(boolean=False, anything=None):
            pass

        m = UniCommand(boo)
        self.mltries.insert(("boo",), m)

        p = Parser("boo -boolean -anything 123")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("boo",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("boo",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 2
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "boolean" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["boolean"] == ("true",)

        assert "anything" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["anything"] == ("123",)

        assert len(argList[0]) == 0

    # boolean with invalid bool token after #and no other token after the
    # invalid one #end of the token list
    def test_solvingParams13(self):
        @shellMethod(boolean=BooleanValueArgChecker(), anything=ArgChecker())
        def boo(boolean=False, anything=None):
            pass

        m = UniCommand(boo)
        self.mltries.insert(("boo",), m)

        p = Parser("boo -boolean plop")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("boo",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("boo",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 1
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "boolean" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["boolean"] == ("true",)

        assert len(argList[0]) == 1
        assert argList[0] == ["plop"]

    # boolean with invalid bool token after #and no other token after the
    # invalid one #start of new parameter
    def test_solvingParams14(self):
        @shellMethod(boolean=BooleanValueArgChecker(), anything=ArgChecker())
        def boo(boolean=False, anything=None):
            pass

        m = UniCommand(boo)
        self.mltries.insert(("boo",), m)

        p = Parser("boo -boolean plop -anything 123")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("boo",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("boo",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 2
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "boolean" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["boolean"] == ("true",)

        assert "anything" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["anything"] == ("123",)

        assert len(argList[0]) == 1
        assert argList[0] == ["plop"]

    # boolean with invalid bool token after #and other token after the invalid
    # one #end of the token list
    def test_solvingParams15(self):
        @shellMethod(boolean=BooleanValueArgChecker(), anything=ArgChecker())
        def boo(boolean=False, anything=None):
            pass

        m = UniCommand(boo)
        self.mltries.insert(("boo",), m)

        p = Parser("boo -boolean plop plip plap")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("boo",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("boo",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 1
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "boolean" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["boolean"] == ("true",)

        assert len(argList[0]) == 3
        assert argList[0] == ["plop", "plip", "plap"]

    # boolean with invalid bool token after #and other token after the invalid
    # one #start of new parameter
    def test_solvingParams16(self):
        @shellMethod(boolean=BooleanValueArgChecker(), anything=ArgChecker())
        def boo(boolean=False, anything=None):
            pass

        m = UniCommand(boo)
        self.mltries.insert(("boo",), m)

        p = Parser("boo -boolean plop plip plap -anything 123")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("boo",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("boo",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 2
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "boolean" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["boolean"] == ("true",)

        assert "anything" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["anything"] == ("123",)

        assert len(argList[0]) == 3
        assert argList[0] == ["plop", "plip", "plap"]

    # boolean with valid bool token after #and no other token after the valid
    # one #end of the token list
    def test_solvingParams17(self):
        @shellMethod(boolean=BooleanValueArgChecker(), anything=ArgChecker())
        def boo(boolean=False, anything=None):
            pass

        m = UniCommand(boo)
        self.mltries.insert(("boo",), m)

        p = Parser("boo -boolean tr")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("boo",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("boo",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 1
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "boolean" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["boolean"] == ("tr",)

        assert len(argList[0]) == 0

    # boolean with valid bool token after #and no other token after the valid
    # one #start of new parameter
    def test_solvingParams18(self):
        @shellMethod(boolean=BooleanValueArgChecker(), anything=ArgChecker())
        def boo(boolean=False, anything=None):
            pass

        m = UniCommand(boo)
        self.mltries.insert(("boo",), m)

        p = Parser("boo -boolean tr -anything 123")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("boo",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("boo",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 2
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "boolean" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["boolean"] == ("tr",)

        assert "anything" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["anything"] == ("123",)

        assert len(argList[0]) == 0

    # boolean with valid bool token after #and other token after the valid
    # one #end of the token list
    def test_solvingParams19(self):
        @shellMethod(boolean=BooleanValueArgChecker(), anything=ArgChecker())
        def boo(boolean=False, anything=None):
            pass

        m = UniCommand(boo)
        self.mltries.insert(("boo",), m)

        p = Parser("boo -boolean tr plop plip plap")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("boo",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("boo",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 1
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "boolean" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["boolean"] == ("tr",)

        assert len(argList[0]) == 3
        assert argList[0] == ["plop", "plip", "plap"]

    # boolean with valid bool token after #and other token after the valid
    # one #start of new parameter
    def test_solvingParams20(self):
        @shellMethod(boolean=BooleanValueArgChecker(), anything=ArgChecker())
        def boo(boolean=False, anything=None):
            pass

        m = UniCommand(boo)
        self.mltries.insert(("boo",), m)

        p = Parser("boo -boolean tr plop plip plap -anything 123")
        p.parse()
        s = Solver()

        solvingresult = s.solve(p, self.mltries, self.var)
        commandList, argList, mappedArgsList, commandNameList = solvingresult

        assert len(commandNameList) == 1
        assert commandNameList[0] == ("boo",)

        assert len(commandList) == 1
        assert commandList[0] == self.mltries.search(("boo",)).getValue()

        assert len(mappedArgsList) == 1
        assert len(mappedArgsList[0][0]) == 2
        assert len(mappedArgsList[0][1]) == 0
        assert len(mappedArgsList[0][2]) == 0

        assert "boolean" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["boolean"] == ("tr",)

        assert "anything" in mappedArgsList[0][0]
        assert mappedArgsList[0][0]["anything"] == ("123",)

        assert len(argList[0]) == 3
        assert argList[0] == ["plop", "plip", "plap"]

    # ## MISC CHECKS ## #

    # no index removing
    def test_removeEveryIndexUnder0(self):
        l = [4, 5, 6, 7, 8]
        l2 = l[:]
        _removeEveryIndexUnder(l, 3)
        assert l == l2

    # no index removing
    def test_removeEveryIndexUnder1(self):
        l = [4, 5, 6, 7, 8]
        l2 = l[:]
        _removeEveryIndexUnder(l, 4)
        assert l == l2

    # all index removing, exact match index
    def test_removeEveryIndexUnder2(self):
        l = [4, 7, 12, 23, 35]
        _removeEveryIndexUnder(l, 36)
        assert l == []

    # all index removing, bigger limit match
    def test_removeEveryIndexUnder3(self):
        l = [4, 7, 12, 23, 35]
        _removeEveryIndexUnder(l, 8000)
        assert l == []

    # part of index removing, exact match index
    def test_removeEveryIndexUnder4(self):
        l = [4, 7, 12, 23, 35]
        l2 = l[2:]
        _removeEveryIndexUnder(l, 12)
        assert l == l2

    # part of index removing, bigger limit match
    def test_removeEveryIndexUnder5(self):
        l = [4, 7, 12, 23, 35]
        l2 = l[2:]
        _removeEveryIndexUnder(l, 9)
        assert l == l2

    # no index updating #exact match index
    def test_addValueToIndex1(self):
        l = [4, 7, 12, 23, 35]
        l2 = [4, 7, 12, 23, 35]
        _addValueToIndex(l, 36)
        assert l == l2

    # no index updating #bigger limit match
    def test_addValueToIndex2(self):
        l = [4, 7, 12, 23, 35]
        l2 = [4, 7, 12, 23, 35]
        _addValueToIndex(l, 8000)
        assert l == l2

    # all index updating #exact match index
    def test_addValueToIndex3(self):
        l = [4, 7, 12, 23, 35]
        l2 = [5, 8, 13, 24, 36]
        _addValueToIndex(l, 4)
        assert l == l2

    # all index updating #bigger limit match
    def test_addValueToIndex4(self):
        l = [4, 7, 12, 23, 35]
        l2 = [5, 8, 13, 24, 36]
        _addValueToIndex(l, 2)
        assert l == l2

    # part of index updating #exact match index
    def test_addValueToIndex5(self):
        l = [4, 7, 12, 23, 35]
        l2 = [4, 7, 12, 24, 36]
        _addValueToIndex(l, 23)
        assert l == l2

    # part of index updating #bigger limit match
    def test_addValueToIndex6(self):
        l = [4, 7, 12, 23, 35]
        l2 = [4, 7, 12, 24, 36]
        _addValueToIndex(l, 15)
        assert l == l2

    def test_isValidBooleanValueForChecker(self):
        assert _isValidBooleanValueForChecker("t")
        assert _isValidBooleanValueForChecker("tr")
        assert _isValidBooleanValueForChecker("tRu")
        assert _isValidBooleanValueForChecker("true")
        assert _isValidBooleanValueForChecker("FALSE")
        assert _isValidBooleanValueForChecker("faLSe")
        assert _isValidBooleanValueForChecker("f")
        assert _isValidBooleanValueForChecker("false")
        assert _isValidBooleanValueForChecker("FA")

        assert not _isValidBooleanValueForChecker("plop")
        assert not _isValidBooleanValueForChecker("falo")
        assert not _isValidBooleanValueForChecker("trut")
