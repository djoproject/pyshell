#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2016  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.arg.checker.default import DefaultChecker
from pyshell.system.setting.environment import DEFAULT_CHECKER
from pyshell.system.setting.variable import VariableGlobalSettings
from pyshell.system.setting.variable import VariableLocalSettings
from pyshell.system.setting.variable import VariableSettings
from pyshell.utils.exception import ParameterException


class TestVariableSettings(object):
    def test_checkEmptyProperties(self):
        s = VariableSettings()
        p = s.getProperties()

        assert p is not None
        assert type(p) is dict
        assert len(p) == 0

    def test_alwaysReturnsDefaultChecker(self):
        s = VariableSettings()
        assert s.getChecker() is DEFAULT_CHECKER
        with pytest.raises(ParameterException):
            s.setChecker(DefaultChecker.getString())
        assert s.getChecker() is DEFAULT_CHECKER

    def test_alwaysAListChecker(self):
        s = VariableSettings()
        assert s.isListChecker()
        with pytest.raises(ParameterException):
            s.setListChecker(False)
        assert s.isListChecker()

    def test_cloneWithoutSource(self):
        s = VariableSettings()
        sc = s.clone()

        assert isinstance(sc, VariableSettings)
        assert s is not sc
        assert hash(s) == hash(sc)


class TestVariableLocalSettings(object):
    def test_localSettings1(self):
        vls = VariableLocalSettings()

        assert vls.isTransient()
        with pytest.raises(ParameterException):
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

    def test_cloneWithoutSource(self):
        s = VariableLocalSettings()
        sc = s.clone()

        assert isinstance(sc, VariableLocalSettings)
        assert s is not sc
        assert hash(s) == hash(sc)

    def test_getGlobalFromLocal(self):
        ls = VariableLocalSettings()

        gs = ls.getGlobalFromLocal()

        assert type(gs) is VariableGlobalSettings


class TestVariableGlobalSettings(object):

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

    def test_cloneWithoutSource(self):
        s = VariableGlobalSettings()
        s.setTransient(True)
        sc = s.clone()

        assert isinstance(sc, VariableGlobalSettings)
        assert s is not sc
        assert hash(s) == hash(sc)
        assert sc.isTransient()

    def test_getLocalFromGlobal(self):
        gs = VariableGlobalSettings()

        ls = gs.getLocalFromGlobal()

        assert type(ls) is VariableLocalSettings
