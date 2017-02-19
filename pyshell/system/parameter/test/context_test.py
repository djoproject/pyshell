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

from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.exception import ArgException
from pyshell.system.parameter.context import ContextParameter
from pyshell.system.parameter.context import _convertToSetList
from pyshell.system.setting.context import ContextGlobalSettings
from pyshell.system.setting.context import ContextLocalSettings
from pyshell.utils.exception import ParameterException


class TestMisc(object):

    def test_convertToSetList(self):
        converted = _convertToSetList(("aaa", "bbb", "aaa", "ccc", "ccc"))
        assert converted == ["aaa", "bbb", "ccc"]


class TestContextParameter(object):

    def test_notAContextSettingClass(self):
        with pytest.raises(ParameterException):
            ContextParameter(value=(0,), settings=object())

    # setValue with valid value
    def test_context1(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0,), settings=settings)
        c.setValue((1, 2, 3, "4",))
        assert c.getValue() == [1, 2, 3, 4, ]

    # setValue with invalid value
    def test_context2(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0,), settings=settings)
        with pytest.raises(ArgException):
            c.setValue((1, 2, 3, "plop",))

    # test addValues to add valid
    def test_context3(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,),
                             settings=settings)
        c.addValues((4, 5, 6,))
        assert c.getValue() == [0, 1, 2, 3, 4, 5, 6]

    # test addValues to add invalid value
    def test_context4(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,),
                             settings=settings)
        with pytest.raises(ArgException):
            c.addValues((4, 5, "plop",))

    # removeValues, remove all value
    def test_context5(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        with pytest.raises(ParameterException):
            c.removeValues(("aa", "bb", "cc", "dd",))

    # removeValues, remove unexisting value
    def test_context6(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        assert c.getValue() == ["aa", "bb", "cc", "dd"]
        c.removeValues(("aa", "aa", "ee", "ff",))
        assert c.getValue() == ["bb", "cc", "dd"]

    def test_removeOnlyUnexistingValues(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        assert c.getValue() == ["aa", "bb", "cc", "dd"]
        c.removeValues(("zz", "yy", "xx", "ww",))
        assert c.getValue() == ["aa", "bb", "cc", "dd"]

    # removeValues, try to remove with read only
    def test_context7(self):
        settings = ContextLocalSettings(read_only=True,
                                        checker=DefaultChecker.getString())
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        assert c.getValue() == ["aa", "bb", "cc", "dd"]
        with pytest.raises(ParameterException):
            c.removeValues(("aa", "aa", "ee", "ff",))

    # removeValues, success remove
    def test_context8(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        assert c.getValue() == ["aa", "bb", "cc", "dd"]
        c.removeValues(("aa",))
        assert c.getValue() == ["bb", "cc", "dd"]

    # removeValues, success remove with index computation
    def test_context9(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        c.settings.tryToSetDefaultIndex(2)
        c.settings.tryToSetIndex(3)
        assert c.getValue() == ["aa", "bb", "cc", "dd"]
        assert c.settings.getDefaultIndex() == 2
        assert c.settings.getIndex() == 3
        c.removeValues(("cc", "dd",))
        assert c.getValue() == ["aa", "bb"]
        assert c.settings.getDefaultIndex() == 0
        assert c.settings.getIndex() == 0

    def test_setSelectedValueExistingValue(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,),
                             settings=settings)

        assert c.getSelectedValue() is 0
        c.setSelectedValue(2)
        assert c.getSelectedValue() is 2

    def test_setSelectedValueUnexistingValue(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,),
                             settings=settings)

        assert c.getSelectedValue() is 0
        with pytest.raises(ParameterException):
            c.setSelectedValue(2222)
        assert c.getSelectedValue() is 0

    def test_setSelectedValueInvalidValue(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,),
                             settings=settings)

        assert c.getSelectedValue() is 0
        with pytest.raises(ArgException):
            c.setSelectedValue("toto")
        assert c.getSelectedValue() is 0

    # test repr
    def test_context10(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        c.settings.tryToSetDefaultIndex(2)
        c.settings.tryToSetIndex(1)
        assert repr(c) == ("Context, available values: "
                           "['aa', 'bb', 'cc', 'dd'], selected index: 1, "
                           "selected value: bb")

    # test str
    def test_context11(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        c.settings.tryToSetDefaultIndex(2)
        c.settings.tryToSetIndex(1)
        assert str(c) == "bb"

    # test enableGlobal
    def test_context12(self):
        c = ContextParameter(value=("aa", "bb", "cc", "dd",))

        assert isinstance(c.settings, ContextLocalSettings)
        c.enableGlobal()
        assert isinstance(c.settings, ContextGlobalSettings)
        s = c.settings
        c.enableGlobal()
        assert c.settings is s

    # test enableLocal
    def test_context13(self):
        c = ContextParameter(value=("aa", "bb", "cc", "dd",))

        assert isinstance(c.settings, ContextLocalSettings)
        s = c.settings
        c.enableGlobal()
        assert isinstance(c.settings, ContextGlobalSettings)
        c.enableLocal()
        assert isinstance(c.settings, ContextLocalSettings)
        assert c.settings is not s
        s = c.settings
        c.enableLocal()
        assert c.settings is s

    def test_context14(self):
        settings = ContextLocalSettings(removable=True)
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        c.settings.tryToSetDefaultIndex(3)
        c.settings.tryToSetIndex(2)
        c.settings.setReadOnly(True)
        c.enableGlobal()
        assert isinstance(c.settings, ContextGlobalSettings)
        assert c.settings.isReadOnly()
        assert c.settings.isRemovable()
        assert c.settings.getIndex() == 2
        assert c.settings.getDefaultIndex() == 3

    def test_context15(self):
        settings = ContextLocalSettings(read_only=False, removable=False)
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        c.settings.tryToSetDefaultIndex(2)
        c.settings.tryToSetIndex(3)
        c.enableGlobal()
        assert isinstance(c.settings, ContextGlobalSettings)
        assert not c.settings.isReadOnly()
        assert not c.settings.isRemovable()
        assert c.settings.getIndex() == 3
        assert c.settings.getDefaultIndex() == 2

    def test_context16(self):
        settings = ContextLocalSettings(removable=True)
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        c.settings.tryToSetDefaultIndex(3)
        c.settings.tryToSetIndex(2)
        c.settings.setReadOnly(True)
        c.enableGlobal()
        assert isinstance(c.settings, ContextGlobalSettings)
        c.enableLocal()
        assert isinstance(c.settings, ContextLocalSettings)

        assert c.settings.isReadOnly()
        assert c.settings.isRemovable()
        assert c.settings.getIndex() == 2
        assert c.settings.getDefaultIndex() == 3

    def test_context17(self):
        settings = ContextLocalSettings(read_only=False, removable=False)
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        c.settings.tryToSetDefaultIndex(2)
        c.settings.tryToSetIndex(3)
        c.enableGlobal()
        assert isinstance(c.settings, ContextGlobalSettings)
        c.enableLocal()
        assert isinstance(c.settings, ContextLocalSettings)

        assert not c.settings.isReadOnly()
        assert not c.settings.isRemovable()
        assert c.settings.getIndex() == 3
        assert c.settings.getDefaultIndex() == 2

    def test_clone(self):
        c = ContextParameter(value=("aa", "bb", "cc", "dd",))
        c_clone = c.clone()

        assert c is not c_clone
        assert c.settings is not c_clone
        assert c.settings.checker is c_clone.settings.checker
        assert c.getValue() is not c_clone.getValue()
        assert c.getValue() == c_clone.getValue()
        assert hash(c.settings) == hash(c_clone.settings)
        assert hash(c) == hash(c_clone)

    def test_cloneWithReadOnly(self):
        c = ContextParameter(value=("aa", "bb", "cc", "dd",))
        c.settings.setReadOnly(True)
        c_clone = c.clone()

        assert c is not c_clone
        assert c.settings is not c_clone
        assert c.settings.checker is c_clone.settings.checker
        assert c.getValue() is not c_clone.getValue()
        assert c.getValue() == c_clone.getValue()
        assert hash(c.settings) == hash(c_clone.settings)
        assert hash(c) == hash(c_clone)

    def test_cloneWithParent(self):
        c = ContextParameter(value=("aa", "bb", "cc", "dd",))
        c_clone = ContextParameter(value=("11", "22", "33",))
        c_clone.settings.setReadOnly(True)
        c.clone(c_clone)

        assert c is not c_clone
        assert c.settings is not c_clone
        assert c.settings.checker is c_clone.settings.checker
        assert c.getValue() is not c_clone.getValue()
        assert c.getValue() == c_clone.getValue()
        assert hash(c.settings) == hash(c_clone.settings)
        assert hash(c) == hash(c_clone)
