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

# TODO
#  add new test for allowed transition testing and forbidde several
#  addon loaded
#  remove old test irrelevant about transaction

import pytest

from pyshell.loader.abstractloader import AbstractLoader
from pyshell.loader.exception import LoadException
from pyshell.loader.exception import RegisterException
from pyshell.loader.globalloader import GlobalLoader
from pyshell.loader.utils import getAndInitCallerModule
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

    def reload(self, parameter_manager, profile=None):
        raise Exception("errroooorrr !")


class TestUtils(object):

    def setUp(self):
        pass

    def tearDown(self):
        global _loaders
        if "_loaders" in globals():
            del _loaders

    # ## getAndInitCallerModule ## #

    # getAndInitCallerModule, parent module does not have _loader THEN parent
    # module has _loader
    def test_getAndInitCallerModule1(self):
        global _loaders
        assert "_loaders" not in globals()
        loader1 = getAndInitCallerModule("getAndInitCallerModule1",
                                         SubAbstractLoader,
                                         profile=None,
                                         module_level=1)
        assert "_loaders" in globals()
        assert isinstance(_loaders, GlobalLoader)
        loader2 = getAndInitCallerModule("getAndInitCallerModule1",
                                         SubAbstractLoader,
                                         profile=None,
                                         module_level=1)
        assert loader1 is loader2

    # getAndInitCallerModule, parent module has _loader but with a wrong type
    def test_getAndInitCallerModule2(self):
        global _loaders
        _loaders = "plop"
        assert "_loaders" in globals()
        with pytest.raises(RegisterException):
            # level is 2 because we have to go outside of the assert module
            getAndInitCallerModule("getAndInitCallerModule1",
                                   AbstractLoader,
                                   profile=None,
                                   module_level=2)

    # ## AbstractLoader ## #

    # AbstractLoader, load, exist, test args
    def test_abstractLoader2(self):
        al = AbstractLoader()
        assert al, "load"
        assert al.load, "__call__"
        assert al.load(None) is None
        assert al.load(None, None) is None
        with pytest.raises(TypeError):
            al.load(None, None, None)

    # AbstractLoader, unload, exist, test args
    def test_abstractLoader3(self):
        al = AbstractLoader()
        assert al, "unload"
        assert al.unload, "__call__"
        assert al.unload(None) is None
        assert al.unload(None, None) is None
        with pytest.raises(TypeError):
            al.unload(None, None, None)

    # AbstractLoader, reload, exist, test args
    def test_abstractLoader4(self):
        al = AbstractLoader()
        assert al, "reload"
        assert al.reload, "__call__"
        assert al.reload(None) is None
        assert al.reload(None, None) is None
        with pytest.raises(TypeError):
            al.reload(None, None, None)

    # ## GlobalLoader ## #

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

    # # reload # #
    # valid reload
    def test_globalLoaderReload7(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoaderLoad1", SubAbstractLoader)
        gl.load(None)
        gl.reload(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_LOADED

    # valid reload with error
    def test_globalLoaderReload8(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoaderLoad1",
                             SubAbstractUnloaderWithError)
        gl.load(None)
        with pytest.raises(ListOfException):
            gl.reload(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_LOADED_E

    # invalid reload
    def test_globalLoaderReload9(self):
        gl = GlobalLoader()
        gl.getOrCreateLoader("GlobalLoaderLoad1", SubAbstractLoader)
        gl.load(None)
        gl.unload(None)
        assert gl.last_updated_profile[0] == DEFAULT_PROFILE_NAME
        assert gl.last_updated_profile[1] == STATE_UNLOADED
        with pytest.raises(LoadException):
            gl.reload(None)
