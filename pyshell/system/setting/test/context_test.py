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

from pyshell.arg.checker.argchecker import ArgChecker
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.system.parameter.context import ContextParameter
from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.system.setting.context import CONTEXT_DEFAULT_CHECKER
from pyshell.system.setting.context import ContextGlobalSettings
from pyshell.system.setting.context import ContextLocalSettings
from pyshell.system.setting.context import ContextSettings
from pyshell.utils.constants import SETTING_PROPERTY_CHECKER
from pyshell.utils.constants import SETTING_PROPERTY_CHECKERLIST
from pyshell.utils.constants import SETTING_PROPERTY_DEFAULTINDEX
from pyshell.utils.constants import SETTING_PROPERTY_INDEX
from pyshell.utils.constants import SETTING_PROPERTY_READONLY
from pyshell.utils.constants import SETTING_PROPERTY_REMOVABLE
from pyshell.utils.constants import SETTING_PROPERTY_TRANSIENT
from pyshell.utils.constants import SETTING_PROPERTY_TRANSIENTINDEX
from pyshell.utils.exception import ParameterException


class TestContextLocalSettingsWithContextParameter(object):
    """
        This class uses ContextLocalSettings but the goal is to test the
        parent class ContextSettings
    """

    # setIndex with correct value
    def test_localSettings3(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,), settings=settings)
        settings.tryToSetDefaultIndex(2)
        settings.tryToSetIndex(1)
        assert c.getSelectedValue() == 1
        settings.setIndex(2)
        assert c.getSelectedValue() == 2

    # setIndex with incorrect value
    def test_localSettings4(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,),
                             settings=settings)
        settings.tryToSetDefaultIndex(2)
        settings.tryToSetIndex(1)
        assert c.getSelectedValue() == 1
        with pytest.raises(ParameterException):
            settings.setIndex(23)

    # setIndex with invalid value
    def test_localSettings5(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,),
                             settings=settings)
        settings.tryToSetDefaultIndex(2)
        settings.tryToSetIndex(1)
        assert c.getSelectedValue() == 1
        with pytest.raises(ParameterException):
            settings.setIndex("plop")

    # setIndex with valid value and readonly
    def test_localSettings6(self):
        settings = ContextLocalSettings(read_only=True,
                                        checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,), settings=settings)

        assert c.getSelectedValue() == 0
        settings.setIndex(2)
        assert c.getSelectedValue() == 2

    # tryToSetIndex with correct value
    def test_localSettings7(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,), settings=settings)
        settings.tryToSetDefaultIndex(2)
        assert c.getSelectedValue() == 0
        settings.tryToSetIndex(3)
        assert c.getSelectedValue() == 3

    # tryToSetIndex with incorrect value
    def test_localSettings8(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,), settings=settings)
        settings.tryToSetDefaultIndex(2)
        assert c.getSelectedValue() == 0
        settings.tryToSetIndex(23)
        assert c.getSelectedValue() == 0

    # tryToSetIndex with invalid value
    def test_localSettings9(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,), settings=settings)
        settings.tryToSetDefaultIndex(2)
        assert c.getSelectedValue() == 0
        settings.tryToSetIndex("plop")
        assert c.getSelectedValue() == 0

    # tryToSetIndex with incorrect value and default value recomputing
    def test_localSettings10(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,), settings=settings)
        settings.tryToSetDefaultIndex(2)
        settings.tryToSetIndex(1)
        assert c.getSelectedValue() == 1
        settings.default_index = 45
        settings.tryToSetIndex(80)
        assert c.getSelectedValue() == 1

    # tryToSetIndex with valid value and readonly
    def test_localSettings11(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,), settings=settings)
        settings.tryToSetDefaultIndex(2)
        settings.setReadOnly(True)

        assert c.getSelectedValue() == 0
        settings.tryToSetIndex(3)
        assert c.getSelectedValue() == 3

    # tryToSetIndex, create a test to set default_index
    def test_localSettings12(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,), settings=settings)
        settings.tryToSetDefaultIndex(1)
        settings.tryToSetIndex(3)
        assert c.getSelectedValue() == 3
        EnvironmentParameter.setValue(c, (11, 22, 33,))
        settings._setValuesSize(3)
        settings.tryToSetIndex(23)
        assert c.getSelectedValue() == 22

    def test_tryToSetIndexWithInvalidIndexAndCorruptedDefaults(self):
        settings = ContextSettings(checker=None)
        settings._setValuesSize(5)
        settings.index = 66
        settings.default_index = 23
        settings.tryToSetIndex(45)

        assert settings.getIndex() is 0
        assert settings.getDefaultIndex() is 0

    # test valid index
    def test_contextConstructor5(self):
        c = ContextParameter(value=(0, 1, 2, 3,))
        c.settings.tryToSetIndex(1)
        assert c.settings.getIndex() == 1

    # test invalid index
    def test_contextConstructor6(self):
        c = ContextParameter(value=(0, 1, 2, 3,))
        c.settings.tryToSetIndex(23)
        assert c.settings.getIndex() == 0

    # setSelectedValue with a valid value
    def test_localSettings13(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        assert c.getSelectedValue() == "aa"
        c.setSelectedValue("cc")
        assert c.getSelectedValue() == "cc"

    # setSelectedValue with a valid value but inexisting
    def test_localSettings14(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        assert c.getSelectedValue() == "aa"
        with pytest.raises(ParameterException):
            c.setSelectedValue("ee")

    # setSelectedValue with an invalid value
    def test_localSettings15(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        assert c.getSelectedValue() == "aa"
        with pytest.raises(ParameterException):
            c.setSelectedValue(object())

    # setSelectedValue with valid value and readonly
    def test_localSettings16(self):
        settings = ContextLocalSettings(read_only=True,
                                        checker=DefaultChecker.getString())
        c = ContextParameter(value=("aa", "bb", "cc", "dd",),
                             settings=settings)
        assert c.getSelectedValue() == "aa"
        c.setSelectedValue("cc")
        assert c.getSelectedValue() == "cc"

    # setDefaultIndex with correct value
    def test_localSettings17(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        ContextParameter(value=("aa", "bb", "cc", "dd",),
                         settings=settings)
        settings.tryToSetDefaultIndex(2)
        assert settings.getDefaultIndex() == 2
        settings.setDefaultIndex(1)
        assert settings.getDefaultIndex() == 1

    # setDefaultIndex with incorrect value
    def test_localSettings18(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        ContextParameter(value=("aa", "bb", "cc", "dd",),
                         settings=settings)
        settings.tryToSetDefaultIndex(2)
        with pytest.raises(ParameterException):
            settings.setDefaultIndex(23)

    # setDefaultIndex with invalid value
    def test_localSettings19(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        ContextParameter(value=("aa", "bb", "cc", "dd",),
                         settings=settings)
        settings.tryToSetDefaultIndex(2)
        with pytest.raises(ParameterException):
            settings.setDefaultIndex("plop")

    # setDefaultIndex with valid value and readonly
    def test_localSettings20(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        ContextParameter(value=("aa", "bb", "cc", "dd",),
                         settings=settings)
        settings.tryToSetDefaultIndex(2)
        settings.setReadOnly(True)
        with pytest.raises(ParameterException):
            settings.setDefaultIndex(1)

    # tryToSetDefaultIndex with correct value
    def test_localSettings21(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        ContextParameter(value=("aa", "bb", "cc", "dd",),
                         settings=settings)
        settings.tryToSetDefaultIndex(2)
        assert settings.getDefaultIndex() == 2
        settings.tryToSetDefaultIndex(1)
        assert settings.getDefaultIndex() == 1

    # tryToSetDefaultIndex with incorrect value
    def test_localSettings22(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        ContextParameter(value=("aa", "bb", "cc", "dd",),
                         settings=settings)
        settings.tryToSetDefaultIndex(2)
        assert settings.getDefaultIndex() == 2
        settings.tryToSetDefaultIndex(100)
        assert settings.getDefaultIndex() == 2

    # tryToSetDefaultIndex with invalid value
    def test_localSettings23(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        ContextParameter(value=("aa", "bb", "cc", "dd",),
                         settings=settings)
        settings.tryToSetDefaultIndex(2)
        assert settings.getDefaultIndex() == 2
        settings.tryToSetDefaultIndex("toto")
        assert settings.getDefaultIndex() == 2

    # tryToSetDefaultIndex with valid value and readonly
    def test_localSettings24(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        ContextParameter(value=("aa", "bb", "cc", "dd",),
                         settings=settings)
        settings.tryToSetDefaultIndex(2)
        settings.setReadOnly(True)
        with pytest.raises(ParameterException):
            settings.tryToSetDefaultIndex(1)

    # tryToSetDefaultIndex, create a test to set default_index to zero
    def test_localSettings25(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getInteger())
        c = ContextParameter(value=(0, 1, 2, 3,), settings=settings)
        settings.tryToSetDefaultIndex(3)
        assert settings.getDefaultIndex() == 3
        EnvironmentParameter.setValue(c, (11, 22, 33,))
        settings._setValuesSize(3)
        settings.tryToSetDefaultIndex(23)
        assert settings.getDefaultIndex() == 0

    # test valid default index
    def test_contextConstructor7(self):
        c = ContextParameter(value=(0, 1, 2, 3,))
        c.settings.tryToSetDefaultIndex(1)
        assert c.settings.getDefaultIndex() == 1

    # test invalid default index
    def test_contextConstructor8(self):
        c = ContextParameter(value=(0, 1, 2, 3,))
        c.settings.tryToSetDefaultIndex(42)
        assert c.settings.getDefaultIndex() == 0

    # test both invalid index AND invalid default index
    def test_contextConstructor9(self):
        c = ContextParameter(value=(0, 1, 2, 3,))
        c.settings.tryToSetDefaultIndex(42)
        c.settings.tryToSetIndex(23)
        assert c.settings.getDefaultIndex() == 0
        assert c.settings.getIndex() == 0

    # test reset
    def test_localSettings26(self):
        settings = ContextLocalSettings(checker=DefaultChecker.getString())
        ContextParameter(value=("aa", "bb", "cc", "dd",), settings=settings)
        settings.tryToSetDefaultIndex(2)
        settings.tryToSetIndex(1)
        assert settings.getDefaultIndex() == 2
        assert settings.getIndex() == 1
        settings.reset()
        assert settings.getDefaultIndex() == 2
        assert settings.getIndex() == 2

    # test getProperties
    def test_localSettings27(self):
        settings = ContextLocalSettings(removable=False)
        ContextParameter(value=(0, 1, 2, 3,), settings=settings)
        settings.tryToSetDefaultIndex(3)
        settings.tryToSetIndex(2)
        settings.setReadOnly(True)
        props = {SETTING_PROPERTY_REMOVABLE: False,
                 SETTING_PROPERTY_READONLY: True,
                 SETTING_PROPERTY_CHECKER: 'any',
                 SETTING_PROPERTY_CHECKERLIST: True,
                 SETTING_PROPERTY_DEFAULTINDEX: 3}
        assert settings.getProperties() == props

    def test_cloneWithoutSource(self):
        s = ContextLocalSettings(checker=DefaultChecker.getInteger())
        ContextParameter(value=(0, 1, 2, 3,), settings=s)
        s.setDefaultIndex(2)
        s.setIndex(1)

        sc = s.clone()

        assert isinstance(sc, ContextLocalSettings)
        assert s is not sc
        assert hash(s) != hash(sc)  # because of the indexes
        assert sc.getDefaultIndex() == 0
        assert sc.getIndex() == 0
        assert sc.values_size == 0


class TestContextSettingsWithoutContextParameter(object):

    def test_setValuesSize(self):
        settings = ContextSettings(checker=None)
        settings._setValuesSize(23)
        assert settings.values_size is 23

    def test_isValidIndexNotAnInt(self):
        settings = ContextSettings(checker=None)
        settings._setValuesSize(5)
        assert not settings._isValidIndex("toto")

    def test_isValidIndexValidMinusInt(self):
        settings = ContextSettings(checker=None)
        settings._setValuesSize(5)
        assert not settings._isValidIndex(-20)
        assert not settings._isValidIndex(-6)

    def test_isValidIndexInvalidMinusInt(self):
        settings = ContextSettings(checker=None)
        settings._setValuesSize(5)
        assert settings._isValidIndex(-5)
        assert settings._isValidIndex(-1)

    def test_isValidIndexInvalidPositivIt(self):
        settings = ContextSettings(checker=None)
        settings._setValuesSize(5)
        assert not settings._isValidIndex(8000)
        assert not settings._isValidIndex(5)

    def test_isValidIndexValidPositivInt(self):
        settings = ContextSettings(checker=None)
        settings._setValuesSize(5)
        assert settings._isValidIndex(4)
        assert settings._isValidIndex(0)

    # None checker
    def test_contextConstructor1(self):
        settings = ContextSettings(checker=None)
        assert settings.isListChecker()
        assert settings.getChecker().getMinimumSize() == 1
        assert settings.getChecker().getMaximumSize() is None

        sub_checker = settings.getChecker().checker
        assert sub_checker.__class__.__name__ == ArgChecker.__name__
        assert isinstance(sub_checker, ArgChecker)

    # arg checker
    def test_contextConstructor2(self):
        settings = ContextSettings(checker=DefaultChecker.getInteger())
        assert settings.isListChecker()
        assert settings.getChecker().getMinimumSize() == 1
        assert settings.getChecker().getMaximumSize() is None

        assert isinstance(settings.getChecker().checker, IntegerArgChecker)

    # arg checker with min size of 0
    def test_contextConstructor2b(self):
        with pytest.raises(ParameterException):
            checker = ArgChecker(minimum_size=0, maximum_size=0)
            ContextSettings(checker=checker)

    # list checker + #list checker with size not adapted to context
    def test_contextConstructor3(self):
        lt = ListArgChecker(DefaultChecker.getInteger(), 3, 27)
        settings = ContextSettings(checker=lt)
        assert settings.isListChecker()
        assert settings.getChecker().getMinimumSize() == 1
        assert settings.getChecker().getMaximumSize() == 27
        assert isinstance(settings.getChecker().checker, IntegerArgChecker)

    def test_setCheckerNoneWithoutPreviousChecker(self):
        settings = ContextSettings()
        checker = settings.getChecker()

        settings.setChecker(checker=None)

        checker2 = settings.getChecker()

        assert checker is checker2

    def test_setCheckerNoneWithPreviousChecker(self):
        original_checker = ListArgChecker(DefaultChecker.getString())
        settings = ContextSettings(checker=original_checker)
        checker = settings.getChecker()
        assert checker is original_checker

        settings.setChecker(checker=None)

        checker2 = settings.getChecker()

        assert checker is not checker2
        assert checker2 is CONTEXT_DEFAULT_CHECKER

    def test_setCheckerNotAList(self):
        settings = ContextSettings()
        checker = DefaultChecker.getString()
        settings.setChecker(checker=checker)
        assert settings.isListChecker()
        assert settings.getChecker().checker is checker

    def test_setCheckerListWithMinSizeBiggerThanZero(self):
        settings = ContextSettings()
        original_checker = ListArgChecker(checker=DefaultChecker.getString(),
                                          minimum_size=14,
                                          maximum_size=56)
        settings.setChecker(original_checker)

        new_checker = settings.getChecker()

        assert new_checker is original_checker
        assert new_checker.getMinimumSize() == 1
        assert new_checker.getMaximumSize() == 56

    def test_setCheckerListWithItemLargerThanOne(self):
        settings = ContextSettings()
        original_sub_checker = ArgChecker()
        original_sub_checker.setSize(minimum_size=5, maximum_size=5)
        original_checker = ListArgChecker(checker=original_sub_checker,
                                          minimum_size=5)
        with pytest.raises(ParameterException):
            settings.setChecker(original_checker)

    def test_setCheckerArgLargerThanOne(self):
        settings = ContextSettings()
        original_checker = ArgChecker()
        original_checker.setSize(minimum_size=5, maximum_size=5)

        with pytest.raises(ParameterException):
            settings.setChecker(original_checker)

    def test_setListCheckerTrue(self):
        settings = ContextSettings()
        assert settings.isListChecker()
        settings.setListChecker(True)
        assert settings.isListChecker()

    def test_setListCheckerFalse(self):
        settings = ContextSettings()
        assert settings.isListChecker()
        with pytest.raises(ParameterException):
            settings.setListChecker(False)
        assert settings.isListChecker()

    def test_cloneWithoutSource(self):
        zs = ContextSettings(checker=DefaultChecker.getInteger())
        zsc = zs.clone()

        assert isinstance(zsc, ContextSettings)
        assert zs is not zsc
        assert hash(zs) == hash(zsc)
        assert zs.getChecker() is zsc.getChecker()
        assert zsc.values_size == 0


class TestContextLocalSettingsWithoutContextParameter(object):
    def test_constructor1(self):
        lcs = ContextLocalSettings(read_only=False, removable=False)
        assert not lcs.isReadOnly()
        assert not lcs.isRemovable()

    def test_constructor2(self):
        lcs = ContextLocalSettings(read_only=True, removable=True)
        assert lcs.isReadOnly()
        assert lcs.isRemovable()

    def test_setTransientIndex(self):
        lcs = ContextLocalSettings()
        assert lcs.isTransientIndex()
        with pytest.raises(ParameterException):
            lcs.setTransientIndex(False)
        assert lcs.isTransientIndex()

    def test_cloneWithoutSource(self):
        s = ContextLocalSettings(checker=DefaultChecker.getInteger())
        sc = s.clone()

        assert isinstance(sc, ContextLocalSettings)
        assert s is not sc
        assert hash(s) == hash(sc)
        assert sc.values_size == 0

    def test_getGlobalFromLocal(self):
        checker = DefaultChecker.getInteger()
        ls = ContextLocalSettings(read_only=True,
                                  removable=False,
                                  checker=checker)

        gs = ls.getGlobalFromLocal()

        assert type(gs) is ContextGlobalSettings
        assert gs.isReadOnly()
        assert not gs.isRemovable()
        assert gs.getChecker() is ls.getChecker()


class TestContextGlobalSettingsWithContextParameter(object):

    # test transientIndex
    def test_contextConstructor10(self):
        settings = ContextGlobalSettings(transient_index=False)
        ContextParameter(value=(0, 1, 2, 3,), settings=settings)
        settings.tryToSetIndex(2)
        assert not settings.isTransientIndex()
        props = {SETTING_PROPERTY_REMOVABLE: True,
                 SETTING_PROPERTY_READONLY: False,
                 SETTING_PROPERTY_TRANSIENT: False,
                 SETTING_PROPERTY_CHECKER: 'any',
                 SETTING_PROPERTY_CHECKERLIST: True,
                 SETTING_PROPERTY_TRANSIENTINDEX: False,
                 SETTING_PROPERTY_DEFAULTINDEX: 0,
                 SETTING_PROPERTY_INDEX: 2}
        assert settings.getProperties() == props

    def test_contextConstructor10b(self):
        settings = ContextGlobalSettings(transient_index=True)
        ContextParameter(value=(0, 1, 2, 3,), settings=settings)
        settings.tryToSetIndex(2)
        assert settings.isTransientIndex()
        props = {SETTING_PROPERTY_REMOVABLE: True,
                 SETTING_PROPERTY_READONLY: False,
                 SETTING_PROPERTY_TRANSIENT: False,
                 SETTING_PROPERTY_CHECKER: 'any',
                 SETTING_PROPERTY_CHECKERLIST: True,
                 SETTING_PROPERTY_TRANSIENTINDEX: True,
                 SETTING_PROPERTY_DEFAULTINDEX: 0}
        assert settings.getProperties() == props

    # __init__ test each properties, True
    def test_globalSettings1(self):
        settings = ContextGlobalSettings(read_only=True,
                                         removable=True,
                                         transient=True,
                                         transient_index=True,
                                         checker=DefaultChecker.getString())
        ContextParameter(value=("aa", "bb", "cc", "dd",), settings=settings)
        assert settings.isReadOnly()
        assert settings.isRemovable()
        assert settings.isTransient()
        assert settings.isTransientIndex()

    # __init__ test each properties, False
    def test_globalSettings2(self):
        settings = ContextGlobalSettings(read_only=False,
                                         removable=False,
                                         transient=False,
                                         transient_index=False,
                                         checker=DefaultChecker.getString())
        ContextParameter(value=("aa", "bb", "cc", "dd",), settings=settings)
        assert not settings.isReadOnly()
        assert not settings.isRemovable()
        assert not settings.isTransient()
        assert not settings.isTransientIndex()

    # test getProperties not transient index
    def test_globalSettings6(self):
        settings = ContextGlobalSettings(transient_index=False)
        ContextParameter(value=(0, 1, 2, 3,), settings=settings)
        settings.tryToSetDefaultIndex(3)
        settings.tryToSetIndex(2)
        props = {SETTING_PROPERTY_REMOVABLE: True,
                 SETTING_PROPERTY_READONLY: False,
                 SETTING_PROPERTY_TRANSIENT: False,
                 SETTING_PROPERTY_CHECKER: 'any',
                 SETTING_PROPERTY_CHECKERLIST: True,
                 SETTING_PROPERTY_TRANSIENTINDEX: False,
                 SETTING_PROPERTY_DEFAULTINDEX: 3,
                 SETTING_PROPERTY_INDEX: 2}
        assert settings.getProperties() == props

    # test getProperties transient index
    def test_globalSettings7(self):
        settings = ContextGlobalSettings(transient_index=True)
        ContextParameter(value=(0, 1, 2, 3,), settings=settings)
        settings.tryToSetDefaultIndex(3)
        settings.tryToSetIndex(2)
        props = {SETTING_PROPERTY_REMOVABLE: True,
                 SETTING_PROPERTY_READONLY: False,
                 SETTING_PROPERTY_TRANSIENT: False,
                 SETTING_PROPERTY_CHECKER: 'any',
                 SETTING_PROPERTY_CHECKERLIST: True,
                 SETTING_PROPERTY_TRANSIENTINDEX: True,
                 SETTING_PROPERTY_DEFAULTINDEX: 3}
        assert settings.getProperties() == props

    def test_cloneWithoutSource(self):
        s = ContextGlobalSettings(checker=DefaultChecker.getInteger())
        s.setTransientIndex(True)
        ContextParameter(value=(0, 1, 2, 3,), settings=s)
        s.setDefaultIndex(2)
        s.setIndex(1)

        sc = s.clone()

        assert isinstance(sc, ContextGlobalSettings)
        assert s is not sc
        assert hash(s) != hash(sc)  # because of the indexes
        assert sc.getDefaultIndex() == 0
        assert sc.getIndex() == 0
        assert sc.values_size == 0
        assert s.isTransientIndex()


class TestContextGlobalSettingsWithoutContextParameter(object):
    # test setTransientIndex in readonly mode
    def test_globalSettings3(self):
        settings = ContextGlobalSettings(read_only=True,
                                         checker=DefaultChecker.getString())
        with pytest.raises(ParameterException):
            settings.setTransientIndex(True)

    # test setTransientIndex with invalid bool
    def test_globalSettings4(self):
        settings = ContextGlobalSettings(checker=DefaultChecker.getString())
        with pytest.raises(ParameterException):
            settings.setTransientIndex("plop")

    # test setTransientIndex with valid bool
    def test_globalSettings5(self):
        settings = ContextGlobalSettings(checker=DefaultChecker.getString())
        assert not settings.isTransientIndex()
        settings.setTransientIndex(True)
        assert settings.isTransientIndex()

    def test_cloneWithoutSource(self):
        s = ContextGlobalSettings(checker=DefaultChecker.getInteger())
        s.setTransientIndex(True)
        sc = s.clone()

        assert isinstance(sc, ContextGlobalSettings)
        assert s is not sc
        assert hash(s) == hash(sc)
        assert sc.values_size == 0
        assert sc.isTransientIndex()

    def test_getLocalFromGlobal(self):
        checker = DefaultChecker.getInteger()
        gs = ContextGlobalSettings(read_only=True,
                                   removable=False,
                                   transient=True,
                                   transient_index=True,
                                   checker=checker)

        ls = gs.getLocalFromGlobal()

        assert type(ls) is ContextLocalSettings
        assert ls.isReadOnly()
        assert not ls.isRemovable()
        assert ls.getChecker() is gs.getChecker()
