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

from pyshell.arg.checker.default import DefaultChecker
from pyshell.system.setting.key import KeyGlobalSettings
from pyshell.system.setting.key import KeyLocalSettings
from pyshell.system.setting.key import KeySettings
from pyshell.utils.constants import SETTING_PROPERTY_CHECKER
from pyshell.utils.constants import SETTING_PROPERTY_CHECKERLIST


class TestKeySettings(object):
    def test_initSetNoneChecker(self):
        s = KeySettings(checker=None)
        assert s.getChecker() is DefaultChecker.getKey()

    def test_initSetAChecker(self):
        s = KeySettings(checker=DefaultChecker.getString())
        assert s.getChecker() is DefaultChecker.getKey()

    def test_setListChecker(self):
        s = KeySettings()
        assert not s.isListChecker()
        s.setListChecker(True)
        assert not s.isListChecker()
        s.setListChecker(False)
        assert not s.isListChecker()

    def test_getProperties(self):
        s = KeySettings()
        props = s.getProperties()
        assert SETTING_PROPERTY_CHECKER not in props
        assert SETTING_PROPERTY_CHECKERLIST not in props

    def test_cloneWithoutSource(self):
        zs = KeySettings()
        zsc = zs.clone()
        assert isinstance(zsc, KeySettings)

        assert zs is not zsc
        assert hash(zs) == hash(zsc)

    def test_cloneWithSource(self):
        to_clone = KeySettings()
        source = KeySettings()
        to_clone.clone(source)

        assert to_clone is not source
        assert hash(to_clone) == hash(source)


class TestKeyLocalSettings(object):
    def test_constructorReadOnlyProp(self):
        s = KeyLocalSettings(read_only=True,
                             removable=False)

        assert s.isReadOnly()
        assert not s.isRemovable()

    def test_constructorRemovableProp(self):
        s = KeyLocalSettings(read_only=False,
                             removable=True)

        assert not s.isReadOnly()
        assert s.isRemovable()

    def test_cloneWithoutSource(self):
        zs = KeyLocalSettings()
        zsc = zs.clone()
        assert isinstance(zsc, KeyLocalSettings)

        assert zs is not zsc
        assert hash(zs) == hash(zsc)

    def test_cloneWithSource(self):
        to_clone = KeyLocalSettings()
        source = KeyLocalSettings()
        to_clone.clone(source)

        assert to_clone is not source
        assert hash(to_clone) == hash(source)

    def test_getGlobalFromLocal(self):
        ls = KeyLocalSettings(read_only=True,
                              removable=False)

        gs = ls.getGlobalFromLocal()

        assert type(gs) is KeyGlobalSettings
        assert gs.isReadOnly()
        assert not gs.isRemovable()
        assert gs.getChecker() is ls.getChecker()


class TestKeyGlobalSettings(object):
    def test_constructorReadOnlyProp(self):
        s = KeyGlobalSettings(read_only=True,
                              removable=False,
                              transient=False)

        assert s.isReadOnly()
        assert not s.isRemovable()
        assert not s.isTransient()

    def test_constructorRemovableProp(self):
        s = KeyGlobalSettings(read_only=False,
                              removable=True,
                              transient=False)

        assert not s.isReadOnly()
        assert s.isRemovable()
        assert not s.isTransient()

    def test_constructorTransientProp(self):
        s = KeyGlobalSettings(read_only=False,
                              removable=False,
                              transient=True)

        assert not s.isReadOnly()
        assert not s.isRemovable()
        assert s.isTransient()

    def test_cloneWithoutSource(self):
        zs = KeyGlobalSettings()
        zsc = zs.clone()
        assert isinstance(zsc, KeyGlobalSettings)

        assert zs is not zsc
        assert hash(zs) == hash(zsc)

    def test_cloneWithSource(self):
        to_clone = KeyGlobalSettings()
        source = KeyGlobalSettings()
        to_clone.clone(source)

        assert to_clone is not source
        assert hash(to_clone) == hash(source)

    def test_getLocalFromGlobal(self):
        gs = KeyGlobalSettings(read_only=True,
                               removable=False,
                               transient=True)

        ls = gs.getLocalFromGlobal()

        assert type(ls) is KeyLocalSettings
        assert ls.isReadOnly()
        assert not ls.isRemovable()
        assert ls.getChecker() is gs.getChecker()
