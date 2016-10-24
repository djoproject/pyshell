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

from pyshell.loader.abstractloader import AbstractLoader
from pyshell.loader.exception import LoadException
from pyshell.loader.exception import RegisterException
from pyshell.loader.exception import UnloadException
from pyshell.loader.masterloader import MasterLoader
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.constants import STATE_UNLOADED_E
from pyshell.utils.exception import ListOfException


class SubAbstractLoader(AbstractLoader):
    def __init__(self, parent):
        AbstractLoader.__init__(self, parent)

    def load(self, parameter_container=None, profile=None):
        pass

    def unload(self, parameter_container=None, profile=None):
        pass


class SubAbstractLoaderWithError(AbstractLoader):
    def __init__(self, parent):
        AbstractLoader.__init__(self, parent)

    def load(self, parameter_container=None, profile=None):
        raise Exception("errroooorrr !")

    def unload(self, parameter_container=None, profile=None):
        pass


class SubAbstractUnloaderWithError(AbstractLoader):
    def __init__(self, parent):
        AbstractLoader.__init__(self, parent)

    def load(self, parameter_container=None, profile=None):
        pass

    def unload(self, parameter_container=None, profile=None):
        raise Exception("errroooorrr !")


class TestMasterLoader(object):
    # MasterLoader, test init, subAddons must be empty, no constructor arg
    def test_MasterLoaderInit(self):
        assert hasattr(MasterLoader, "__init__")
        assert hasattr(MasterLoader.__init__, "__call__")
        assert isinstance(MasterLoader("test.addon.name"), MasterLoader)
        with pytest.raises(TypeError):
            MasterLoader("test.addon.name", None)

    # # getLoader # #

    # profile is not None, loaderName exist
    def test_MasterLoaderGetLoader1(self):
        gl = MasterLoader("test.addon.name")
        l1 = gl.getOrCreateLoader(SubAbstractLoader,
                                  profile="plop")
        l2 = gl.getOrCreateLoader(SubAbstractLoader,
                                  profile="plop")
        l2 = gl.getOrCreateLoader(SubAbstractLoader,
                                  profile="plop")
        assert l1 is l2

    # profile is not None, loaderName does not exist, class_definition
    # is anything
    def test_MasterLoaderGetLoader2(self):
        gl = MasterLoader("test.addon.name")
        with pytest.raises(RegisterException):
            gl.getOrCreateLoader(42, profile="plop")

    # profile is not None, loaderName does not exist, class_definition is
    # AbstractLoader
    def test_MasterLoaderGetLoader3(self):
        gl = MasterLoader("test.addon.name")
        with pytest.raises(RegisterException):
            gl.getOrCreateLoader(AbstractLoader,
                                 profile="plop")

    # profile is not None, loaderName does not exist, class_definition is a
    # class definition that does not inherit from AbstractLoader
    def test_MasterLoaderGetLoader4(self):
        gl = MasterLoader("test.addon.name")
        with pytest.raises(RegisterException):
            gl.getOrCreateLoader(object,
                                 profile="plop")

    # profile is not None, loaderName does not exist, class_definition is
    # valid, profile already exist for another loaderName
    def test_MasterLoaderGetLoader5(self):
        gl = MasterLoader("test.addon.name")
        l1 = gl.getOrCreateLoader(SubAbstractLoader,
                                  profile="plop")
        l2 = gl.getOrCreateLoader(SubAbstractLoader,
                                  profile="plop")
        assert l1 is l2

    # profile is not None, loaderName does not exist, class_definition is
    # valid, profile does not exist for another loaderName
    def test_MasterLoaderGetLoader6(self):
        gl = MasterLoader("test.addon.name")
        l1 = gl.getOrCreateLoader(SubAbstractLoader,
                                  profile="plop")
        assert l1 is not None

    # profile is None, loaderName exist
    def test_MasterLoaderGetLoader7(self):
        gl = MasterLoader("test.addon.name")
        l1 = gl.getOrCreateLoader(SubAbstractLoader,
                                  profile=None)
        l2 = gl.getOrCreateLoader(SubAbstractLoader,
                                  profile=None)
        assert l1 is l2

    # profile is None, loaderName does not exist, class_definition is anything
    def test_MasterLoaderGetLoader8(self):
        gl = MasterLoader("test.addon.name")
        with pytest.raises(RegisterException):
            gl.getOrCreateLoader(42, profile=None)

    # profile is None, loaderName does not exist, class_definition
    # is AbstractLoader
    def test_MasterLoaderGetLoader9(self):
        gl = MasterLoader("test.addon.name")
        with pytest.raises(RegisterException):
            gl.getOrCreateLoader(AbstractLoader,
                                 profile=None)

    # profile is None, loaderName does not exist, class_definition is a
    # class definition that does not inherit from AbstractLoader
    def test_MasterLoaderGetLoader10(self):
        gl = MasterLoader("test.addon.name")
        with pytest.raises(RegisterException):
            gl.getOrCreateLoader(object,
                                 profile=None)

    # profile is None, loaderName does not exist, class_definition is valid,
    # profile already exist for another loaderName
    # def test_MasterLoaderGetLoader11(self):
    #     gl = MasterLoader("test.addon.name")
    #     l1 = gl.getOrCreateLoader(SubAbstractLoader,
    #                               profile=None)
    #     l2 = gl.getOrCreateLoader(SubAbstractLoader,
    #                               profile=None)
    #     assert l1 is not l2

    # profile is None, loaderName does not exist, class_definition is valid,
    # profile does not exist for another loaderName
    def test_MasterLoaderGetLoader12(self):
        gl = MasterLoader("test.addon.name")
        l1 = gl.getOrCreateLoader(SubAbstractLoader,
                                  profile=None)
        assert l1 is not None

    # # _innerLoad # #
    # profile is not None, profile is not in profile_list
    def test_MasterLoaderInnerLoad1(self):
        gl = MasterLoader("test.addon.name")
        assert gl._innerLoad(method_name="kill",
                             priority_method_name="getKillPriority",
                             parameter_container=None,
                             profile="TOTO",
                             next_state="nstate",
                             next_state_if_error="estate") is None
    # profile is not None, profile is in profile_list, profile in invalid state
    # def test_MasterLoader_innerLoad2(self):
    #    gl = MasterLoader("test.addon.name")
    #    gl.getOrCreateLoader("MasterLoader_innerLoad2",
    #                              SubAbstractLoader,
    #                              profile = "TOTO")
    #    self.assertRaises(LoadException,
    #                      gl._innerLoad,
    #                      method_name="kill",
    #                      parameter_container=None,
    #                      profile = "TOTO",
    #                      next_state="nstate",
    #                      next_state_if_error="estate")

    # profile is not None, profile is in profile_list,profile in valid state,
    # unknown method name
    def test_MasterLoaderInnerLoad3(self):
        gl = MasterLoader("test.addon.name")
        gl.getOrCreateLoader(SubAbstractLoader,
                             profile="TOTO")
        with pytest.raises(AttributeError):
            gl._innerLoad(method_name="kill",
                          priority_method_name="getKillPriority",
                          parameter_container=None,
                          profile="TOTO",
                          next_state="nstate",
                          next_state_if_error="estate")

    # profile is not None, profile is in profile_list,profile in valid state,
    # known method name, with error production
    def test_MasterLoaderInnerLoad4(self):
        gl = MasterLoader("test.addon.name")
        gl.getOrCreateLoader(SubAbstractLoaderWithError,
                             profile="TOTO")
        with pytest.raises(ListOfException):
            gl._innerLoad(method_name="load",
                          priority_method_name="getLoadPriority",
                          parameter_container=None,
                          profile="TOTO",
                          next_state="nstate",
                          next_state_if_error="estate")
        assert gl.last_updated_profile[0] == "TOTO"
        assert gl.last_updated_profile[1] == "estate"

    # profile is not None, profile is in profile_list,profile in valid state,
    # known method name, without error production
    def test_MasterLoaderInnerLoad5(self):
        gl = MasterLoader("test.addon.name")
        gl.getOrCreateLoader(SubAbstractLoader,
                             profile="TOTO")
        gl._innerLoad(method_name="load",
                      priority_method_name="getLoadPriority",
                      parameter_container=None,
                      profile="TOTO",
                      next_state="nstate",
                      next_state_if_error="estate")
        assert gl.last_updated_profile[0] == "TOTO"
        assert gl.last_updated_profile[1] == "nstate"

    # profile is None, profile is not in profile_list
    def test_MasterLoaderInnerLoad6(self):
        gl = MasterLoader("test.addon.name")
        assert gl._innerLoad(method_name="kill",
                             priority_method_name="getKillPriority",
                             parameter_container=None,
                             profile=None,
                             next_state="nstate",
                             next_state_if_error="estate") is None

    # profile is None, profile is in profile_list, profile in invalid state
    # def test_MasterLoader_innerLoad7(self):
    #    gl = MasterLoader("test.addon.name")
    #    gl.getOrCreateLoader("MasterLoader_innerLoad7",
    #                              SubAbstractLoader, profile = None)
    #    self.assertRaises(LoadException,
    #                      gl._innerLoad,
    #                      method_name="kill",
    #                      parameter_container=None,
    #                      profile = DEFAULT_PROFILE_NAME,
    #                      next_state="nstate",
    #                      next_state_if_error="estate")

    # profile is None, profile is in profile_list,profile in valid state,
    # unknown method name
    def test_MasterLoaderInnerLoad8(self):
        gl = MasterLoader("test.addon.name")
        gl.getOrCreateLoader(SubAbstractLoader,
                             profile=None)
        with pytest.raises(AttributeError):
            gl._innerLoad(method_name="kill",
                          priority_method_name="getKillPriority",
                          parameter_container=None,
                          profile=DEFAULT_PROFILE_NAME,
                          next_state="nstate",
                          next_state_if_error="estate")

    # profile is None, profile is in profile_list,profile in valid state,
    # known method name, with error production
    def test_MasterLoaderInnerLoad9(self):
        gl = MasterLoader("test.addon.name")
        gl.getOrCreateLoader(SubAbstractLoaderWithError,
                             profile=None)
        with pytest.raises(ListOfException):
            gl._innerLoad(method_name="load",
                          priority_method_name="getLoadPriority",
                          parameter_container=None,
                          profile=DEFAULT_PROFILE_NAME,
                          next_state="nstate",
                          next_state_if_error="estate")
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == "estate"

    # profile is None, profile is in profile_list,profile in valid state,
    # known method name, without error production
    def test_MasterLoaderInnerLoad10(self):
        gl = MasterLoader("test.addon.name")
        gl.getOrCreateLoader(SubAbstractLoader,
                             profile=None)
        gl._innerLoad(method_name="load",
                      priority_method_name="getLoadPriority",
                      parameter_container=None,
                      profile=DEFAULT_PROFILE_NAME,
                      next_state="nstate",
                      next_state_if_error="estate")
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == "nstate"

    # # load # #
    # valid load
    def test_MasterLoaderLoad1(self):
        gl = MasterLoader("test.addon.name")
        gl.getOrCreateLoader(SubAbstractLoader)
        gl.load(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_LOADED

    # valid load with error
    def test_MasterLoaderLoad2(self):
        gl = MasterLoader("test.addon.name")
        gl.getOrCreateLoader(SubAbstractLoaderWithError)
        with pytest.raises(ListOfException):
            gl.load(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_LOADED_E

    # invalid load
    def test_MasterLoaderLoad3(self):
        gl = MasterLoader("test.addon.name")
        gl.getOrCreateLoader(SubAbstractLoader)
        gl.load(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_LOADED
        with pytest.raises(LoadException):
            gl.load(None)
        # gl.load(None)

    # # unload # #
    # valid unload
    def test_MasterLoaderUnload4(self):
        gl = MasterLoader("test.addon.name")
        gl.getOrCreateLoader(SubAbstractLoader)
        gl.load(None)
        gl.unload(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_UNLOADED

    # valid unload with error
    def test_MasterLoaderUnload5(self):
        gl = MasterLoader("test.addon.name")
        gl.getOrCreateLoader(SubAbstractUnloaderWithError)
        gl.load(None)
        with pytest.raises(ListOfException):
            gl.unload(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_UNLOADED_E

    # invalid unload
    def test_MasterLoaderUnload6(self):
        gl = MasterLoader("test.addon.name")
        gl.getOrCreateLoader(SubAbstractLoader)
        gl.load(None)
        gl.unload(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_UNLOADED
        with pytest.raises(UnloadException):
            gl.unload(None)


class RecordLoadOrderAbstractLoader(AbstractLoader):
    def __init__(self, parent):
        AbstractLoader.__init__(self, parent)
        self.load_list = None
        self.unload_list = None
        self.id = None

    def load(self, parameter_container, profile=None):
        self.load_list.append(self.id)

    def unload(self, parameter_container, profile=None):
        self.unload_list.append(self.id)

class RecordLoadOrderAbstractLoader2(RecordLoadOrderAbstractLoader):
    pass

class TestMasterLoaderPriority(object):
    def test_samePriorityInsertionOrder1(self):
        load_list = []
        unload_list = []
        gl = MasterLoader("test.addon.name")
        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader)

        loader.id = 1
        loader.load_list = load_list
        loader.unload_list = unload_list

        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader2)

        loader.id = 2
        loader.load_list = load_list
        loader.unload_list = unload_list

        gl.load(None)

        assert len(load_list) == 2
        assert load_list[0] == 1
        assert load_list[1] == 2

        gl.unload(None)

        assert len(unload_list) == 2
        assert unload_list[0] == 1
        assert unload_list[1] == 2

    def test_samePriorityInsertionOrder2(self):
        load_list = []
        unload_list = []
        gl = MasterLoader("test.addon.name")
        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader)

        loader.id = 2
        loader.load_list = load_list
        loader.unload_list = unload_list

        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader2)

        loader.id = 1
        loader.load_list = load_list
        loader.unload_list = unload_list

        gl.load(None)

        assert len(load_list) == 2
        assert load_list[0] == 2
        assert load_list[1] == 1

        gl.unload(None)

        assert len(unload_list) == 2
        assert unload_list[0] == 2
        assert unload_list[1] == 1

    def test_differentPriorityInsertionOrder1(self):
        load_list = []
        unload_list = []
        gl = MasterLoader("test.addon.name")
        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader)

        loader.id = 1
        loader.load_list = load_list
        loader.unload_list = unload_list
        loader.load_priority = 50
        loader.unload_priority = 50

        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader2)

        loader.id = 2
        loader.load_list = load_list
        loader.unload_list = unload_list

        gl.load(None)

        assert len(load_list) == 2
        assert load_list[0] == 1
        assert load_list[1] == 2

        gl.unload(None)

        assert len(unload_list) == 2
        assert unload_list[0] == 1
        assert unload_list[1] == 2

    def test_differentPriorityInsertionOrder2(self):
        load_list = []
        unload_list = []
        gl = MasterLoader("test.addon.name")
        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader)

        loader.id = 2
        loader.load_list = load_list
        loader.unload_list = unload_list

        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader2)

        loader.id = 1
        loader.load_list = load_list
        loader.unload_list = unload_list
        loader.load_priority = 50
        loader.unload_priority = 50

        gl.load(None)

        assert len(load_list) == 2
        assert load_list[0] == 1
        assert load_list[1] == 2

        gl.unload(None)

        assert len(unload_list) == 2
        assert unload_list[0] == 1
        assert unload_list[1] == 2

    def test_differentPriorityInsertionOrder3(self):
        load_list = []
        unload_list = []
        gl = MasterLoader("test.addon.name")
        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader)

        loader.id = 1
        loader.load_list = load_list
        loader.unload_list = unload_list
        loader.load_priority = 50
        loader.unload_priority = 200

        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader2)

        loader.id = 2
        loader.load_list = load_list
        loader.unload_list = unload_list

        gl.load(None)

        assert len(load_list) == 2
        assert load_list[0] == 1
        assert load_list[1] == 2

        gl.unload(None)

        assert len(unload_list) == 2
        assert unload_list[0] == 2
        assert unload_list[1] == 1

    def test_differentPriorityInsertionOrder4(self):
        load_list = []
        unload_list = []
        gl = MasterLoader("test.addon.name")
        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader)

        loader.id = 2
        loader.load_list = load_list
        loader.unload_list = unload_list

        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader2)

        loader.id = 1
        loader.load_list = load_list
        loader.unload_list = unload_list
        loader.load_priority = 50
        loader.unload_priority = 200

        gl.load(None)

        assert len(load_list) == 2
        assert load_list[0] == 1
        assert load_list[1] == 2

        gl.unload(None)

        assert len(unload_list) == 2
        assert unload_list[0] == 2
        assert unload_list[1] == 1

    def test_differentPriorityInsertionOrder5(self):
        load_list = []
        unload_list = []
        gl = MasterLoader("test.addon.name")
        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader)

        loader.id = 1
        loader.load_list = load_list
        loader.unload_list = unload_list
        loader.load_priority = 200
        loader.unload_priority = 50

        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader2)

        loader.id = 2
        loader.load_list = load_list
        loader.unload_list = unload_list

        gl.load(None)

        assert len(load_list) == 2
        assert load_list[0] == 2
        assert load_list[1] == 1

        gl.unload(None)

        assert len(unload_list) == 2
        assert unload_list[0] == 1
        assert unload_list[1] == 2

    def test_differentPriorityInsertionOrder6(self):
        load_list = []
        unload_list = []
        gl = MasterLoader("test.addon.name")
        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader)

        loader.id = 2
        loader.load_list = load_list
        loader.unload_list = unload_list

        loader = gl.getOrCreateLoader(RecordLoadOrderAbstractLoader2)

        loader.id = 1
        loader.load_list = load_list
        loader.unload_list = unload_list
        loader.load_priority = 200
        loader.unload_priority = 50

        gl.load(None)

        assert len(load_list) == 2
        assert load_list[0] == 2
        assert load_list[1] == 1

        gl.unload(None)

        assert len(unload_list) == 2
        assert unload_list[0] == 1
        assert unload_list[1] == 2
