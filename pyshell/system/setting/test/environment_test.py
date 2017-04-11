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
from pyshell.arg.checker.list import ListArgChecker
from pyshell.system.setting.environment import DEFAULT_CHECKER
from pyshell.system.setting.environment import EnvironmentGlobalSettings
from pyshell.system.setting.environment import EnvironmentLocalSettings
from pyshell.system.setting.environment import EnvironmentSettings
from pyshell.utils.constants import SETTING_PROPERTY_CHECKER
from pyshell.utils.constants import SETTING_PROPERTY_CHECKERLIST
from pyshell.utils.exception import ParameterException


class ReadOnlyEnvironmentSettings(EnvironmentSettings):
    def __init__(self, checker):
        self.readonly = True
        EnvironmentSettings.__init__(self, checker=checker)

    def setReadOnly(self, state):
        self.readonly = state

    def isReadOnly(self):
        return self.readonly


class TestEnvironmentSettings(object):
    def test_constructorNoneChecker(self):
        s = EnvironmentSettings(checker=None)
        assert s.getChecker() is DEFAULT_CHECKER

    def test_constructorNotNoneChecker(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentSettings(checker=int_checker)
        assert s.getChecker() is int_checker

    def test_constructorInvalidChecker(self):
        with pytest.raises(ParameterException):
            EnvironmentSettings(checker="toto")

    def test_setCheckerReadOnlyParameter(self):
        s = ReadOnlyEnvironmentSettings(checker=None)
        assert s.getChecker() is DEFAULT_CHECKER

        int_checker = DefaultChecker.getInteger()
        with pytest.raises(ParameterException):
            s.setChecker(int_checker)

    def test_setCheckerNoneChecker(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentSettings(checker=int_checker)
        assert s.getChecker() is int_checker

        s.setChecker(checker=None)
        assert s.getChecker() is DEFAULT_CHECKER

    def test_setCheckerConserveListStateIfEnabled(self):
        s = EnvironmentSettings(checker=None)
        assert s.getChecker() is DEFAULT_CHECKER
        assert s.isListChecker()
        sub_default_checker = DEFAULT_CHECKER.checker

        int_checker = DefaultChecker.getInteger()
        assert not isinstance(int_checker, ListArgChecker)

        s.setChecker(checker=int_checker)
        assert s.isListChecker()
        assert s.getChecker().checker is int_checker
        assert s.getChecker().checker is not sub_default_checker

    def test_setCheckerValidChecker(self):
        str_checker = DefaultChecker.getString()
        s = EnvironmentSettings(checker=str_checker)
        assert s.getChecker() is str_checker

        int_checker = DefaultChecker.getInteger()
        s.setChecker(checker=int_checker)

        assert s.getChecker() is int_checker

    def test_isListCheckerIsAListChecker(self):
        s = EnvironmentSettings(checker=None)
        assert s.getChecker() is DEFAULT_CHECKER
        assert s.isListChecker()
        assert isinstance(DEFAULT_CHECKER, ListArgChecker)

    def test_isListCheckerIsNotAListChecker(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentSettings(checker=int_checker)
        assert s.getChecker() is int_checker
        assert not s.isListChecker()
        assert not isinstance(int_checker, ListArgChecker)

    def test_setListCheckerReadOnlyParameter(self):
        s = ReadOnlyEnvironmentSettings(checker=None)
        with pytest.raises(ParameterException):
            s.setListChecker(True)

    def test_setListCheckerEnableListAndIsList(self):
        s = EnvironmentSettings(checker=DEFAULT_CHECKER)
        assert s.isListChecker()

        s.setListChecker(True)

        assert s.isListChecker()
        assert s.getChecker() is DEFAULT_CHECKER

    def test_setListCheckerEnableListAndIsNotAList(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentSettings(checker=int_checker)
        assert not s.isListChecker()

        s.setListChecker(True)

        assert s.isListChecker()
        assert s.getChecker().checker is int_checker

    def test_setListCheckerDisableListAndIsAList(self):
        s = EnvironmentSettings(checker=DEFAULT_CHECKER)
        assert s.isListChecker()

        s.setListChecker(False)

        assert not s.isListChecker()
        assert s.getChecker() is DEFAULT_CHECKER.checker

    def test_setListCheckerDisableListAndNotAList(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentSettings(checker=int_checker)
        assert not s.isListChecker()

        s.setListChecker(False)

        assert not s.isListChecker()
        assert s.getChecker() is int_checker

    def test_getPropertiesListChecker(self):
        s = EnvironmentSettings(checker=DEFAULT_CHECKER)
        assert s.isListChecker()

        assert s.getProperties() == {SETTING_PROPERTY_CHECKER: 'any',
                                     SETTING_PROPERTY_CHECKERLIST: True}

    def test_getPropertiesNotAListChecker(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentSettings(checker=int_checker)
        assert not s.isListChecker()

        assert s.getProperties() == {SETTING_PROPERTY_CHECKER: 'integer',
                                     SETTING_PROPERTY_CHECKERLIST: False}

    def test_cloneWithoutSource(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentSettings(checker=int_checker)

        sc = s.clone()

        assert isinstance(sc, EnvironmentSettings)
        sc.getChecker() is s.getChecker()


class TestEnvironmentLocalSettings(object):
    def test_constructorReadOnlyProp(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentLocalSettings(read_only=True,
                                     removable=False,
                                     checker=int_checker)

        assert s.isReadOnly()
        assert not s.isRemovable()
        assert s.getChecker() is int_checker

    def test_constructorRemovableProp(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentLocalSettings(read_only=False,
                                     removable=True,
                                     checker=int_checker)

        assert not s.isReadOnly()
        assert s.isRemovable()
        assert s.getChecker() is int_checker

    def test_constructorNoneChecker(self):
        s = EnvironmentLocalSettings(checker=None)
        assert s.getChecker() is DEFAULT_CHECKER

    def test_constructorNotNoneChecker(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentLocalSettings(checker=int_checker)
        assert s.getChecker() is int_checker

    def test_constructorInvalidChecker(self):
        with pytest.raises(ParameterException):
            EnvironmentLocalSettings(checker="toto")

    def test_cloneWithoutSource(self):
        s = EnvironmentLocalSettings()
        sc = s.clone()

        assert isinstance(sc, EnvironmentLocalSettings)
        assert s is not sc
        assert hash(s) == hash(sc)

    def test_getGlobalFromLocal(self):
        checker = DefaultChecker.getInteger()
        ls = EnvironmentLocalSettings(read_only=True,
                                      removable=False,
                                      checker=checker)

        assert ls.getChecker() is checker

        gs = ls.getGlobalFromLocal()

        assert type(gs) is EnvironmentGlobalSettings
        assert gs.isReadOnly()
        assert not gs.isRemovable()
        assert gs.getChecker() is ls.getChecker()


class TestEnvironmentGlobalSettings(object):
    def test_constructorReadOnlyProp(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentGlobalSettings(read_only=True,
                                      removable=False,
                                      transient=False,
                                      checker=int_checker)

        assert s.isReadOnly()
        assert not s.isRemovable()
        assert not s.isTransient()
        assert s.getChecker() is int_checker

    def test_constructorRemovableProp(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentGlobalSettings(read_only=False,
                                      removable=True,
                                      transient=False,
                                      checker=int_checker)

        assert not s.isReadOnly()
        assert s.isRemovable()
        assert not s.isTransient()
        assert s.getChecker() is int_checker

    def test_constructorTransientProp(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentGlobalSettings(read_only=False,
                                      removable=False,
                                      transient=True,
                                      checker=int_checker)

        assert not s.isReadOnly()
        assert not s.isRemovable()
        assert s.isTransient()
        assert s.getChecker() is int_checker

    def test_constructorNoneChecker(self):
        s = EnvironmentGlobalSettings(checker=None)
        assert s.getChecker() is DEFAULT_CHECKER

    def test_constructorNotNoneChecker(self):
        int_checker = DefaultChecker.getInteger()
        s = EnvironmentGlobalSettings(checker=int_checker)
        assert s.getChecker() is int_checker

    def test_constructorInvalidChecker(self):
        with pytest.raises(ParameterException):
            EnvironmentGlobalSettings(checker="toto")

    def test_cloneWithoutSource(self):
        s = EnvironmentGlobalSettings()
        sc = s.clone()

        assert isinstance(sc, EnvironmentGlobalSettings)
        assert s is not sc
        assert hash(s) == hash(sc)

    def test_getLocalFromGlobal(self):
        checker = DefaultChecker.getInteger()
        gs = EnvironmentGlobalSettings(read_only=True,
                                       removable=False,
                                       transient=True,
                                       checker=checker)

        ls = gs.getLocalFromGlobal()

        assert type(ls) is EnvironmentLocalSettings
        assert ls.isReadOnly()
        assert not ls.isRemovable()
        assert gs.getChecker() is ls.getChecker()
