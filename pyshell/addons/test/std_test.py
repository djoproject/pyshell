#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2017  Jonathan Delvaux <pyshell@djoproject.net>

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

import pyshell.addons.std as monkey_std
from pyshell.addons.std import echo
from pyshell.addons.std import echo16
from pyshell.addons.std import exitFun
from pyshell.addons.std import generator
from pyshell.addons.std import helpFun
from pyshell.addons.std import historyLoad
from pyshell.addons.std import historySave
from pyshell.addons.std import intToAscii
from pyshell.addons.std import man
from pyshell.addons.std import usageFun
from pyshell.arg.checker.default import DefaultChecker
from pyshell.command.command import MultiOutput
from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.system.setting.environment import EnvironmentGlobalSettings
from pyshell.utils.exception import DefaultPyshellException


class TestStd(object):
    def test_exitFun(self):
        with pytest.raises(SystemExit):
            exitFun()

    def test_echo(self, capsys):
        echo_input = ["aa", "bb", "cc"]
        result = echo(echo_input)
        out, err = capsys.readouterr()
        assert result == echo_input
        assert out == "aa bb cc\n"

    def test_echo16(self, capsys):
        echo_input = ["aa", "23", "cc"]
        result = echo16(echo_input)
        out, err = capsys.readouterr()
        echo_input[1] = "0x17"
        assert result == echo_input
        assert out == "aa 0x17 cc\n"

    def test_intToAscii(self, capsys):
        echo_input = [888, 71, 4000]
        result = intToAscii(echo_input)
        out, err = capsys.readouterr()
        echo_input[1] = "G"
        assert result == ("888G4000",)
        assert out == "888G4000\n"


class FakeCommand(object):
    def __init__(self):
        self.help_message = "HELP"

    def usage(self):
        return "USAGE"


class TestUsage(object):
    def setup_method(self, method):
        settings = EnvironmentGlobalSettings(transient=True,
                                             read_only=True,
                                             removable=False,
                                             checker=DefaultChecker.getArg())

        self.mltries = multiLevelTries()
        self.mlparam = EnvironmentParameter(value=self.mltries,
                                            settings=settings)

        self.space = EnvironmentParameter(value=4, settings=settings.clone())

    def test_usageFunFailedToFind(self):
        mltries = multiLevelTries()
        path = ("toto",)
        with pytest.raises(DefaultPyshellException):
            usageFun(path, mltries)

    def test_usageFunAmbiguous(self):
        self.mltries.insert(("toto",), 42)
        self.mltries.insert(("tota",), 24)
        path = ("to",)
        with pytest.raises(DefaultPyshellException):
            usageFun(path, self.mlparam)

    def test_usageFunNotFound(self):
        path = ("toto",)
        with pytest.raises(DefaultPyshellException):
            usageFun(path, self.mlparam)

    def test_usageFunNoValueOnTheLastToken(self):
        self.mltries.insert(("toto", "tata",), 42)
        self.mltries.insert(("toto", "titi",), 24)
        path = ("toto",)
        with pytest.raises(DefaultPyshellException):
            usageFun(path, self.mlparam)

    def test_usageFunSuccess(self):
        path = ("toto",)
        self.mltries.insert(path, FakeCommand())
        result = usageFun(path, self.mlparam)
        assert result == "toto USAGE"

    def test_man(self):
        path = ("toto",)
        self.mltries.insert(path, FakeCommand())
        result = man(path, self.mlparam, self.space)
        assert len(result) is 9
        assert result[0] == "Command Name:"
        assert result[1] == "    toto"
        assert result[2] == ""
        assert result[3] == "Description:"
        assert result[4] == "    HELP"
        assert result[5] == ""
        assert result[6] == "Usage: "
        assert result[7] == "    toto USAGE"
        assert result[8] == ""

    def test_manWithNoneSpace(self):
        path = ("toto",)
        self.mltries.insert(path, FakeCommand())
        result = man(path, self.mlparam, None)
        assert len(result) is 9
        assert result[0] == "Command Name:"
        assert result[1] == "    toto"
        assert result[2] == ""
        assert result[3] == "Description:"
        assert result[4] == "    HELP"
        assert result[5] == ""
        assert result[6] == "Usage: "
        assert result[7] == "    toto USAGE"
        assert result[8] == ""

    def test_generatorWithMultiOutput(self):
        result = generator(start=0, stop=100, step=1, multi_output=True)
        assert result == range(0, 100, 1)
        assert isinstance(result, MultiOutput)

    def test_generatorWithoutMultiOutput(self):
        result = generator(start=0, stop=100, step=1, multi_output=False)
        assert result == range(0, 100, 1)
        assert not isinstance(result, MultiOutput)


