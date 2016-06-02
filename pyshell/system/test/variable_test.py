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
from pyshell.system.variable import VarParameter
from pyshell.system.variable import VariableGlobalSettings
from pyshell.system.variable import VariableLocalSettings
from pyshell.system.variable import VariableParameterManager
from pyshell.utils.exception import ParameterException


class Anything(object):

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class TestVariable(object):

    def setUp(self):
        pass

    # # settings # #

    def test_localSettings1(self):
        vls = VariableLocalSettings()

        assert vls.isTransient()
        vls.setTransient(True)
        assert vls.isTransient()

    def test_localSettings2(self):
        vls = VariableLocalSettings()

        assert not vls.isReadOnly()
        vls.setReadOnly(True)
        assert not vls.isReadOnly()

    def test_localSettings3(self):
        vls = VariableLocalSettings()

        assert vls.isRemovable()
        vls.setRemovable(False)
        assert vls.isRemovable()

    def test_localSettings4(self):
        vls = VariableLocalSettings()
        assert len(vls.getProperties()) == 0

    # #

    def test_globalSettings1(self):
        vls = VariableGlobalSettings()

        assert not vls.isTransient()
        vls.setTransient(True)
        assert vls.isTransient()

    def test_globalSettings2(self):
        vls = VariableGlobalSettings(transient=True)

        assert vls.isTransient()
        vls.setTransient(False)
        assert not vls.isTransient()

    def test_globalSettings3(self):
        vls = VariableGlobalSettings(transient=False)

        assert not vls.isTransient()
        vls.setTransient(True)
        assert vls.isTransient()

    def test_globalSettings4(self):
        vls = VariableGlobalSettings()

        assert not vls.isReadOnly()
        vls.setReadOnly(True)
        assert not vls.isReadOnly()

    def test_globalSettings5(self):
        vls = VariableGlobalSettings()

        assert vls.isRemovable()
        vls.setRemovable(False)
        assert vls.isRemovable()

    def test_globalSettings7(self):
        vls = VariableGlobalSettings()
        assert len(vls.getProperties()) == 0

    def test_globalSettings8(self):
        vls = VariableGlobalSettings()
        vls.setStartingPoint(hash(vls))

    def test_globalSettings11(self):
        vls = VariableGlobalSettings()
        vls.setStartingPoint(hash(self))
        assert vls.isEqualToStartingHash(hash(self))

    def test_globalSettings12(self):
        vls = VariableGlobalSettings()
        vls.setStartingPoint(hash(self))
        with pytest.raises(ParameterException):
            vls.setStartingPoint(hash(self))

    # # manager # #

    def test_manager(self):
        assert VariableParameterManager() is not None

    def test_addAValidVariable(self):
        manager = VariableParameterManager()
        manager.setParameter("test.var", VarParameter("0x1122ff"))
        assert manager.hasParameter("t.v")
        param = manager.getParameter("te.va")
        assert isinstance(param, VarParameter)
        assert hasattr(param.getValue(), "__iter__")
        assert param.getValue() == ["0x1122ff"]

    def test_addNotAllowedParameter(self):
        manager = VariableParameterManager()
        with pytest.raises(ParameterException):
            manager.setParameter("test.var", EnvironmentParameter("0x1122ff"))

    # # properties # #

    def test_noProperties(self):
        v = VarParameter("plop")
        assert len(v.settings.getProperties()) == 0

    # # parsing # #

    def test_varParsing1(self):  # string sans espace
        v = VarParameter("plop")
        assert v.getValue() == ["plop"]

    def test_varParsing2(self):  # string avec espace
        v = VarParameter("plop plip plap")
        assert v.getValue() == ["plop", "plip", "plap"]

    def test_varParsing3(self):  # anything
        v = VarParameter(Anything("toto"))
        assert v.getValue() == ["toto"]

    def test_varParsing4(self):  # list de string sans espace
        v = VarParameter(["plop", "plip", "plap"])
        assert v.getValue() == ["plop", "plip", "plap"]

    def test_varParsing5(self):  # list de string avec espace
        v = VarParameter(["pl op", "p li pi", "pla pa"])
        assert v.getValue() == ["pl", "op", "p", "li", "pi", "pla", "pa"]

    def test_varParsing6(self):  # list de anything
        v = VarParameter(
            [Anything("plop"), Anything("plip"), Anything("plap")])
        assert v.getValue() == ["plop", "plip", "plap"]

    def test_varParsing7(self):  # list de list de string sans espace
        v = VarParameter([["plop", "plipi"], ["plapa"]])
        assert v.getValue() == ["plop", "plipi", "plapa"]

    def test_varParsing8(self):  # list de list de string avec espace
        v = VarParameter([["pl op", "p li pi"], ["pla pa"]])
        assert v.getValue() == ["pl", "op", "p", "li", "pi", "pla", "pa"]

    def test_varParsing9(self):  # list de list de anything
        v = VarParameter([[Anything("pl op"), Anything("p li pi")],
                          [Anything("pla pa")]])
        assert v.getValue() == ["pl", "op", "p", "li", "pi", "pla", "pa"]

    # # __str__ __repr__ # #

    def test_varStr1(self):
        v = VarParameter("plop plip plap")
        assert str(v) == "plop plip plap"

    def test_varStr2(self):
        v = VarParameter("")
        assert str(v) == ""

    def test_varRepr1(self):
        v = VarParameter("plop plip plap")
        assert repr(v) == "Variable, value: ['plop', 'plip', 'plap']"

    def test_varRepr2(self):
        v = VarParameter("")
        assert repr(v) == "Variable (empty)"

    # # enableGlobal, enableLocal # #

    def test_enableGlobal(self):
        v = VarParameter("plop plip plap")
        assert type(v.settings) is VariableLocalSettings
        v.enableGlobal()
        assert type(v.settings) is VariableGlobalSettings
        s = v.settings
        v.enableGlobal()
        assert v.settings is s

    def test_enableLocal(self):
        v = VarParameter("plop plip plap")
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
        v = VarParameter("plop plip plap")
        v_clone = v.clone()

        assert v is not v_clone
        assert v.settings is not v_clone
        assert v.typ is v_clone.typ
        assert v.getValue() is not v_clone.getValue()
        assert v.getValue() == v_clone.getValue()
        assert hash(v.settings) == hash(v_clone.settings)
        assert hash(v) == hash(v_clone)
