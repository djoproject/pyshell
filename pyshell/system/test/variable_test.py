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

from pyshell.system.environment import EnvironmentParameter
from pyshell.system.setting.variable import VariableGlobalSettings
from pyshell.system.setting.variable import VariableLocalSettings
from pyshell.system.variable import VariableParameter
from pyshell.system.variable import VariableParameterManager
from pyshell.utils.exception import ParameterException


class Anything(object):

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class TestVariable(object):
    # # manager # #

    def test_manager(self):
        assert VariableParameterManager() is not None

    def test_addAValidVariable(self):
        manager = VariableParameterManager()
        manager.setParameter("test.var", VariableParameter("0x1122ff"))
        assert manager.hasParameter("t.v")
        param = manager.getParameter("te.va")
        assert isinstance(param,  VariableParameter)
        assert hasattr(param.getValue(), "__iter__")
        assert param.getValue() == ["0x1122ff"]

    def test_addNotAllowedParameter(self):
        manager = VariableParameterManager()
        with pytest.raises(ParameterException):
            manager.setParameter("test.var", EnvironmentParameter("0x1122ff"))

    # # properties # #

    def test_noProperties(self):
        v = VariableParameter("plop")
        assert len(v.settings.getProperties()) == 0

    # # parsing # #

    def test_varParsing1(self):  # string sans espace
        v = VariableParameter("plop")
        assert v.getValue() == ["plop"]

    def test_varParsing2(self):  # string avec espace
        v = VariableParameter("plop plip plap")
        assert v.getValue() == ["plop plip plap"]

    def test_varParsing3(self):  # anything
        v = VariableParameter(Anything("toto"))
        assert v.getValue() == ["toto"]

    def test_varParsing4(self):  # list de string sans espace
        v = VariableParameter(["plop", "plip", "plap"])
        assert v.getValue() == ["plop", "plip", "plap"]

    def test_varParsing5(self):  # list de string avec espace
        v = VariableParameter(["pl op", "p li pi", "pla pa"])
        assert v.getValue() == ["pl op", "p li pi", "pla pa"]

    def test_varParsing6(self):  # list de anything
        v = VariableParameter(
            [Anything("plop"), Anything("plip"), Anything("plap")])
        assert v.getValue() == ["plop", "plip", "plap"]

    def test_varParsing7(self):  # list de list de string sans espace
        v = VariableParameter([["plop", "plipi"], ["plapa"]])
        assert v.getValue() == ["plop", "plipi", "plapa"]

    def test_varParsing8(self):  # list de list de string avec espace
        v = VariableParameter([["pl op", "p li pi"], ["pla pa"]])
        assert v.getValue() == ["pl op", "p li pi", "pla pa"]

    def test_varParsing9(self):  # list de list de anything
        v = VariableParameter([[Anything("pl op"), Anything("p li pi")],
                               [Anything("pla pa")]])
        assert v.getValue() == ["pl op", "p li pi", "pla pa"]

    # # __str__ __repr__ # #

    def test_varStr1(self):
        v = VariableParameter("plop plip plap")
        assert str(v) == "plop plip plap"

    def test_varStr2(self):
        v = VariableParameter("")
        assert str(v) == ""

    def test_varStr3(self):
        v = VariableParameter(())
        assert str(v) == ""

    def test_varRepr1(self):
        v = VariableParameter("plop plip plap")
        assert repr(v) == "Variable, value: ['plop plip plap']"

    def test_varRepr2(self):
        v = VariableParameter("")
        assert repr(v) == "Variable, value: ['']"

    def test_varRepr3(self):
        v = VariableParameter(())
        assert repr(v) == "Variable (empty)"

    # # enableGlobal, enableLocal # #

    def test_enableGlobal(self):
        v = VariableParameter("plop plip plap")
        assert type(v.settings) is VariableLocalSettings
        v.enableGlobal()
        assert type(v.settings) is VariableGlobalSettings
        s = v.settings
        v.enableGlobal()
        assert v.settings is s

    def test_enableLocal(self):
        v = VariableParameter("plop plip plap")
        assert type(v.settings) is VariableLocalSettings
        s = v.settings
        v.enableGlobal()
        assert type(v.settings) is VariableGlobalSettings
        v.enableLocal()
        assert type(v.settings) is VariableLocalSettings
        assert v.settings is not s
        s = v.settings
        v.enableLocal()
        assert v.settings is s

    def test_clone(self):
        v = VariableParameter("plop plip plap")
        v_clone = v.clone()

        assert v is not v_clone
        assert v.settings is not v_clone
        assert v.settings.getChecker() is v_clone.settings.getChecker()
        assert v.getValue() is not v_clone.getValue()
        assert v.getValue() == v_clone.getValue()
        assert hash(v.settings) == hash(v_clone.settings)
        assert hash(v) == hash(v_clone)
