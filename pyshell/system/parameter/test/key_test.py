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

from pyshell.system.parameter.key import CryptographicKeyParameter
from pyshell.system.setting.key import KeyGlobalSettings
from pyshell.system.setting.key import KeyLocalSettings
from pyshell.utils.exception import ParameterException


class TestCryptographicKeyParameter(object):

    def test_initInvalidSettings(self):
        with pytest.raises(ParameterException):
            CryptographicKeyParameter("0x1122ff", settings=object())

    # test enableGlobal
    def test_environmentMethod29(self):
        e = CryptographicKeyParameter("0x1122ff")

        assert type(e.settings) is KeyLocalSettings
        e.enableGlobal()
        assert type(e.settings) is KeyGlobalSettings
        s = e.settings
        e.enableGlobal()
        assert e.settings is s

    # test enableLocal
    def test_environmentMethod30(self):
        e = CryptographicKeyParameter("0x1122ff")

        assert type(e.settings) is KeyLocalSettings
        s = e.settings
        e.enableGlobal()
        assert type(e.settings) is KeyGlobalSettings
        e.enableLocal()
        assert type(e.settings) is KeyLocalSettings
        assert e.settings is not s
        s = e.settings
        e.enableLocal()
        assert e.settings is s

    def test_environmentMethod31(self):
        e = CryptographicKeyParameter("0x1122ff",
                                      settings=KeyLocalSettings(
                                          read_only=True,
                                          removable=True))
        e.enableGlobal()
        assert type(e.settings) is KeyGlobalSettings
        assert e.settings.isReadOnly()
        assert e.settings.isRemovable()

    def test_environmentMethod32(self):
        e = CryptographicKeyParameter("0x1122ff",
                                      settings=KeyLocalSettings(
                                          read_only=False,
                                          removable=False))
        e.enableGlobal()
        assert type(e.settings) is KeyGlobalSettings
        assert not e.settings.isReadOnly()
        assert not e.settings.isRemovable()

    def test_environmentMethod33(self):
        e = CryptographicKeyParameter("0x1122ff",
                                      settings=KeyLocalSettings(
                                          read_only=True,
                                          removable=True))
        e.enableGlobal()
        assert type(e.settings) is KeyGlobalSettings
        e.enableLocal()
        assert type(e.settings) is KeyLocalSettings

        assert e.settings.isReadOnly()
        assert e.settings.isRemovable()

    def test_environmentMethod34(self):
        e = CryptographicKeyParameter("0x1122ff",
                                      settings=KeyLocalSettings(
                                          read_only=False,
                                          removable=False))
        e.enableGlobal()
        assert type(e.settings) is KeyGlobalSettings
        e.enableLocal()
        assert type(e.settings) is KeyLocalSettings

        assert not e.settings.isReadOnly()
        assert not e.settings.isRemovable()

    def test_clone(self):
        k = CryptographicKeyParameter("0x1122ff")
        k_clone = k.clone()

        assert k is not k_clone
        assert k.settings is not k_clone
        assert k.settings.checker is k_clone.settings.checker
        assert k.getValue() is not k_clone.getValue()
        assert k.getValue() == k_clone.getValue()
        assert hash(k.settings) == hash(k_clone.settings)
        assert hash(k) == hash(k_clone)
