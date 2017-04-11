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

from pyshell.addons.parameter import addValues
from pyshell.addons.parameter import cleanKeyStore
from pyshell.addons.parameter import createValue
from pyshell.addons.parameter import createValues
from pyshell.addons.parameter import getParameter
from pyshell.addons.parameter import getProperties
from pyshell.addons.parameter import getSelectedValue
from pyshell.addons.parameter import listParameter
from pyshell.addons.parameter import listProperties
from pyshell.addons.parameter import removeParameter
from pyshell.addons.parameter import selectValue
from pyshell.addons.parameter import setProperties
from pyshell.addons.parameter import setValue
from pyshell.addons.parameter import setValues
from pyshell.addons.parameter import statParameter
from pyshell.addons.parameter import subtractValues
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.system.manager.parent import ParentManager
from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.system.setting.environment import EnvironmentLocalSettings


class TestParameterAddon(object):
    def setup_method(self, method):
        self.managers = ParentManager()
        self.env = self.managers.getEnvironmentManager()
        self.local_param = self.env.setParameter("local",
                                                 "value",
                                                 local_param=True)
        self.global_param = self.env.setParameter("global",
                                                  "value",
                                                  local_param=False)

    def test_getParameterLocalAndExist(self):
        param = getParameter(key="local",
                             manager=self.env,
                             start_with_local=True,
                             explore_other_scope=False)

        assert param.getValue() == ["value"]

    def test_getParameterLocalAndNotExist(self):
        with pytest.raises(Exception):
            getParameter(key="titi",
                         manager=self.env,
                         start_with_local=True,
                         explore_other_scope=False)

    def test_getParameterGlobalAndExist(self):
        param = getParameter(key="global",
                             manager=self.env,
                             start_with_local=False,
                             explore_other_scope=False)

        assert param.getValue() == ["value"]

    def test_getParameterGlobalAndNotExist(self):
        with pytest.raises(Exception):
            getParameter(key="titi",
                         manager=self.env,
                         start_with_local=False,
                         explore_other_scope=False)

    def test_setPropertiesNoSetter(self):
        info = "setToto", "getToto", DefaultChecker.getArg()
        with pytest.raises(Exception):
            setProperties(key="local",
                          property_info=info,
                          property_value=42,
                          manager=self.env,
                          start_with_local=True,
                          explore_other_scope=False,
                          perfect_match=True)

    def test_setPropertiesValidCase(self):
        info = "setRemovable", "isRemovable", DefaultChecker.getBoolean()
        assert self.local_param.settings.isRemovable()
        setProperties(key="local",
                      property_info=info,
                      property_value=False,
                      manager=self.env,
                      start_with_local=True,
                      explore_other_scope=False,
                      perfect_match=True)
        assert not self.local_param.settings.isRemovable()

    def test_getPropertiesNoGetter(self):
        info = "setToto", "getToto", DefaultChecker.getArg()
        with pytest.raises(Exception):
            getProperties(key="local",
                          property_info=info,
                          manager=self.env,
                          start_with_local=True,
                          explore_other_scope=False,
                          perfect_match=True)

    def test_getPropertiesValidCase(self):
        info = "setRemovable", "isRemovable", DefaultChecker.getBoolean()
        assert self.local_param.settings.isRemovable()
        value = getProperties(key="local",
                              property_info=info,
                              manager=self.env,
                              start_with_local=True,
                              explore_other_scope=False,
                              perfect_match=True)
        assert value

    def test_listPropertiesLocal(self):
        result = listProperties(key="local",
                                manager=self.env,
                                start_with_local=True,
                                explore_other_scope=False,
                                perfect_match=True)
        assert len(result) is 5
        assert result[0] == ("Key", "Value",)
        assert ("checkerList", True,) in result
        assert ("readOnly", False,) in result
        assert ("checker", "any",) in result
        assert ("removable", True,) in result

    def test_listPropertiesGlobal(self):
        result = listProperties(key="global",
                                manager=self.env,
                                start_with_local=False,
                                explore_other_scope=False,
                                perfect_match=True)
        assert len(result) is 6
        assert result[0] == ("Key", "Value",)
        assert ("checkerList", True,) in result
        assert ("readOnly", False,) in result
        assert ("transient", False,) in result
        assert ("checker", "any",) in result
        assert ("removable", True,) in result

    def test_removeParameterDoesNotExist(self):
        removeParameter(key="titi",
                        manager=self.env,
                        start_with_local=True,
                        explore_other_scope=False)

    def test_removeParameterExists(self):
        removeParameter(key="local",
                        manager=self.env,
                        start_with_local=True,
                        explore_other_scope=False)

        assert not self.env.hasParameter("local",
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False)

    def test_listParameterEmpty(self):
        output = listParameter(manager=self.managers.getContextManager(),
                               key=None,
                               start_with_local=True,
                               explore_other_scope=True)
        assert len(output) is 1
        assert "No item available" in output[0]

    def test_listParameterListTypeParameter(self):
        output = listParameter(manager=self.env,
                               key=None,
                               start_with_local=True,
                               explore_other_scope=False)
        assert len(output) is 2
        assert len(output[0]) is 2
        assert "Name" in output[0][0]
        assert "Value" in output[0][1]
        assert len(output[1]) is 2
        assert "local" in output[1][0]
        assert "value" == output[1][1]

    def test_listParameterNotAListTypeParameter(self):
        settings = EnvironmentLocalSettings(read_only=False,
                                            removable=True,
                                            checker=DefaultChecker.getString())
        parameter = EnvironmentParameter("titi", settings)
        self.local_param = self.env.setParameter("local",
                                                 parameter,
                                                 local_param=True)
        output = listParameter(manager=self.env,
                               key=None,
                               start_with_local=True,
                               explore_other_scope=False)
        assert len(output) is 2
        assert len(output[0]) is 2
        assert "Name" in output[0][0]
        assert "Value" in output[0][1]
        assert len(output[1]) is 2
        assert "local" in output[1][0]
        assert "titi" == output[1][1]

    def test_statEmpty(self):
        output = statParameter(manager=self.managers.getContextManager(),
                               key=None,
                               start_with_local=True,
                               explore_other_scope=True)

        assert len(output) is 1
        assert "No item available" in output[0]

    def test_statLocal(self):
        output = statParameter(manager=self.env,
                               key=None,
                               start_with_local=True,
                               explore_other_scope=False)
        assert len(output) is 2
        assert len(output[0]) is 6
        assert "Name" in output[0][0]
        assert "Scope" in output[0][1]
        assert "checker" in output[0][2]
        assert "checkerList" in output[0][3]
        assert "readOnly" in output[0][4]
        assert "removable" in output[0][5]

        assert len(output[1]) is 6
        assert "local" in output[1][0]
        assert "local" in output[1][1]
        assert "any" in output[1][2]
        assert "True" in output[1][3]
        assert "False" in output[1][4]
        assert "True" in output[1][5]

    def test_statGlobal(self):
        output = statParameter(manager=self.env,
                               key=None,
                               start_with_local=False,
                               explore_other_scope=False)
        assert len(output) is 2
        assert len(output[0]) is 7
        assert "Name" in output[0][0]
        assert "Scope" in output[0][1]
        assert "checker" in output[0][2]
        assert "checkerList" in output[0][3]
        assert "readOnly" in output[0][4]
        assert "removable" in output[0][5]
        assert "transient" in output[0][6]

        assert len(output[1]) is 7
        assert "global" in output[1][0]
        assert "global" in output[1][1]
        assert "any" in output[1][2]
        assert "True" in output[1][3]
        assert "False" in output[1][4]
        assert "True" in output[1][5]
        assert "False" in output[1][6]

    def test_statAll(self):
        output = statParameter(manager=self.env,
                               key=None,
                               start_with_local=True,
                               explore_other_scope=True)
        assert len(output) is 3
        assert len(output[0]) is 7
        assert "Name" in output[0][0]
        assert "Scope" in output[0][1]
        assert "checker" in output[0][2]
        assert "checkerList" in output[0][3]
        assert "readOnly" in output[0][4]
        assert "removable" in output[0][5]
        assert "transient" in output[0][6]

        assert len(output[1]) is 7
        assert "global" in output[1][0]
        assert "global" in output[1][1]
        assert "any" in output[1][2]
        assert "True" in output[1][3]
        assert "False" in output[1][4]
        assert "True" in output[1][5]
        assert "False" in output[1][6]

        assert len(output[2]) is 7
        assert "local" in output[2][0]
        assert "local" in output[2][1]
        assert "any" in output[2][2]
        assert "True" in output[2][3]
        assert "False" in output[2][4]
        assert "True" in output[2][5]
        assert "-" in output[2][6]

    def test_statAllWithSameName(self):
        self.global_param = self.env.setParameter("global",
                                                  "value",
                                                  local_param=True)

        output = statParameter(manager=self.env,
                               key=None,
                               start_with_local=True,
                               explore_other_scope=True)
        assert len(output) is 3
        assert len(output[0]) is 6
        assert "Name" in output[0][0]
        assert "Scope" in output[0][1]
        assert "checker" in output[0][2]
        assert "checkerList" in output[0][3]
        assert "readOnly" in output[0][4]
        assert "removable" in output[0][5]

        assert len(output[1]) is 6
        assert "global" in output[1][0]
        assert "local" in output[1][1]
        assert "any" in output[1][2]
        assert "True" in output[1][3]
        assert "False" in output[1][4]
        assert "True" in output[1][5]

        assert len(output[2]) is 6
        assert "local" in output[2][0]
        assert "local" in output[2][1]
        assert "any" in output[2][2]
        assert "True" in output[2][3]
        assert "False" in output[2][4]
        assert "True" in output[2][5]

    def test_subtractValues(self):
        values = ("uu", "ii", "oo", "aa",)
        parameter = EnvironmentParameter(values)
        self.local_param = self.env.setParameter("local",
                                                 parameter,
                                                 local_param=True)

        subtractValues(key="local",
                       values=("ii", "yy",),
                       manager=self.env,
                       start_with_local=True,
                       explore_other_scope=False)
        assert tuple(parameter.getValue()) == ("uu", "oo", "aa",)

    def test_addValues(self):
        values = ("uu", "oo", "aa",)
        parameter = EnvironmentParameter(values)
        self.local_param = self.env.setParameter("local",
                                                 parameter,
                                                 local_param=True)
        addValues(key="local",
                  values=("ii", "aa",),
                  manager=self.env,
                  start_with_local=True,
                  explore_other_scope=False)

        assert tuple(parameter.getValue()) == ("uu", "oo", "aa", "ii", "aa",)

    def test_createValuesNoListWithEmptyValue(self):
        with pytest.raises(Exception):
            createValues(value_type=DefaultChecker.getArg(),
                         key="creates_value",
                         values=(),
                         manager=self.env,
                         list_enabled=False,
                         local_param=True,)

    def test_createValuesNoListSuccess(self):
        createValues(value_type=DefaultChecker.getString(),
                     key="creates_value",
                     values=("toto", "titi", "tata"),
                     manager=self.env,
                     list_enabled=False,
                     local_param=True,)
        assert self.env.hasParameter("creates_value",
                                     perfect_match=True,
                                     local_param=True,
                                     explore_other_scope=False)
        param = self.env.getParameter(string_path="creates_value",
                                      perfect_match=True,
                                      local_param=True,
                                      explore_other_scope=False)
        assert param.getValue() == "toto"
        assert not isinstance(param.settings.getChecker(), ListArgChecker)
        assert param.settings.getChecker() is DefaultChecker.getString()

    def test_createValuesListSuccess(self):
        createValues(value_type=DefaultChecker.getInteger(),
                     key="creates_value",
                     values=(11, 22, 33,),
                     manager=self.env,
                     list_enabled=True,
                     local_param=True,)
        assert self.env.hasParameter("creates_value",
                                     perfect_match=True,
                                     local_param=True,
                                     explore_other_scope=False)
        param = self.env.getParameter(string_path="creates_value",
                                      perfect_match=True,
                                      local_param=True,
                                      explore_other_scope=False)
        assert param.getValue() == [11, 22, 33]
        assert isinstance(param.settings.getChecker(), ListArgChecker)
        def_int = DefaultChecker.getInteger()
        assert param.settings.getChecker().checker is def_int

    def test_createValuesNoListNoTypeSuccess(self):
        createValues(value_type=None,
                     key="creates_value",
                     values=("toto", "titi", "tata"),
                     manager=self.env,
                     list_enabled=False,
                     local_param=True,)
        assert self.env.hasParameter("creates_value",
                                     perfect_match=True,
                                     local_param=True,
                                     explore_other_scope=False)
        param = self.env.getParameter(string_path="creates_value",
                                      perfect_match=True,
                                      local_param=True,
                                      explore_other_scope=False)
        assert param.getValue() == "toto"
        assert not isinstance(param.settings.getChecker(), ListArgChecker)
        assert param.settings.getChecker() is DefaultChecker.getArg()

    def test_createValuesListNoTypeSuccess(self):
        createValues(value_type=None,
                     key="creates_value",
                     values=(11, 22, 33,),
                     manager=self.env,
                     list_enabled=True,
                     local_param=True,)
        assert self.env.hasParameter("creates_value",
                                     perfect_match=True,
                                     local_param=True,
                                     explore_other_scope=False)
        param = self.env.getParameter(string_path="creates_value",
                                      perfect_match=True,
                                      local_param=True,
                                      explore_other_scope=False)
        assert param.getValue() == [11, 22, 33]
        assert isinstance(param.settings.getChecker(), ListArgChecker)
        assert param.settings.getChecker().checker is DefaultChecker.getArg()

    def test_createValueNoType(self):
        createValue(value_type=None,
                    key="create_value",
                    value="titi",
                    manager=self.env,
                    local_param=True,)
        assert self.env.hasParameter("create_value",
                                     perfect_match=True,
                                     local_param=True,
                                     explore_other_scope=False)
        param = self.env.getParameter(string_path="create_value",
                                      perfect_match=True,
                                      local_param=True,
                                      explore_other_scope=False)
        assert param.getValue() == "titi"
        assert not isinstance(param.settings.getChecker(), ListArgChecker)
        assert param.settings.getChecker() is DefaultChecker.getArg()

    def test_createValueType(self):
        createValue(value_type=DefaultChecker.getString(),
                    key="create_value",
                    value="toto",
                    manager=self.env,
                    local_param=True)
        assert self.env.hasParameter("create_value",
                                     perfect_match=True,
                                     local_param=True,
                                     explore_other_scope=False)
        param = self.env.getParameter(string_path="create_value",
                                      perfect_match=True,
                                      local_param=True,
                                      explore_other_scope=False)
        assert param.getValue() == "toto"
        assert not isinstance(param.settings.getChecker(), ListArgChecker)
        assert param.settings.getChecker() is DefaultChecker.getString()

    def test_setValuesOnListParameter(self):
        createValues(value_type=None,
                     key="set_values",
                     values=(11, 22, 33,),
                     manager=self.env,
                     list_enabled=True,
                     local_param=True,)
        setValues(key="set_values",
                  values=(44, 55, 66,),
                  manager=self.env,
                  start_with_local=True,
                  explore_other_scope=False)

        assert self.env.hasParameter("set_values",
                                     perfect_match=True,
                                     local_param=True,
                                     explore_other_scope=False)
        param = self.env.getParameter(string_path="set_values",
                                      perfect_match=True,
                                      local_param=True,
                                      explore_other_scope=False)
        assert param.getValue() == [44, 55, 66]
        assert isinstance(param.settings.getChecker(), ListArgChecker)
        assert param.settings.getChecker().checker is DefaultChecker.getArg()

    def test_setValuesNotOnListParameterWithNoValue(self):
        createValues(value_type=None,
                     key="set_values",
                     values=("toto", "titi", "tata"),
                     manager=self.env,
                     list_enabled=False,
                     local_param=True,)

        with pytest.raises(Exception):
            setValues(key="set_values",
                      values=(),
                      manager=self.env,
                      start_with_local=True,
                      explore_other_scope=False)

    def test_setValuesNotOnListParameter(self):
        createValues(value_type=None,
                     key="set_values",
                     values=("toto", "titi", "tata"),
                     manager=self.env,
                     list_enabled=False,
                     local_param=True,)

        setValues(key="set_values",
                  values=("tutu", "tyty",),
                  manager=self.env,
                  start_with_local=True,
                  explore_other_scope=False)

        assert self.env.hasParameter("set_values",
                                     perfect_match=True,
                                     local_param=True,
                                     explore_other_scope=False)
        param = self.env.getParameter(string_path="set_values",
                                      perfect_match=True,
                                      local_param=True,
                                      explore_other_scope=False)

        assert param.getValue() == "tutu"
        assert not isinstance(param.settings.getChecker(), ListArgChecker)
        assert param.settings.getChecker() is DefaultChecker.getArg()

    def test_setValue(self):
        createValue(value_type=DefaultChecker.getString(),
                    key="set_value",
                    value="toto",
                    manager=self.env,
                    local_param=True)

        setValue(key="set_value",
                 value="plip",
                 manager=self.env,
                 start_with_local=True,
                 explore_other_scope=False)

        assert self.env.hasParameter("set_value",
                                     perfect_match=True,
                                     local_param=True,
                                     explore_other_scope=False)
        param = self.env.getParameter(string_path="set_value",
                                      perfect_match=True,
                                      local_param=True,
                                      explore_other_scope=False)

        assert param.getValue() == "plip"
        assert not isinstance(param.settings.getChecker(), ListArgChecker)
        assert param.settings.getChecker() is DefaultChecker.getString()

    def test_selectValue(self):
        con = self.managers.getContextManager()
        createValues(value_type=None,
                     key="selectValue",
                     values=("toto", "titi", "tata"),
                     manager=con,
                     list_enabled=True,
                     local_param=True,)

        assert con.hasParameter("selectValue",
                                perfect_match=True,
                                local_param=True,
                                explore_other_scope=False)

        param = con.getParameter(string_path="selectValue",
                                 perfect_match=True,
                                 local_param=True,
                                 explore_other_scope=False)

        assert param.getSelectedValue() == "toto"

        selectValue(key="selectValue",
                    value="tata",
                    manager=con,
                    start_with_local=True,
                    explore_other_scope=False)

        assert param.getSelectedValue() == "tata"

    def test_getSelectedValue(self):
        con = self.managers.getContextManager()
        createValues(value_type=None,
                     key="selectValue",
                     values=("toto", "titi", "tata"),
                     manager=con,
                     list_enabled=True,
                     local_param=True,)

        value = getSelectedValue(key="selectValue",
                                 manager=con,
                                 start_with_local=True,
                                 explore_other_scope=False)

        assert value == "toto"

    def test_cleanKeyStoreAllNoKey(self):
        keys = self.managers.getKeyManager()
        cleanKeyStore(manager=keys, remove_locals=True, remove_globals=True)

    def test_cleanKeyStoreAll(self):
        keys = self.managers.getKeyManager()
        createValue(value_type=None,
                    key="local_key",
                    value="0x112233",
                    manager=keys,
                    local_param=True)
        createValue(value_type=None,
                    key="global_key",
                    value="0b00110011",
                    manager=keys,
                    local_param=False)

        cleanKeyStore(manager=keys, remove_locals=True, remove_globals=True)

        assert not keys.hasParameter("local_key",
                                     perfect_match=True,
                                     local_param=True,
                                     explore_other_scope=False)
        assert not keys.hasParameter("global_key",
                                     perfect_match=True,
                                     local_param=False,
                                     explore_other_scope=True)

    def test_cleanKeyStoreLocalNoKey(self):
        keys = self.managers.getKeyManager()
        cleanKeyStore(manager=keys, remove_locals=True, remove_globals=False)

    def test_cleanKeyStoreLocal(self):
        keys = self.managers.getKeyManager()
        createValue(value_type=None,
                    key="local_key",
                    value="0x112233",
                    manager=keys,
                    local_param=True)
        createValue(value_type=None,
                    key="global_key",
                    value="0b00110011",
                    manager=keys,
                    local_param=False)

        cleanKeyStore(manager=keys, remove_locals=True, remove_globals=False)

        assert not keys.hasParameter("local_key",
                                     perfect_match=True,
                                     local_param=True,
                                     explore_other_scope=False)
        assert keys.hasParameter("global_key",
                                 perfect_match=True,
                                 local_param=False,
                                 explore_other_scope=True)

    def test_cleanKeyStoreGlobalNoKey(self):
        keys = self.managers.getKeyManager()
        cleanKeyStore(manager=keys, remove_locals=False, remove_globals=True)

    def test_cleanKeyStoreGlobal(self):
        keys = self.managers.getKeyManager()
        createValue(value_type=None,
                    key="local_key",
                    value="0x112233",
                    manager=keys,
                    local_param=True)
        createValue(value_type=None,
                    key="global_key",
                    value="0b00110011",
                    manager=keys,
                    local_param=False)

        cleanKeyStore(manager=keys, remove_locals=False, remove_globals=True)

        assert keys.hasParameter("local_key",
                                 perfect_match=True,
                                 local_param=True,
                                 explore_other_scope=False)
        assert not keys.hasParameter("global_key",
                                     perfect_match=True,
                                     local_param=False,
                                     explore_other_scope=True)
