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
from pyshell.loader.globalloader import GlobalLoader
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.constants import STATE_UNLOADED_E
from pyshell.utils.exception import ListOfException


class SubAbstractLoader(AbstractLoader):
    pass


class SubAbstractLoaderWithError(AbstractLoader):

    def load(self, parameter_manager, profile=None):
        raise Exception("errroooorrr !")


class SubAbstractUnloaderWithError(AbstractLoader):

    def unload(self, parameter_manager, profile=None):
        raise Exception("errroooorrr !")


class TestGlobalLoader(object):
    # GlobalLoader, test init, subAddons must be empty, no constructor arg
    def test_globalLoaderInit(self):
        assert hasattr(GlobalLoader, "__init__")
        assert hasattr(GlobalLoader.__init__, "__call__")
        assert isinstance(GlobalLoader(), GlobalLoader)
        with pytest.raises(TypeError):
            GlobalLoader(None)

    # # getLoader # #

    # profile is not None, loaderName exist
    def test_globalLoaderGetLoader1(self):
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderGetLoader1",
                                  SubAbstractLoader,
                                  profile="plop")
        l2 = gl.getOrCreateLoader("GlobalLoaderGetLoader1",
                                  SubAbstractLoader,
                                  profile="plop")
        l2 = gl.getOrCreateLoader("GlobalLoaderGetLoader1",
                                  SubAbstractLoader,
                                  profile="plop")
        assert l1 is l2

    # profile is not None, loaderName does not exist, class_definition
    # is anything
    def test_globalLoaderGetLoader2(self):
        gl = GlobalLoader()
        with pytest.raises(RegisterException):
            gl.getOrCreateLoader("GlobalLoaderGetLoader2", 42, profile="plop")

    # profile is not None, loaderName does not exist, class_definition is
    # AbstractLoader
    def test_globalLoaderGetLoader3(self):
        gl = GlobalLoader()
        with pytest.raises(RegisterException):
            gl.getOrCreateLoader("GlobalLoaderGetLoader3",
                                 AbstractLoader,
                                 profile="plop")

    # profile is not None, loaderName does not exist, class_definition is a
    # class definition that does not inherit from AbstractLoader
    def test_globalLoaderGetLoader4(self):
        gl = GlobalLoader()
        with pytest.raises(RegisterException):
            gl.getOrCreateLoader("GlobalLoaderGetLoader4",
                                 object,
                                 profile="plop")

    # profile is not None, loaderName does not exist, class_definition is
    # valid, profile already exist for another loaderName
    def test_globalLoaderGetLoader5(self):
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderGetLoader5a",
                                  SubAbstractLoader,
                                  profile="plop")
        l2 = gl.getOrCreateLoader("GlobalLoaderGetLoader5b",
                                  SubAbstractLoader,
                                  profile="plop")
        assert l1 is not l2

    # profile is not None, loaderName does not exist, class_definition is
    # valid, profile does not exist for another loaderName
    def test_globalLoaderGetLoader6(self):
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderGetLoader6",
                                  SubAbstractLoader,
                                  profile="plop")
        assert l1 is not None

    # profile is None, loaderName exist
    def test_globalLoaderGetLoader7(self):
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderGetLoader7",
                                  SubAbstractLoader,
                                  profile=None)
        l2 = gl.getOrCreateLoader("GlobalLoaderGetLoader7",
                                  SubAbstractLoader,
                                  profile=None)
        assert l1 is l2

    # profile is None, loaderName does not exist, class_definition is anything
    def test_globalLoaderGetLoader8(self):
        gl = GlobalLoader()
        with pytest.raises(RegisterException):
            gl.getOrCreateLoader("GlobalLoaderGetLoader8", 42, profile=None)

    # profile is None, loaderName does not exist, class_definition
    # is AbstractLoader
    def test_globalLoaderGetLoader9(self):
        gl = GlobalLoader()
        with pytest.raises(RegisterException):
            gl.getOrCreateLoader("GlobalLoaderGetLoader9",
                                 AbstractLoader,
                                 profile=None)

    # profile is None, loaderName does not exist, class_definition is a
    # class definition that does not inherit from AbstractLoader
    def test_globalLoaderGetLoader10(self):
        gl = GlobalLoader()
        with pytest.raises(RegisterException):
            gl.getOrCreateLoader("GlobalLoaderGetLoader10",
                                 object,
                                 profile=None)

    # profile is None, loaderName does not exist, class_definition is valid,
    # profile already exist for another loaderName
    def test_globalLoaderGetLoader11(self):
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderGetLoader11a",
                                  SubAbstractLoader,
                                  profile=None)
        l2 = gl.getOrCreateLoader("GlobalLoaderGetLoader11b",
                                  SubAbstractLoader,
                                  profile=None)
        assert l1 is not l2

    # profile is None, loaderName does not exist, class_definition is valid,
    # profile does not exist for another loaderName
    def test_globalLoaderGetLoader12(self):
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderGetLoader12",
                                  SubAbstractLoader,
                                  profile=None)
        assert l1 is not None

    # # _innerLoad # #
    # profile is not None, profile is not in profile_list
    def test_globalLoaderInnerLoad1(self):
        gl = GlobalLoader()
        assert gl._innerLoad(method_name="kill",
                             priority_method_name="getKillPriority",
                             parameter_manager=None,
                             profile="TOTO",
                             next_state="nstate",
                             next_state_if_error="estate") is None
    # profile is not None, profile is in profile_list, profile in invalid state
    # def test_GlobalLoader_innerLoad2(self):
    #    gl = GlobalLoader()
    #    gl.getOrCreateLoader("GlobalLoader_innerLoad2",
    #                              SubAbstractLoader,
    #                              profile = "TOTO")
    #    self.assertRaises(LoadException,
    #                      gl._innerLoad,
    #                      method_name="kill",
    #                      parameter_manager=None,
    #                      profile = "TOTO",
    #                      next_state="nstate",
    #                      next_state_if_error="estate")

    # profile is not None, profile is in profile_list,profile in valid state,
    # unknown method name
    def test_globalLoaderInnerLoad3(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoader_innerLoad3",
                             SubAbstractLoader,
                             profile="TOTO")
        with pytest.raises(AttributeError):
            gl._innerLoad(method_name="kill",
                          priority_method_name="getKillPriority",
                          parameter_manager=None,
                          profile="TOTO",
                          next_state="nstate",
                          next_state_if_error="estate")

    # profile is not None, profile is in profile_list,profile in valid state,
    # known method name, with error production
    def test_globalLoaderInnerLoad4(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoader_innerLoad4",
                             SubAbstractLoaderWithError,
                             profile="TOTO")
        with pytest.raises(ListOfException):
            gl._innerLoad(method_name="load",
                          priority_method_name="getLoadPriority",
                          parameter_manager=None,
                          profile="TOTO",
                          next_state="nstate",
                          next_state_if_error="estate")
        assert gl.last_updated_profile[0] == "TOTO"
        assert gl.last_updated_profile[1] == "estate"

    # profile is not None, profile is in profile_list,profile in valid state,
    # known method name, without error production
    def test_globalLoaderInnerLoad5(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoader_innerLoad5",
                             SubAbstractLoader,
                             profile="TOTO")
        gl._innerLoad(method_name="load",
                      priority_method_name="getLoadPriority",
                      parameter_manager=None,
                      profile="TOTO",
                      next_state="nstate",
                      next_state_if_error="estate")
        assert gl.last_updated_profile[0] == "TOTO"
        assert gl.last_updated_profile[1] == "nstate"

    # profile is None, profile is not in profile_list
    def test_globalLoaderInnerLoad6(self):
        gl = GlobalLoader()
        assert gl._innerLoad(method_name="kill",
                             priority_method_name="getKillPriority",
                             parameter_manager=None,
                             profile=None,
                             next_state="nstate",
                             next_state_if_error="estate") is None

    # profile is None, profile is in profile_list, profile in invalid state
    # def test_GlobalLoader_innerLoad7(self):
    #    gl = GlobalLoader()
    #    gl.getOrCreateLoader("GlobalLoader_innerLoad7",
    #                              SubAbstractLoader, profile = None)
    #    self.assertRaises(LoadException,
    #                      gl._innerLoad,
    #                      method_name="kill",
    #                      parameter_manager=None,
    #                      profile = DEFAULT_PROFILE_NAME,
    #                      next_state="nstate",
    #                      next_state_if_error="estate")

    # profile is None, profile is in profile_list,profile in valid state,
    # unknown method name
    def test_globalLoaderInnerLoad8(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoader_innerLoad8",
                             SubAbstractLoader,
                             profile=None)
        with pytest.raises(AttributeError):
            gl._innerLoad(method_name="kill",
                          priority_method_name="getKillPriority",
                          parameter_manager=None,
                          profile=DEFAULT_PROFILE_NAME,
                          next_state="nstate",
                          next_state_if_error="estate")

    # profile is None, profile is in profile_list,profile in valid state,
    # known method name, with error production
    def test_globalLoaderInnerLoad9(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoader_innerLoad9",
                             SubAbstractLoaderWithError,
                             profile=None)
        with pytest.raises(ListOfException):
            gl._innerLoad(method_name="load",
                          priority_method_name="getLoadPriority",
                          parameter_manager=None,
                          profile=DEFAULT_PROFILE_NAME,
                          next_state="nstate",
                          next_state_if_error="estate")
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == "estate"

    # profile is None, profile is in profile_list,profile in valid state,
    # known method name, without error production
    def test_globalLoaderInnerLoad10(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoader_innerLoad10",
                             SubAbstractLoader,
                             profile=None)
        gl._innerLoad(method_name="load",
                      priority_method_name="getLoadPriority",
                      parameter_manager=None,
                      profile=DEFAULT_PROFILE_NAME,
                      next_state="nstate",
                      next_state_if_error="estate")
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == "nstate"

    # # load # #
    # valid load
    def test_globalLoaderLoad1(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoaderLoad1", SubAbstractLoader)
        gl.load(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_LOADED

    # valid load with error
    def test_globalLoaderLoad2(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoaderLoad2",
                             SubAbstractLoaderWithError)
        with pytest.raises(ListOfException):
            gl.load(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_LOADED_E

    # invalid load
    def test_globalLoaderLoad3(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoaderLoad3", SubAbstractLoader)
        gl.load(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_LOADED
        # with pytest.raises(LoadException):
        #     gl.load(None)
        # from now, no exception is raised if an addon is already loaded
        # maybe it will change in the future.
        gl.load(None)

    # # unload # #
    # valid unload
    def test_globalLoaderUnload4(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoaderLoad1", SubAbstractLoader)
        gl.load(None)
        gl.unload(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_UNLOADED

    # valid unload with error
    def test_globalLoaderUnload5(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoaderLoad1",
                             SubAbstractUnloaderWithError)
        gl.load(None)
        with pytest.raises(ListOfException):
            gl.unload(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_UNLOADED_E

    # invalid unload
    def test_globalLoaderUnload6(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoaderLoad1", SubAbstractLoader)
        gl.load(None)
        gl.unload(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_UNLOADED
        with pytest.raises(LoadException):
            gl.unload(None)


class RecordLoadOrderAbstractLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.load_list = None
        self.unload_list = None
        self.id = None

    def load(self, parameter_manager, profile=None):
        self.load_list.append(self.id)

    def unload(self, parameter_manager, profile=None):
        self.unload_list.append(self.id)


class TestGlobalLoaderPriority(object):
    def test_samePriorityInsertionOrder1(self):
        load_list = []
        unload_list = []
        gl = GlobalLoader()
        loader = gl.getOrCreateLoader("GlobalLoaderLoad1",
                                      RecordLoadOrderAbstractLoader)

        loader.id = 1
        loader.load_list = load_list
        loader.unload_list = unload_list

        loader = gl.getOrCreateLoader("GlobalLoaderLoad2",
                                      RecordLoadOrderAbstractLoader)

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
        gl = GlobalLoader()
        loader = gl.getOrCreateLoader("GlobalLoaderLoad1",
                                      RecordLoadOrderAbstractLoader)

        loader.id = 2
        loader.load_list = load_list
        loader.unload_list = unload_list

        loader = gl.getOrCreateLoader("GlobalLoaderLoad2",
                                      RecordLoadOrderAbstractLoader)

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
        gl = GlobalLoader()
        loader = gl.getOrCreateLoader("GlobalLoaderLoad1",
                                      RecordLoadOrderAbstractLoader)

        loader.id = 1
        loader.load_list = load_list
        loader.unload_list = unload_list
        loader.load_priority = 50
        loader.unload_priority = 50

        loader = gl.getOrCreateLoader("GlobalLoaderLoad2",
                                      RecordLoadOrderAbstractLoader)

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
        gl = GlobalLoader()
        loader = gl.getOrCreateLoader("GlobalLoaderLoad1",
                                      RecordLoadOrderAbstractLoader)

        loader.id = 2
        loader.load_list = load_list
        loader.unload_list = unload_list

        loader = gl.getOrCreateLoader("GlobalLoaderLoad2",
                                      RecordLoadOrderAbstractLoader)

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
        gl = GlobalLoader()
        loader = gl.getOrCreateLoader("GlobalLoaderLoad1",
                                      RecordLoadOrderAbstractLoader)

        loader.id = 1
        loader.load_list = load_list
        loader.unload_list = unload_list
        loader.load_priority = 50
        loader.unload_priority = 200

        loader = gl.getOrCreateLoader("GlobalLoaderLoad2",
                                      RecordLoadOrderAbstractLoader)

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
        gl = GlobalLoader()
        loader = gl.getOrCreateLoader("GlobalLoaderLoad1",
                                      RecordLoadOrderAbstractLoader)

        loader.id = 2
        loader.load_list = load_list
        loader.unload_list = unload_list

        loader = gl.getOrCreateLoader("GlobalLoaderLoad2",
                                      RecordLoadOrderAbstractLoader)

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
        gl = GlobalLoader()
        loader = gl.getOrCreateLoader("GlobalLoaderLoad1",
                                      RecordLoadOrderAbstractLoader)

        loader.id = 1
        loader.load_list = load_list
        loader.unload_list = unload_list
        loader.load_priority = 200
        loader.unload_priority = 50

        loader = gl.getOrCreateLoader("GlobalLoaderLoad2",
                                      RecordLoadOrderAbstractLoader)

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
        gl = GlobalLoader()
        loader = gl.getOrCreateLoader("GlobalLoaderLoad1",
                                      RecordLoadOrderAbstractLoader)

        loader.id = 2
        loader.load_list = load_list
        loader.unload_list = unload_list

        loader = gl.getOrCreateLoader("GlobalLoaderLoad2",
                                      RecordLoadOrderAbstractLoader)

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
