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

from uuid import uuid4

import pytest

from pyshell.system.parameter import Parameter
from pyshell.system.setting.parameter import ParameterGlobalSettings
from pyshell.system.setting.parameter import ParameterLocalSettings
from pyshell.utils.exception import ParameterException


class CopyableObject(object):
    def __init__(self, to_store):
        self.to_store = to_store

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other.to_store == self.to_store)

    def __hash__(self):
        return hash(self.to_store)


class TestParameter(object):
    # test value/getvalue on constructor

    def test_parameterConstructor1(self):
        with pytest.raises(ParameterException):
            Parameter(None, object())

    def test_parameterConstructor2(self):
        p = Parameter(None)
        assert isinstance(p.settings, ParameterLocalSettings)

    def test_parameterConstructor3(self):
        ls = ParameterLocalSettings()
        p = Parameter(None, settings=ls)
        assert p.settings is ls

    def test_parameterConstructor4(self):
        ls = ParameterLocalSettings()
        ls.setReadOnly(True)
        o = object()
        p = Parameter(o, settings=ls)
        assert p.getValue() is o
        with pytest.raises(ParameterException):
            p.setValue("plop")

    # test setValue/getValue
    def test_parameter1(self):
        p = Parameter(None)
        assert p.getValue() is None
        p.setValue(42)
        assert p.getValue() == 42

    # test enableLocal
    def test_parameter2(self):
        p = Parameter(None)
        sett = p.settings
        assert isinstance(sett, ParameterLocalSettings)
        p.enableLocal()
        assert sett is p.settings

    # test enableGlobal
    def test_parameter3(self):
        p = Parameter(None)
        p.enableGlobal()
        sett = p.settings
        assert isinstance(sett, ParameterGlobalSettings)
        p.enableGlobal()
        assert sett is p.settings

    # test from global to local
    def test_parameter4(self):
        p = Parameter(None)
        p.enableGlobal()
        assert isinstance(p.settings, ParameterGlobalSettings)
        p.settings.setRemovable(True)
        p.settings.setReadOnly(True)
        p.enableLocal()
        assert isinstance(p.settings, ParameterLocalSettings)
        assert p.settings.isReadOnly()
        assert p.settings.isRemovable()

    # test from global to local
    def test_parameter5(self):
        p = Parameter(None)
        p.enableGlobal()
        assert isinstance(p.settings, ParameterGlobalSettings)
        p.settings.setRemovable(False)
        p.settings.setReadOnly(False)
        p.enableLocal()
        assert isinstance(p.settings, ParameterLocalSettings)
        assert not p.settings.isReadOnly()
        assert not p.settings.isRemovable()

    # test from local to global
    def test_parameter6(self):
        p = Parameter(None)
        assert isinstance(p.settings, ParameterLocalSettings)
        p.settings.setRemovable(False)
        p.settings.setReadOnly(False)
        p.enableGlobal()
        assert isinstance(p.settings, ParameterGlobalSettings)
        assert not p.settings.isReadOnly()
        assert not p.settings.isRemovable()

    # test from local to global
    def test_parameter7(self):
        p = Parameter(None)
        assert isinstance(p.settings, ParameterLocalSettings)
        p.settings.setRemovable(True)
        p.settings.setReadOnly(True)
        p.enableGlobal()
        assert isinstance(p.settings, ParameterGlobalSettings)
        assert p.settings.isReadOnly()
        assert p.settings.isRemovable()

    # test str
    def test_parameter8(self):
        p = Parameter(42)
        assert str(p) == "42"

    # test repr
    def test_parameter9(self):
        p = Parameter(42)
        assert repr(p) == "Parameter: 42"

    # test hash
    def test_parameter10(self):
        p1 = Parameter(42)
        p2 = Parameter(42)
        assert hash(p1) == hash(p2)
        p3 = Parameter(43)
        assert hash(p1) != hash(p3)
        p4 = Parameter(42)
        p4.settings.setReadOnly(True)
        assert hash(p1) != hash(p4)

    def test_hashList(self):
        p1 = Parameter([42])
        p2 = Parameter([42])
        assert hash(p1) == hash(p2)
        p3 = Parameter([43])
        assert hash(p1) != hash(p3)
        p4 = Parameter([42])
        p4.settings.setReadOnly(True)
        assert hash(p1) != hash(p4)

    def test_cloneWithoutSource(self):
        p = Parameter(CopyableObject(uuid4()))
        p_clone = p.clone()

        assert p is not p_clone
        assert p.settings is not p_clone.settings
        assert p.getValue() is not p_clone.getValue()
        assert p.getValue() == p_clone.getValue()
        assert hash(p.settings) == hash(p_clone.settings)
        assert hash(p) == hash(p_clone)

    def test_cloneWithSource(self):
        to_clone = Parameter(CopyableObject(uuid4()))
        to_clone.settings.setReadOnly(True)
        source = Parameter(CopyableObject(uuid4()))
        source.settings.setReadOnly(False)
        to_clone.clone(source)

        assert to_clone is not source
        assert to_clone.settings is not source.settings
        assert to_clone.getValue() is not source.getValue()
        assert to_clone.getValue() == source.getValue()
        assert hash(to_clone.settings) == hash(source.settings)
        assert hash(to_clone) == hash(source)
