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

from pyshell.arg.argchecker import ArgChecker
from pyshell.arg.argchecker import EnvironmentParameterChecker
from pyshell.arg.argchecker import IntegerArgChecker
from pyshell.arg.argchecker import ListArgChecker
from pyshell.arg.argchecker import StringArgChecker
from pyshell.arg.exception import ArgException
from pyshell.arg.exception import ArgInitializationException
from pyshell.system.context import ContextParameter
from pyshell.system.context import ContextParameterManager
from pyshell.system.context import GlobalContextSettings
from pyshell.system.context import LocalContextSettings
from pyshell.system.context import _convertToSetList
from pyshell.system.environment import EnvironmentParameter
from pyshell.utils.exception import ParameterException


class TestContext(object):
    # # misc # #

    def test_convertToSetList(self):
        converted = _convertToSetList(("aaa", "bbb", "aaa", "ccc", "ccc"))
        assert converted == ["aaa", "bbb", "ccc"]

    # # manager # #

    def test_manager1(self):
        assert ContextParameterManager() is not None

    # try to set valid value
    def test_manager2(self):
        manager = ContextParameterManager()
        param = manager.setParameter("context.test", ("plop",))
        assert param.getSelectedValue() == "plop"
        assert param.getValue() == ["plop"]

    # try to set valid parameter
    def test_manager3(self):
        manager = ContextParameterManager()
        param = manager.setParameter("context.test",
                                     ContextParameter(("plop",)))
        assert param.getSelectedValue() == "plop"
        assert param.getValue() == ["plop"]

    # try to set invalid parameter
    def test_manager4(self):
        manager = ContextParameterManager()
        with pytest.raises(ParameterException):
            manager.setParameter("test.var", EnvironmentParameter("0x1122ff"))

    # # ContextSettings and LocalContextSettings # #

    def test_localSettings1(self):
        lcs = LocalContextSettings(read_only=False, removable=False)
        assert not lcs.isReadOnly()
        assert not lcs.isRemovable()

    def test_localSettings2(self):
        lcs = LocalContextSettings(read_only=True, removable=True)
        assert lcs.isReadOnly()
        assert lcs.isRemovable()

    # setIndex with correct value
    def test_localSettings3(self):
        c = ContextParameter((0, 1, 2, 3,),
                             typ=IntegerArgChecker(),
                             default_index=2,
                             index=1)
        assert c.getSelectedValue() == 1
        c.settings.setIndex(2)
        assert c.getSelectedValue() == 2

    # setIndex with incorrect value
    def test_localSettings4(self):
        c = ContextParameter((0, 1, 2, 3,),
                             typ=IntegerArgChecker(),
                             default_index=2,
                             index=1)
        assert c.getSelectedValue() == 1
        with pytest.raises(ParameterException):
            c.settings.setIndex(23)

    # setIndex with invalid value
    def test_localSettings5(self):
        c = ContextParameter((0, 1, 2, 3,),
                             typ=IntegerArgChecker(),
                             default_index=2,
                             index=1)
        assert c.getSelectedValue() == 1
        with pytest.raises(ParameterException):
            c.settings.setIndex("plop")

    # setIndex with valid value and readonly
    def test_localSettings6(self):
        settings = LocalContextSettings(read_only=True)
        c = ContextParameter((0, 1, 2, 3,),
                             typ=IntegerArgChecker(),
                             settings=settings)

        assert c.getSelectedValue() == 0
        c.settings.setIndex(2)
        assert c.getSelectedValue() == 2

    # tryToSetIndex with correct value
    def test_localSettings7(self):
        c = ContextParameter((0, 1, 2, 3,),
                             typ=IntegerArgChecker(),
                             default_index=2)
        assert c.getSelectedValue() == 0
        c.settings.tryToSetIndex(3)
        assert c.getSelectedValue() == 3

    # tryToSetIndex with incorrect value
    def test_localSettings8(self):
        c = ContextParameter((0, 1, 2, 3,),
                             typ=IntegerArgChecker(),
                             default_index=2)
        assert c.getSelectedValue() == 0
        c.settings.tryToSetIndex(23)
        assert c.getSelectedValue() == 0

    # tryToSetIndex with invalid value
    def test_localSettings9(self):
        c = ContextParameter((0, 1, 2, 3,),
                             typ=IntegerArgChecker(),
                             default_index=2)
        assert c.getSelectedValue() == 0
        c.settings.tryToSetIndex("plop")
        assert c.getSelectedValue() == 0

    # tryToSetIndex with incorrect value and default value recomputing
    def test_localSettings10(self):
        c = ContextParameter((0, 1, 2, 3,),
                             typ=IntegerArgChecker(),
                             default_index=2,
                             index=1)
        assert c.getSelectedValue() == 1
        c.default_index = 45
        c.settings.tryToSetIndex(80)
        assert c.getSelectedValue() == 1

    # tryToSetIndex with valid value and readonly
    def test_localSettings11(self):
        settings = LocalContextSettings(read_only=True)
        c = ContextParameter((0, 1, 2, 3,),
                             typ=IntegerArgChecker(),
                             default_index=2,
                             settings=settings)
        assert c.getSelectedValue() == 0
        c.settings.tryToSetIndex(3)
        assert c.getSelectedValue() == 3

    # tryToSetIndex, create a test to set default_index
    def test_localSettings12(self):
        c = ContextParameter((0, 1, 2, 3,),
                             typ=IntegerArgChecker(),
                             index=3,
                             default_index=1)
        assert c.getSelectedValue() == 3
        EnvironmentParameter.setValue(c, (11, 22, 33,))
        c.settings.tryToSetIndex(23)
        assert c.getSelectedValue() == 22

    # setIndexValue with a valid value
    def test_localSettings13(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",), typ=StringArgChecker())
        assert c.getSelectedValue() == "aa"
        c.settings.setIndexValue("cc")
        assert c.getSelectedValue() == "cc"

    # setIndexValue with a valid value but inexisting
    def test_localSettings14(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",), typ=StringArgChecker())
        assert c.getSelectedValue() == "aa"
        with pytest.raises(ParameterException):
            c.settings.setIndexValue("ee")

    # setIndexValue with an invalid value
    def test_localSettings15(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",), typ=StringArgChecker())
        assert c.getSelectedValue() == "aa"
        with pytest.raises(ParameterException):
            c.settings.setIndexValue(object())

    # setIndexValue with valid value and readonly
    def test_localSettings16(self):
        settings = LocalContextSettings(read_only=True)
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             settings=settings)
        assert c.getSelectedValue() == "aa"
        c.settings.setIndexValue("cc")
        assert c.getSelectedValue() == "cc"

    # setDefaultIndex with correct value
    def test_localSettings17(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             default_index=2)
        assert c.settings.getDefaultIndex() == 2
        c.settings.setDefaultIndex(1)
        assert c.settings.getDefaultIndex() == 1

    # setDefaultIndex with incorrect value
    def test_localSettings18(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             default_index=2)
        with pytest.raises(ParameterException):
            c.settings.setDefaultIndex(23)

    # setDefaultIndex with invalid value
    def test_localSettings19(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             default_index=2)
        with pytest.raises(ParameterException):
            c.settings.setDefaultIndex("plop")

    # setDefaultIndex with valid value and readonly
    def test_localSettings20(self):
        settings = LocalContextSettings(read_only=True)
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             default_index=2,
                             settings=settings)
        with pytest.raises(ParameterException):
            c.settings.setDefaultIndex(1)

    # tryToSetDefaultIndex with correct value
    def test_localSettings21(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             default_index=2)
        assert c.settings.getDefaultIndex() == 2
        c.settings.tryToSetDefaultIndex(1)
        assert c.settings.getDefaultIndex() == 1

    # tryToSetDefaultIndex with incorrect value
    def test_localSettings22(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             default_index=2)
        assert c.settings.getDefaultIndex() == 2
        c.settings.tryToSetDefaultIndex(100)
        assert c.settings.getDefaultIndex() == 2

    # tryToSetDefaultIndex with invalid value
    def test_localSettings23(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(), default_index=2)
        assert c.settings.getDefaultIndex() == 2
        c.settings.tryToSetDefaultIndex("toto")
        assert c.settings.getDefaultIndex() == 2

    # tryToSetDefaultIndex with valid value and readonly
    def test_localSettings24(self):
        settings = LocalContextSettings(read_only=True)
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             default_index=2,
                             settings=settings)
        with pytest.raises(ParameterException):
            c.settings.tryToSetDefaultIndex(1)

    # tryToSetDefaultIndex, create a test to set default_index to zero
    def test_localSettings25(self):
        c = ContextParameter((0, 1, 2, 3,),
                             typ=IntegerArgChecker(),
                             default_index=3)
        assert c.settings.getDefaultIndex() == 3
        EnvironmentParameter.setValue(c, (11, 22, 33,))
        c.settings.tryToSetDefaultIndex(23)
        assert c.settings.getDefaultIndex() == 0

    # test reset
    def test_localSettings26(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             default_index=2,
                             index=1)
        assert c.settings.getDefaultIndex() == 2
        assert c.settings.getIndex() == 1
        c.settings.reset()
        assert c.settings.getDefaultIndex() == 2
        assert c.settings.getIndex() == 2

    # test getProperties
    def test_localSettings27(self):
        settings = LocalContextSettings(removable=False, read_only=True)
        c = ContextParameter((0, 1, 2, 3,),
                             index=2,
                             default_index=3,
                             settings=settings)
        assert c.settings.getProperties() == (('removable', False),
                                              ('readOnly', True),
                                              ('transient', True),
                                              ('transientIndex', True),
                                              ('defaultIndex', 3))

    # # GlobalContextSettings # #

    # __init__ test each properties, True
    def test_globalSettings1(self):
        settings = GlobalContextSettings(read_only=True,
                                         removable=True,
                                         transient=True,
                                         transient_index=True)
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             settings=settings)
        assert c.settings.isReadOnly()
        assert c.settings.isRemovable()
        assert c.settings.isTransient()
        assert c.settings.isTransientIndex()

    # __init__ test each properties, False
    def test_globalSettings2(self):
        settings = GlobalContextSettings(read_only=False,
                                         removable=False,
                                         transient=False,
                                         transient_index=False)
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             settings=settings)
        assert not c.settings.isReadOnly()
        assert not c.settings.isRemovable()
        assert not c.settings.isTransient()
        assert not c.settings.isTransientIndex()

    # test setTransientIndex in readonly mode
    def test_globalSettings3(self):
        settings = GlobalContextSettings(read_only=True)
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             settings=settings)
        with pytest.raises(ParameterException):
            c.settings.setTransientIndex(True)

    # test setTransientIndex with invalid bool
    def test_globalSettings4(self):
        settings = GlobalContextSettings()
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             settings=settings)
        with pytest.raises(ParameterException):
            c.settings.setTransientIndex("plop")

    # test setTransientIndex with valid bool
    def test_globalSettings5(self):
        settings = GlobalContextSettings()
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             settings=settings)
        assert not c.settings.isTransientIndex()
        c.settings.setTransientIndex(True)
        assert c.settings.isTransientIndex()

    # test getProperties not transient index
    def test_globalSettings6(self):
        settings = GlobalContextSettings(transient_index=False)
        c = ContextParameter((0, 1, 2, 3,),
                             index=2,
                             default_index=3,
                             settings=settings)
        assert c.settings.getProperties() == (('removable', True),
                                              ('readOnly', False),
                                              ('transient', False),
                                              ('transientIndex', False),
                                              ('defaultIndex', 3),
                                              ('index', 2))

    # test getProperties transient index
    def test_globalSettings7(self):
        settings = GlobalContextSettings(transient_index=True)
        c = ContextParameter((0, 1, 2, 3,),
                             index=2,
                             default_index=3,
                             settings=settings)
        assert c.settings.getProperties() == (('removable', True),
                                              ('readOnly', False),
                                              ('transient', False),
                                              ('transientIndex', True),
                                              ('defaultIndex', 3))

    # # parameter # #

    # on constructor
    # None typ
    def test_contextConstructor1(self):
        c = ContextParameter(("toto",), typ=None)
        assert isinstance(c.typ, ListArgChecker)
        assert c.typ.minimum_size == 1
        assert c.typ.maximum_size is None

        assert c.typ.checker.__class__.__name__ == ArgChecker.__name__
        assert isinstance(c.typ.checker, ArgChecker)

    # arg typ
    def test_contextConstructor2(self):
        c = ContextParameter((0,), typ=IntegerArgChecker())
        assert isinstance(c.typ, ListArgChecker)
        assert c.typ.minimum_size == 1
        assert c.typ.maximum_size is None

        assert isinstance(c.typ.checker, IntegerArgChecker)

    # arg typ with min size of 0
    def test_contextConstructor2b(self):
        with pytest.raises(ArgInitializationException):
            ContextParameter(("plop", ), EnvironmentParameterChecker("plip"))

    # list typ + #list typ with size not adapted to context
    def test_contextConstructor3(self):
        lt = ListArgChecker(IntegerArgChecker(), 3, 27)
        c = ContextParameter((0,), typ=lt)
        assert isinstance(c.typ, ListArgChecker)
        assert c.typ.minimum_size == 1
        assert c.typ.maximum_size == 27
        assert isinstance(c.typ.checker, IntegerArgChecker)

    # test valid index
    def test_contextConstructor5(self):
        c = ContextParameter((0, 1, 2, 3,), index=1)
        assert c.settings.getIndex() == 1

    # test invalid index
    def test_contextConstructor6(self):
        c = ContextParameter((0, 1, 2, 3,), index=23)
        assert c.settings.getIndex() == 0

    # test valid default index
    def test_contextConstructor7(self):
        c = ContextParameter((0, 1, 2, 3,), default_index=1)
        assert c.settings.getDefaultIndex() == 1

    # test invalid default index
    def test_contextConstructor8(self):
        c = ContextParameter((0, 1, 2, 3,), default_index=42)
        assert c.settings.getDefaultIndex() == 0

    # test both invalid index AND invalid default index
    def test_contextConstructor9(self):
        c = ContextParameter((0, 1, 2, 3,), index=23, default_index=42)
        assert c.settings.getDefaultIndex() == 0
        assert c.settings.getIndex() == 0

    # test transientIndex
    def test_contextConstructor10(self):
        settings = GlobalContextSettings(transient_index=False)
        c = ContextParameter((0, 1, 2, 3,), index=2, settings=settings)
        assert not c.settings.isTransientIndex()
        assert c.settings.getProperties() == (('removable', True),
                                              ('readOnly', False),
                                              ('transient', False),
                                              ('transientIndex', False),
                                              ('defaultIndex', 0),
                                              ('index', 2))

        settings = GlobalContextSettings(transient_index=True)
        c = ContextParameter((0, 1, 2, 3,), index=2, settings=settings)
        assert c.settings.isTransientIndex()
        assert c.settings.getProperties() == (('removable', True),
                                              ('readOnly', False),
                                              ('transient', False),
                                              ('transientIndex', True),
                                              ('defaultIndex', 0))

    # test method

    # setValue with valid value
    def test_context1(self):
        c = ContextParameter((0,), typ=IntegerArgChecker())
        c.setValue((1, 2, 3, "4",))
        assert c.getValue() == [1, 2, 3, 4, ]

    # setValue with invalid value
    def test_context2(self):
        c = ContextParameter((0,), typ=IntegerArgChecker())
        with pytest.raises(ArgException):
            c.setValue((1, 2, 3, "plop",))

    # test addValues to add valid
    def test_context3(self):
        c = ContextParameter((0, 1, 2, 3,), typ=IntegerArgChecker())
        c.addValues((4, 5, 6,))
        assert c.getValue() == [0, 1, 2, 3, 4, 5, 6]

    # test addValues to add invalid value
    def test_context4(self):
        c = ContextParameter((0, 1, 2, 3,), typ=IntegerArgChecker())
        with pytest.raises(ArgException):
            c.addValues((4, 5, "plop",))

    # removeValues, remove all value
    def test_context5(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",), typ=StringArgChecker())
        with pytest.raises(ParameterException):
            c.removeValues(("aa", "bb", "cc", "dd",))

    # removeValues, remove unexisting value
    def test_context6(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",), typ=StringArgChecker())
        assert c.getValue() == ["aa", "bb", "cc", "dd"]
        c.removeValues(("aa", "aa", "ee", "ff",))
        assert c.getValue() == ["bb", "cc", "dd"]

    # removeValues, try to remove with read only
    def test_context7(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             settings=LocalContextSettings(read_only=True))
        assert c.getValue() == ["aa", "bb", "cc", "dd"]
        with pytest.raises(ParameterException):
            c.removeValues(("aa", "aa", "ee", "ff",))

    # removeValues, success remove
    def test_context8(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",), typ=StringArgChecker())
        assert c.getValue() == ["aa", "bb", "cc", "dd"]
        c.removeValues(("aa",))
        assert c.getValue() == ["bb", "cc", "dd"]

    # removeValues, success remove with index computation
    def test_context9(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             default_index=2,
                             index=3)
        assert c.getValue() == ["aa", "bb", "cc", "dd"]
        assert c.settings.getDefaultIndex() == 2
        assert c.settings.getIndex() == 3
        c.removeValues(("cc", "dd",))
        assert c.getValue() == ["aa", "bb"]
        assert c.settings.getDefaultIndex() == 0
        assert c.settings.getIndex() == 0

    # test repr
    def test_context10(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             default_index=2,
                             index=1)
        assert repr(c) == ("Context, available values: "
                           "['aa', 'bb', 'cc', 'dd'], selected index: 1, "
                           "selected value: bb")

    # test str
    def test_context11(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             typ=StringArgChecker(),
                             default_index=2,
                             index=1)
        assert str(c) == "bb"

    # test enableGlobal
    def test_context12(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",))

        assert isinstance(c.settings, LocalContextSettings)
        c.enableGlobal()
        assert isinstance(c.settings, GlobalContextSettings)
        s = c.settings
        c.enableGlobal()
        assert c.settings is s

    # test enableLocal
    def test_context13(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",))

        assert isinstance(c.settings, LocalContextSettings)
        s = c.settings
        c.enableGlobal()
        assert isinstance(c.settings, GlobalContextSettings)
        c.enableLocal()
        assert isinstance(c.settings, LocalContextSettings)
        assert c.settings is not s
        s = c.settings
        c.enableLocal()
        assert c.settings is s

    def test_context14(self):
        settings = LocalContextSettings(read_only=True, removable=True)
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             settings=settings,
                             index=2,
                             default_index=3)
        c.enableGlobal()
        assert isinstance(c.settings, GlobalContextSettings)
        assert c.settings.isReadOnly()
        assert c.settings.isRemovable()
        assert c.settings.getIndex() == 2
        assert c.settings.getDefaultIndex() == 3

    def test_context15(self):
        settings = LocalContextSettings(read_only=False, removable=False)
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             settings=settings,
                             index=3,
                             default_index=2)
        c.enableGlobal()
        assert isinstance(c.settings, GlobalContextSettings)
        assert not c.settings.isReadOnly()
        assert not c.settings.isRemovable()
        assert c.settings.getIndex() == 3
        assert c.settings.getDefaultIndex() == 2

    def test_context16(self):
        settings = LocalContextSettings(read_only=True, removable=True)
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             settings=settings,
                             index=2,
                             default_index=3)
        c.enableGlobal()
        assert isinstance(c.settings, GlobalContextSettings)
        c.enableLocal()
        assert isinstance(c.settings, LocalContextSettings)

        assert c.settings.isReadOnly()
        assert c.settings.isRemovable()
        assert c.settings.getIndex() == 2
        assert c.settings.getDefaultIndex() == 3

    def test_context17(self):
        settings = LocalContextSettings(read_only=False, removable=False)
        c = ContextParameter(("aa", "bb", "cc", "dd",),
                             settings=settings,
                             index=3,
                             default_index=2)
        c.enableGlobal()
        assert isinstance(c.settings, GlobalContextSettings)
        c.enableLocal()
        assert isinstance(c.settings, LocalContextSettings)

        assert not c.settings.isReadOnly()
        assert not c.settings.isRemovable()
        assert c.settings.getIndex() == 3
        assert c.settings.getDefaultIndex() == 2

    def test_clone(self):
        c = ContextParameter(("aa", "bb", "cc", "dd",))
        c_clone = c.clone()

        assert c is not c_clone
        assert c.settings is not c_clone
        assert c.typ is c_clone.typ
        assert c.getValue() is not c_clone.getValue()
        assert c.getValue() == c_clone.getValue()
        assert hash(c.settings) == hash(c_clone.settings)
        assert hash(c) == hash(c_clone)