class FakeReadline(object):
    def __init__(self):
        self.read_path = None
        self.write_path = None

    def read_history_file(self, path):  # noqa
        self.read_path = path

    def write_history_file(self, path):  # noqa
        self.write_path = path


class RaisingReadline(object):
    def __init__(self):
        self.read_path = None
        self.write_path = None

    def read_history_file(self, path):  # noqa
        self.read_path = path
        raise IOError("oops")

    def write_history_file(self, path):  # noqa
        self.write_path = path
        raise IOError("oops")


class TestHistoryLoad(object):
    def setup_method(self, method):
        self.readline = FakeReadline()

        settings = EnvironmentGlobalSettings(
            transient=True,
            read_only=False,
            removable=True,
            checker=DefaultChecker.getString())

        self.dpath = EnvironmentParameter(value="dir", settings=settings)
        self.fpath = EnvironmentParameter(value="path",
                                          settings=settings.clone())

        settings = EnvironmentGlobalSettings(
            transient=True,
            read_only=False,
            removable=True,
            checker=DefaultChecker.getBoolean())

        self.use = EnvironmentParameter(value=True, settings=settings)

    def test_useHistoryIsNone(self, monkeypatch):
        monkeypatch.setattr(monkey_std, 'readline', self.readline)
        historyLoad(use_history=None,
                    parameter_directory=self.dpath,
                    history_file=self.fpath)
        assert self.readline.read_path is None
        assert self.readline.write_path is None

    def test_parameterDirectoryIsNone(self, monkeypatch):
        monkeypatch.setattr(monkey_std, 'readline', self.readline)
        historyLoad(use_history=self.use,
                    parameter_directory=None,
                    history_file=self.fpath)
        assert self.readline.read_path is None
        assert self.readline.write_path is None

    def test_historyFileIsNone(self, monkeypatch):
        monkeypatch.setattr(monkey_std, 'readline', self.readline)
        historyLoad(use_history=self.use,
                    parameter_directory=self.dpath,
                    history_file=None)
        assert self.readline.read_path is None
        assert self.readline.write_path is None

    def test_useHistoryIsFalse(self, monkeypatch):
        monkeypatch.setattr(monkey_std, 'readline', self.readline)
        self.use.setValue(False)
        historyLoad(use_history=self.use,
                    parameter_directory=self.dpath,
                    history_file=self.fpath)
        assert self.readline.read_path is None
        assert self.readline.write_path is None

    def test_useHistoryIsTrue(self, monkeypatch):
        monkeypatch.setattr(monkey_std, 'readline', self.readline)
        historyLoad(use_history=self.use,
                    parameter_directory=self.dpath,
                    history_file=self.fpath)
        assert self.readline.read_path == "dir/path"
        assert self.readline.write_path is None

    def test_raise(self, monkeypatch):
        readline = RaisingReadline()
        monkeypatch.setattr(monkey_std, 'readline', readline)
        historyLoad(use_history=self.use,
                    parameter_directory=self.dpath,
                    history_file=self.fpath)
        assert readline.read_path == "dir/path"
        assert readline.write_path is None


class TestHistorySave(object):
    def setup_method(self, method):
        self.readline = FakeReadline()

        settings = EnvironmentGlobalSettings(
            transient=True,
            read_only=False,
            removable=True,
            checker=DefaultChecker.getString())

        self.dpath = EnvironmentParameter(value="dir", settings=settings)
        self.fpath = EnvironmentParameter(value="path",
                                          settings=settings.clone())

        settings = EnvironmentGlobalSettings(
            transient=True,
            read_only=False,
            removable=True,
            checker=DefaultChecker.getBoolean())

        self.use = EnvironmentParameter(value=True, settings=settings)

    def test_useHistoryIsNone(self, monkeypatch):
        monkeypatch.setattr(monkey_std, 'readline', self.readline)
        historySave(use_history=None,
                    parameter_directory=self.dpath,
                    history_file=self.fpath)
        assert self.readline.read_path is None
        assert self.readline.write_path is None

    def test_parameterDirectoryIsNone(self, monkeypatch):
        monkeypatch.setattr(monkey_std, 'readline', self.readline)
        historySave(use_history=self.use,
                    parameter_directory=None,
                    history_file=self.fpath)
        assert self.readline.read_path is None
        assert self.readline.write_path is None

    def test_historyFileIsNone(self, monkeypatch):
        monkeypatch.setattr(monkey_std, 'readline', self.readline)
        historySave(use_history=self.use,
                    parameter_directory=self.dpath,
                    history_file=None)
        assert self.readline.read_path is None
        assert self.readline.write_path is None

    def test_useHistoryIsFalse(self, monkeypatch):
        monkeypatch.setattr(monkey_std, 'readline', self.readline)
        self.use.setValue(False)
        historySave(use_history=self.use,
                    parameter_directory=self.dpath,
                    history_file=self.fpath)
        assert self.readline.read_path is None
        assert self.readline.write_path is None

    def test_useHistoryIsTrue(self, monkeypatch):
        monkeypatch.setattr(monkey_std, 'readline', self.readline)
        historySave(use_history=self.use,
                    parameter_directory=self.dpath,
                    history_file=self.fpath)
        assert self.readline.read_path is None
        assert self.readline.write_path == "dir/path"

    def test_raise(self, monkeypatch):
        monkeypatch.setattr(monkey_std, 'readline', RaisingReadline())
        with pytest.raises(IOError):
            historySave(use_history=self.use,
                        parameter_directory=self.dpath,
                        history_file=self.fpath)


