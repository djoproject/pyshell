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

from pyshell.arg.exception import ArgException
from pyshell.system.manager.key import CryptographicKeyParameterManager
from pyshell.system.manager.test.fakeparent import FakeParentManager
from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.system.parameter.key import CryptographicKeyParameter
from pyshell.utils.constants import KEY_ATTRIBUTE_NAME
from pyshell.utils.exception import ParameterException
from pyshell.utils.key import CryptographicKey


class TestCryptographicKeyParameterManager(object):

    def test_manager(self):
        manager = CryptographicKeyParameterManager(FakeParentManager())
        assert manager is not None

    def test_getLoaderName(self):
        name = CryptographicKeyParameterManager.getLoaderName()
        assert name is KEY_ATTRIBUTE_NAME

    def test_addNotYetParametrizedButValidKey(self):
        manager = CryptographicKeyParameterManager(FakeParentManager())
        manager.setParameter("test.key", "0x1122ff")
        assert manager.hasParameter("t.k")
        param = manager.getParameter("te.ke")
        assert isinstance(param, CryptographicKeyParameter)
        assert isinstance(param.getValue(), CryptographicKey)
        assert str(param.getValue()) == "0x1122ff"

    def test_addNotYetParametrizedAndInValidKey(self):
        manager = CryptographicKeyParameterManager(FakeParentManager())
        with pytest.raises(ArgException):
            manager.setParameter("test.key", "0xplop")

    def test_addValidParameter(self):
        manager = CryptographicKeyParameterManager(FakeParentManager())
        manager.setParameter("test.key", CryptographicKeyParameter("0x1122ff"))
        assert manager.hasParameter("t.k")
        param = manager.getParameter("te.ke")
        assert isinstance(param, CryptographicKeyParameter)
        assert isinstance(param.getValue(), CryptographicKey)
        assert str(param.getValue()) == "0x1122ff"

    def test_addNotAllowedParameter(self):
        manager = CryptographicKeyParameterManager(FakeParentManager())
        with pytest.raises(ParameterException):
            manager.setParameter("test.key", EnvironmentParameter("0x1122ff"))
