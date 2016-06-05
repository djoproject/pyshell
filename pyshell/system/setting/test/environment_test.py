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

from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.arg.argchecker import ListArgChecker
from pyshell.system.setting.environment import DEFAULT_CHECKER
from pyshell.system.setting.environment import EnvironmentGlobalSettings
from pyshell.system.setting.environment import EnvironmentLocalSettings
from pyshell.system.setting.environment import EnvironmentSettings
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
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        s = EnvironmentSettings(checker=int_checker)
        assert s.getChecker() is int_checker

    def test_constructorInvalidChecker(self):
        with pytest.raises(ParameterException):
            EnvironmentSettings(checker="toto")

    def test_setCheckerReadOnlyParameter(self):
        s = ReadOnlyEnvironmentSettings(checker=None)
        assert s.getChecker() is DEFAULT_CHECKER

        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        with pytest.raises(ParameterException):
            s.setChecker(int_checker)

    def test_setCheckerNoneChecker(self):
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        s = EnvironmentSettings(checker=int_checker)
        assert s.getChecker() is int_checker

        s.setChecker(checker=None)
        assert s.getChecker() is DEFAULT_CHECKER

    def test_setCheckerConserveListStateIfEnabled(self):
        s = EnvironmentSettings(checker=None)
        assert s.getChecker() is DEFAULT_CHECKER
        assert s.isListChecker()
        sub_default_checker = DEFAULT_CHECKER.checker

        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        assert not isinstance(int_checker, ListArgChecker)

        s.setChecker(checker=int_checker)
        assert s.isListChecker()
        assert s.getChecker().checker is int_checker
        assert s.getChecker().checker is not sub_default_checker

    def test_setCheckerValidChecker(self):
        str_checker = DefaultInstanceArgChecker.getStringArgCheckerInstance()
        s = EnvironmentSettings(checker=str_checker)
        assert s.getChecker() is str_checker

        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        s.setChecker(checker=int_checker)

        assert s.getChecker() is int_checker

    def test_isListCheckerIsAListChecker(self):
        s = EnvironmentSettings(checker=None)
        assert s.getChecker() is DEFAULT_CHECKER
        assert s.isListChecker()
        assert isinstance(DEFAULT_CHECKER, ListArgChecker)

    def test_isListCheckerIsNotAListChecker(self):
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
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
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
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
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        s = EnvironmentSettings(checker=int_checker)
        assert not s.isListChecker()

        s.setListChecker(False)

        assert not s.isListChecker()
        assert s.getChecker() is int_checker

    def test_getPropertiesListChecker(self):
        s = EnvironmentSettings(checker=DEFAULT_CHECKER)
        assert s.isListChecker()

        assert s.getProperties() == (('removable', True),
                                     ('readOnly', False),
                                     ('transient', True),
                                     ('checker', 'any'),
                                     ('checkerList', True))

    def test_getPropertiesNotAListChecker(self):
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        s = EnvironmentSettings(checker=int_checker)
        assert not s.isListChecker()

        assert s.getProperties() == (('removable', True),
                                     ('readOnly', False),
                                     ('transient', True),
                                     ('checker', 'integer'),
                                     ('checkerList', False))

    def test_cloneWithoutSource(self):
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        s = EnvironmentSettings(checker=int_checker)

        sc = s.clone()

        assert isinstance(sc, EnvironmentSettings)
        sc.getChecker() is s.getChecker()

    def test_cloneWithSource(self):
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        source = EnvironmentSettings(checker=int_checker)
        source.setListChecker(True)

        str_checker = DefaultInstanceArgChecker.getStringArgCheckerInstance()
        to_clone = EnvironmentSettings(checker=str_checker)

        to_clone.clone(source)
        to_clone.getChecker() is source.getChecker()
        assert not source.isListChecker()
        assert source.getChecker() is str_checker
        assert hash(to_clone) == hash(source)

    def test_cloneWithSourceAndReadOnly(self):
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        source = ReadOnlyEnvironmentSettings(checker=int_checker)
        source.setReadOnly(False)
        source.setListChecker(True)
        source.setReadOnly(True)

        str_checker = DefaultInstanceArgChecker.getStringArgCheckerInstance()
        to_clone = EnvironmentSettings(checker=str_checker)

        to_clone.clone(source)
        to_clone.getChecker() is source.getChecker()
        assert not source.isListChecker()
        assert source.getChecker() is str_checker

        assert source.isReadOnly()
        source.setReadOnly(False)
        assert hash(to_clone) == hash(source)


class TestEnvironmentLocalSettings(object):
    def test_constructorReadOnlyProp(self):
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        s = EnvironmentLocalSettings(read_only=True,
                                     removable=False,
                                     checker=int_checker)

        assert s.isReadOnly()
        assert not s.isRemovable()
        assert s.getChecker() is int_checker

    def test_constructorRemovableProp(self):
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
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
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
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

    def test_cloneWithSource(self):
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        to_clone = EnvironmentLocalSettings(read_only=False,
                                            removable=False,
                                            checker=int_checker)

        str_checker = DefaultInstanceArgChecker.getStringArgCheckerInstance()
        source = EnvironmentLocalSettings(read_only=True,
                                          removable=True,
                                          checker=str_checker)

        assert hash(to_clone) != hash(source)
        to_clone.clone(source)
        assert hash(to_clone) == hash(source)

    def test_getGlobalFromLocal(self):
        checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
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
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        s = EnvironmentGlobalSettings(read_only=True,
                                      removable=False,
                                      transient=False,
                                      checker=int_checker)

        assert s.isReadOnly()
        assert not s.isRemovable()
        assert not s.isTransient()
        assert s.getChecker() is int_checker

    def test_constructorRemovableProp(self):
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        s = EnvironmentGlobalSettings(read_only=False,
                                      removable=True,
                                      transient=False,
                                      checker=int_checker)

        assert not s.isReadOnly()
        assert s.isRemovable()
        assert not s.isTransient()
        assert s.getChecker() is int_checker

    def test_constructorTransientProp(self):
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
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
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
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

    def test_cloneWithSource(self):
        int_checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        to_clone = EnvironmentGlobalSettings(read_only=False,
                                             removable=False,
                                             transient=False,
                                             checker=int_checker)

        str_checker = DefaultInstanceArgChecker.getStringArgCheckerInstance()
        source = EnvironmentGlobalSettings(read_only=True,
                                           removable=True,
                                           transient=True,
                                           checker=str_checker)

        assert hash(to_clone) != hash(source)
        to_clone.clone(source)
        assert hash(to_clone) == hash(source)

    def test_getLocalFromGlobal(self):
        checker = DefaultInstanceArgChecker.getIntegerArgCheckerInstance()
        gs = EnvironmentGlobalSettings(read_only=True,
                                       removable=False,
                                       transient=True,
                                       checker=checker)

        ls = gs.getLocalFromGlobal()

        assert type(ls) is EnvironmentLocalSettings
        assert ls.isReadOnly()
        assert not ls.isRemovable()
        assert gs.getChecker() is ls.getChecker()