class TestHelp(object):
    def setup_method(self, method):
        settings = EnvironmentGlobalSettings(transient=True,
                                             read_only=True,
                                             removable=False,
                                             checker=DefaultChecker.getArg())

        self.mltries = multiLevelTries()
        self.mlparam = EnvironmentParameter(value=self.mltries,
                                            settings=settings)

    def test_empty(self):
        with pytest.raises(DefaultPyshellException):
            helpFun(self.mlparam, args=None)

    def test_unknownCase1(self):
        with pytest.raises(DefaultPyshellException):
            helpFun(self.mlparam, args=("toto",))

    def test_simple(self):
        path = ("toto",)
        self.mltries.insert(path, FakeCommand())
        result = helpFun(self.mlparam, args=None)
        assert len(result) == 1
        assert result[0] == "toto: HELP"

    def test_hiddenCmd(self):
        path = ("toto",)
        self.mltries.insert(path, FakeCommand())
        self.mltries.setStopTraversal(path, True)
        with pytest.raises(DefaultPyshellException):
            helpFun(self.mlparam, args=None)

    def test_commandGroupLessThan3(self):
        path = ("toto", "titi")
        self.mltries.insert(path, FakeCommand())

        path = ("toto", "tata")
        self.mltries.insert(path, FakeCommand())

        self.mltries.setStopTraversal(("toto",), True)
        result = helpFun(self.mlparam, args=None)
        assert len(result) == 1
        assert result[0] == "toto: {tata, titi}"

    def test_commandGroupMoreThan3(self):
        path = ("toto", "titi")
        self.mltries.insert(path, FakeCommand())

        path = ("toto", "tata")
        self.mltries.insert(path, FakeCommand())

        path = ("toto", "tutu")
        self.mltries.insert(path, FakeCommand())

        path = ("toto", "tyty")
        self.mltries.insert(path, FakeCommand())

        path = ("toto",)
        self.mltries.insert(path, FakeCommand())

        self.mltries.setStopTraversal(("toto",), True)
        result = helpFun(self.mlparam, args=None)
        assert len(result) == 1
        assert result[0] == "toto: {tata, titi, tutu, ...}"

    def test_ambiguityPrefix(self):
        path = ("toto",)
        self.mltries.insert(path, FakeCommand())

        path = ("totu",)
        self.mltries.insert(path, FakeCommand())

        path = ("tutu",)
        self.mltries.insert(path, FakeCommand())

        result = helpFun(self.mlparam, args=("to",))
        assert len(result) == 2
        assert result[0] == "toto: HELP"
        assert result[1] == "totu: HELP"

    def test_ambiguityPrefixCase2(self):
        path = ("toto", "tutu",)
        self.mltries.insert(path, FakeCommand())

        path = ("totu", "tutu",)
        self.mltries.insert(path, FakeCommand())

        with pytest.raises(DefaultPyshellException):
            helpFun(self.mlparam, args=("to", "tutu"))

    def test_strangePath(self):
        path = ("toto", "tutu",)
        self.mltries.insert(path, FakeCommand())

        path = ("toto",)
        self.mltries.insert(path, FakeCommand())

        result = helpFun(self.mlparam, args=None)
        assert len(result) == 2
        assert result[0] == "toto tutu: HELP"
        assert result[1] == "toto: HELP"

    def test_strangePathCase2(self):
        path = ("toto", "tutu",)
        self.mltries.insert(path, FakeCommand())

        path = ("toto",)
        self.mltries.insert(path, FakeCommand())

        result = helpFun(self.mlparam, args=("to",))
        assert len(result) == 2
        assert result[0] == "toto tutu: HELP"
        assert result[1] == "toto: HELP"
