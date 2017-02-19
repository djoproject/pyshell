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

from threading import Lock

import pytest

from pyshell.arg.checker.argchecker import ArgChecker
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.arg.exception import ArgException
from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.system.parameter.environment import ParametersLocker
from pyshell.system.parameter.environment import _lockKey
from pyshell.system.setting.environment import EnvironmentGlobalSettings
from pyshell.system.setting.environment import EnvironmentLocalSettings
from pyshell.utils.constants import SETTING_PROPERTY_CHECKER
from pyshell.utils.constants import SETTING_PROPERTY_CHECKERLIST
from pyshell.utils.constants import SETTING_PROPERTY_READONLY
from pyshell.utils.constants import SETTING_PROPERTY_REMOVABLE
from pyshell.utils.constants import SETTING_PROPERTY_TRANSIENT
from pyshell.utils.exception import ParameterException

try:
    from thread import LockType
except:
    from _thread import LockType


class DummyLock(object):

    def __init__(self, value):
        self.value = value
        self.lock = Lock()

    def getLockId(self):
        return self.value

    def getLock(self):
        return self.lock


class TestEnvironment(object):
    # # misc # #
    # test lockSorter

    def test_misc1(self):
        sorted_list = sorted([DummyLock(5),
                              DummyLock(1),
                              DummyLock(4),
                              DummyLock(0),
                              DummyLock(888)],
                             key=_lockKey)
        assert sorted_list[0].value == 0
        assert sorted_list[1].value == 1
        assert sorted_list[2].value == 4
        assert sorted_list[3].value == 5
        assert sorted_list[4].value == 888

    # test ParametersLocker, just try a lock in a single thread with several
    # lock
    def test_misc2(self):
        lockers = ParametersLocker([DummyLock(5),
                                    DummyLock(1),
                                    DummyLock(4),
                                    DummyLock(0),
                                    DummyLock(888)])
        with lockers:
            pass

    # # parameter constructor # #

    # test removable boolean
    def test_environmentConstructor1(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     removable=True))
        assert e.settings.isRemovable()
        props = ((SETTING_PROPERTY_REMOVABLE, True),
                 (SETTING_PROPERTY_READONLY, False),
                 (SETTING_PROPERTY_TRANSIENT, True),
                 (SETTING_PROPERTY_CHECKER, 'any'),
                 (SETTING_PROPERTY_CHECKERLIST, True))
        assert e.settings.getProperties() == props

        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     removable=False))
        assert not e.settings.isRemovable()
        props = ((SETTING_PROPERTY_REMOVABLE, False),
                 (SETTING_PROPERTY_READONLY, False),
                 (SETTING_PROPERTY_TRANSIENT, True),
                 (SETTING_PROPERTY_CHECKER, 'any'),
                 (SETTING_PROPERTY_CHECKERLIST, True))
        assert e.settings.getProperties() == props

    # test readonly boolean
    def test_environmentConstructor2(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=True))
        assert e.settings.isReadOnly()
        props = ((SETTING_PROPERTY_REMOVABLE, True),
                 (SETTING_PROPERTY_READONLY, True),
                 (SETTING_PROPERTY_TRANSIENT, True),
                 (SETTING_PROPERTY_CHECKER, 'any'),
                 (SETTING_PROPERTY_CHECKERLIST, True))
        assert e.settings.getProperties() == props

        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=False))
        assert not e.settings.isReadOnly()
        props = ((SETTING_PROPERTY_REMOVABLE, True),
                 (SETTING_PROPERTY_READONLY, False),
                 (SETTING_PROPERTY_TRANSIENT, True),
                 (SETTING_PROPERTY_CHECKER, 'any'),
                 (SETTING_PROPERTY_CHECKERLIST, True))
        assert e.settings.getProperties() == props

    # test typ None
    def test_environmentConstructor3(self):
        e = EnvironmentParameter("plop")
        assert isinstance(e.settings.checker, ListArgChecker)
        assert e.settings.checker.minimum_size is None
        assert e.settings.checker.maximum_size is None

        sub_checker_name = e.settings.checker.checker.__class__.__name__
        assert sub_checker_name == ArgChecker.__name__
        assert isinstance(e.settings.checker.checker, ArgChecker)

    # test typ not an argchecker
    def test_environmentConstructor4(self):
        with pytest.raises(ParameterException):
            EnvironmentParameter("plop", object())

    # test typ valid argchecker not a list + isListChecker
    def test_environmentConstructor5(self):
        settings = EnvironmentLocalSettings(
            checker=DefaultChecker.getInteger())
        e = EnvironmentParameter(42, settings=settings)
        assert isinstance(e.settings.checker, IntegerArgChecker)
        assert not e.settings.isListChecker()

    # test typ valid argchecker list + isListChecker
    def test_environmentConstructor6(self):
        settings = EnvironmentLocalSettings(
            checker=ListArgChecker(DefaultChecker.getInteger()))
        e = EnvironmentParameter(42, settings=settings)
        assert isinstance(e.settings.checker, ListArgChecker)
        assert e.settings.checker.minimum_size is None
        assert e.settings.checker.maximum_size is None
        sub_checker_name = e.settings.checker.checker.__class__.__name__
        assert sub_checker_name == IntegerArgChecker.__name__
        assert isinstance(e.settings.checker.checker, IntegerArgChecker)
        assert e.settings.isListChecker()

    # # parameter method # #

    # _raiseIfReadOnly with not readonly
    def test_environmentMethod2(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=False))
        assert e.settings._raiseIfReadOnly() is None

    # _raiseIfReadOnly with readonly and method name
    def test_environmentMethod3(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=True))
        with pytest.raises(ParameterException):
            e.settings._raiseIfReadOnly("meth")

    # _raiseIfReadOnly with readonly and no method name
    def test_environmentMethod4(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=True))
        with pytest.raises(ParameterException):
            e.settings._raiseIfReadOnly()

    # getLock with lock disabled
    def test_environmentMethod5(self):
        e = EnvironmentParameter("plop")
        e.enableLocal()
        assert e.getLock() is None
        assert e.getLockId() == -1
        assert not e.isLockEnable()

    # getLock without lock disabled
    def test_environmentMethod6(self):
        e = EnvironmentParameter("plop")
        e.enableGlobal()
        assert isinstance(e.getLock(), LockType)
        assert e.getLockId() == 0
        assert e.isLockEnable()

    # addValues readonly
    def test_environmentMethod10(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=True))
        with pytest.raises(ParameterException):
            e.addValues(("aa", "bb", "cc",))

    # addValues with non list typ
    def test_environmentMethod11(self):
        settings = EnvironmentLocalSettings(
            checker=DefaultChecker.getInteger())
        e = EnvironmentParameter(42, settings=settings)
        with pytest.raises(ParameterException):
            e.addValues((1, 23, 69,))

    # addValues with not iterable value
    def test_environmentMethod12(self):
        e = EnvironmentParameter(42)
        e.addValues(33)
        assert e.getValue() == [42, 33]

    # addValues with invalid values in front of the checker
    def test_environmentMethod13(self):
        settings = EnvironmentLocalSettings(
            checker=ListArgChecker(DefaultChecker.getInteger()))
        e = EnvironmentParameter(42, settings=settings)
        with pytest.raises(ArgException):
            e.addValues(("plop", "plip", "plap",))

    # addValues success
    def test_environmentMethod13b(self):
        e = EnvironmentParameter("plop")
        e.addValues(("aa", "bb", "cc",))
        assert e.getValue() == ["plop", "aa", "bb", "cc"]

    # removeValues readonly
    def test_environmentMethod14(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=True))
        with pytest.raises(ParameterException):
            e.removeValues("plop")

    # removeValues with non list typ
    def test_environmentMethod15(self):
        settings = EnvironmentLocalSettings(
            checker=DefaultChecker.getInteger())
        e = EnvironmentParameter(42, settings=settings)
        with pytest.raises(ParameterException):
            e.removeValues(42)

    # removeValues with not iterable value
    def test_environmentMethod16(self):
        e = EnvironmentParameter("plop")
        e.removeValues("plop")
        assert e.getValue() == []

    # removeValues with existing and not existing value
    def test_environmentMethod17(self):
        e = EnvironmentParameter(["plop", "plip", "plap", "plup"])
        e.removeValues(("plip", "plip", "ohoh", "titi", "plop",))
        assert e.getValue() == ["plap", "plup"]

    # removeValues with zero value
    def test_environmentMethod17a(self):
        e = EnvironmentParameter(["plop", "plip", "plap", "plup"])
        e.removeValues(())
        assert e.getValue() == ["plop", "plip", "plap", "plup"]

    # setValue valid
    def test_environmentMethod18(self):
        e = EnvironmentParameter("plop")
        assert e.getValue() == ["plop"]
        e.setValue("plip")
        assert e.getValue() == ["plip"]
        e.setValue(("aa", "bb", "cc",))
        assert e.getValue() == ["aa", "bb", "cc"]

        settings = EnvironmentLocalSettings(
            checker=DefaultChecker.getInteger())
        e = EnvironmentParameter(42, settings=settings)
        assert e.getValue() == 42
        e.setValue(23)
        assert e.getValue() == 23

    # setValue unvalid
    def test_environmentMethod19(self):
        settings = EnvironmentLocalSettings(
            checker=DefaultChecker.getInteger())
        e = EnvironmentParameter(42, settings=settings)
        with pytest.raises(ArgException):
            e.setValue("plop")

        settings = EnvironmentLocalSettings(
            checker=ListArgChecker(DefaultChecker.getInteger()))
        e = EnvironmentParameter(42, settings=settings)
        with pytest.raises(ArgException):
            e.setValue(("plop", "plap",))

    # setReadOnly with not valid bool
    def test_environmentMethod22(self):
        e = EnvironmentParameter("plop")
        with pytest.raises(ParameterException):
            e.settings.setReadOnly(object())

    # setReadOnly with valid bool + getProp
    def test_environmentMethod23(self):
        e = EnvironmentParameter("plop")
        e.enableLocal()
        assert not e.settings.isReadOnly()
        props = ((SETTING_PROPERTY_REMOVABLE, True),
                 (SETTING_PROPERTY_READONLY, False),
                 (SETTING_PROPERTY_TRANSIENT, True),
                 (SETTING_PROPERTY_CHECKER, 'any'),
                 (SETTING_PROPERTY_CHECKERLIST, True))
        assert e.settings.getProperties() == props

        e.settings.setReadOnly(True)
        assert e.settings.isReadOnly()
        props = ((SETTING_PROPERTY_REMOVABLE, True),
                 (SETTING_PROPERTY_READONLY, True),
                 (SETTING_PROPERTY_TRANSIENT, True),
                 (SETTING_PROPERTY_CHECKER, 'any'),
                 (SETTING_PROPERTY_CHECKERLIST, True))
        assert e.settings.getProperties() == props

        e.settings.setReadOnly(False)
        assert not e.settings.isReadOnly()
        props = ((SETTING_PROPERTY_REMOVABLE, True),
                 (SETTING_PROPERTY_READONLY, False),
                 (SETTING_PROPERTY_TRANSIENT, True),
                 (SETTING_PROPERTY_CHECKER, 'any'),
                 (SETTING_PROPERTY_CHECKERLIST, True))
        assert e.settings.getProperties() == props

    # setRemovable readonly
    def test_environmentMethod24(self):
        e = EnvironmentParameter(
            "plop", settings=EnvironmentLocalSettings(
                read_only=True))
        with pytest.raises(ParameterException):
            e.settings.setRemovable(True)

    # setRemovable with not valid bool
    def test_environmentMethod25(self):
        e = EnvironmentParameter("plop")
        with pytest.raises(ParameterException):
            e.settings.setRemovable(object())

    # setRemovable with valid bool + getProp
    def test_environmentMethod26(self):
        e = EnvironmentParameter("plop")
        e.enableLocal()
        assert e.settings.isRemovable()
        props = ((SETTING_PROPERTY_REMOVABLE, True),
                 (SETTING_PROPERTY_READONLY, False),
                 (SETTING_PROPERTY_TRANSIENT, True),
                 (SETTING_PROPERTY_CHECKER, 'any'),
                 (SETTING_PROPERTY_CHECKERLIST, True))
        assert e.settings.getProperties() == props

        e.settings.setRemovable(False)
        assert not e.settings.isRemovable()
        props = ((SETTING_PROPERTY_REMOVABLE, False),
                 (SETTING_PROPERTY_READONLY, False),
                 (SETTING_PROPERTY_TRANSIENT, True),
                 (SETTING_PROPERTY_CHECKER, 'any'),
                 (SETTING_PROPERTY_CHECKERLIST, True))
        assert e.settings.getProperties() == props

        e.settings.setRemovable(True)
        assert e.settings.isRemovable()
        props = ((SETTING_PROPERTY_REMOVABLE, True),
                 (SETTING_PROPERTY_READONLY, False),
                 (SETTING_PROPERTY_TRANSIENT, True),
                 (SETTING_PROPERTY_CHECKER, 'any'),
                 (SETTING_PROPERTY_CHECKERLIST, True))
        assert e.settings.getProperties() == props

    # repr
    def test_environmentMethod27(self):
        e = EnvironmentParameter("plop")
        assert repr(e) == "Environment, value:['plop']"

    # str
    def test_environmentMethod28(self):
        e = EnvironmentParameter("plop")
        assert str(e) == "['plop']"

    # test enableGlobal
    def test_environmentMethod29(self):
        e = EnvironmentParameter("plop")

        assert type(e.settings) is EnvironmentLocalSettings
        e.enableGlobal()
        assert type(e.settings) is EnvironmentGlobalSettings
        s = e.settings
        e.enableGlobal()
        assert e.settings is s

    # test enableLocal
    def test_environmentMethod30(self):
        e = EnvironmentParameter("plop")

        assert type(e.settings) is EnvironmentLocalSettings
        s = e.settings
        e.enableGlobal()
        assert type(e.settings) is EnvironmentGlobalSettings
        e.enableLocal()
        assert type(e.settings) is EnvironmentLocalSettings
        assert e.settings is not s
        s = e.settings
        e.enableLocal()
        assert e.settings is s

    def test_environmentMethod31(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=True,
                                     removable=True))
        e.enableGlobal()
        assert type(e.settings) is EnvironmentGlobalSettings
        assert e.settings.isReadOnly()
        assert e.settings.isRemovable()

    def test_environmentMethod32(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=False,
                                     removable=False))
        e.enableGlobal()
        assert type(e.settings) is EnvironmentGlobalSettings
        assert not e.settings.isReadOnly()
        assert not e.settings.isRemovable()

    def test_environmentMethod33(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=True,
                                     removable=True))
        e.enableGlobal()
        assert type(e.settings) is EnvironmentGlobalSettings
        e.enableLocal()
        assert type(e.settings) is EnvironmentLocalSettings

        assert e.settings.isReadOnly()
        assert e.settings.isRemovable()

    def test_environmentMethod34(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=False,
                                     removable=False))
        e.enableGlobal()
        assert type(e.settings) is EnvironmentGlobalSettings
        e.enableLocal()
        assert type(e.settings) is EnvironmentLocalSettings

        assert not e.settings.isReadOnly()
        assert not e.settings.isRemovable()

    def test_environmentMethod35(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=False,
                                     removable=False))
        h1 = hash(e)
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=False,
                                     removable=False))
        h2 = hash(e)

        assert h1 == h2

    def test_environmentMethod36(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=False,
                                     removable=False))
        h1 = hash(e)
        e = EnvironmentParameter("plip",
                                 settings=EnvironmentLocalSettings(
                                     read_only=False,
                                     removable=False))
        h2 = hash(e)

        assert h1 != h2

    def test_environmentMethod37(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=False,
                                     removable=False))
        h1 = hash(e)
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=True,
                                     removable=False))
        h2 = hash(e)

        assert h1 != h2

    def test_environmentMethod38(self):
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=False,
                                     removable=False))
        h1 = hash(e)
        e = EnvironmentParameter("plop",
                                 settings=EnvironmentLocalSettings(
                                     read_only=False,
                                     removable=True))
        h2 = hash(e)

        assert h1 != h2

    def test_clone(self):
        e = EnvironmentParameter(("plop",))
        e_clone = e.clone()

        assert e is not e_clone
        assert e.settings is not e_clone
        assert e.settings.checker is e_clone.settings.checker
        assert e.getValue() is not e_clone.getValue()
        assert e.getValue() == e_clone.getValue()
        assert hash(e.settings) == hash(e_clone.settings)
        assert hash(e) == hash(e_clone)
