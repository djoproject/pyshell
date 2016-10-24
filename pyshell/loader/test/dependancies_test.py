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

from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.loader.dependancies import DependanciesLoader
from pyshell.loader.dependancies import _localGetAndInitCallerModule
from pyshell.loader.dependancies import registerDependOnAddon
from pyshell.loader.exception import LoadException
from pyshell.loader.exception import RegisterException
from pyshell.loader.masterloader import MasterLoader
from pyshell.loader.utils import getNearestModule
from pyshell.system.container import ParameterContainer
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.environment import EnvironmentParameterManager
from pyshell.system.setting.environment import EnvironmentLocalSettings
from pyshell.utils.constants import ADDONLIST_KEY
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.exception import ListOfException


DEFAULT_CHECKER = DefaultInstanceArgChecker.getArgCheckerInstance()


def loader(profile=None):
    return _localGetAndInitCallerModule(profile)


class TestDependancies(object):

    def teardown_method(self, method):
        mod = getNearestModule()
        if hasattr(mod, "_loaders"):
            delattr(mod, "_loaders")

    # # _localGetAndInitCallerModule # #

    # _localGetAndInitCallerModule with None profile
    def test_localGetAndInitCallerModule1(self):
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")
        a = loader()
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        assert isinstance(_loaders, MasterLoader)
        b = loader()
        assert a is b
        assert isinstance(a, DependanciesLoader)

    # _localGetAndInitCallerModule withouth None profile
    def test_localGetAndInitCallerModule2(self):
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")
        a = loader("plop")
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        assert isinstance(_loaders, MasterLoader)
        b = loader("plop")
        c = loader()
        assert a is b
        assert a is not c
        assert isinstance(a, DependanciesLoader)
        assert isinstance(c, DependanciesLoader)

    # # registerDependOnAddon # #

    # registerDependOnAddon with invalid dependancy_name, profile None
    def testRegisterDependOnAddon1(self):
        with pytest.raises(RegisterException):
            registerDependOnAddon(dependancy_name=object(),
                                  dependancy_profile=None,
                                  profile=None)

    # registerDependOnAddon with str dependancy_name, profile None
    def testRegisterDependOnAddon2(self):
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")
        registerDependOnAddon(dependancy_name="plop",
                              dependancy_profile=None,
                              profile=None)
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        loader_name = (DependanciesLoader.__module__ + "." +
                       DependanciesLoader.__name__)
        l = _loaders.profile_list[DEFAULT_PROFILE_NAME][loader_name]
        assert isinstance(l, DependanciesLoader)
        assert l.dep[0] == ("plop", None,)

    # registerDependOnAddon with unicode dependancy_name, profile None
    def testRegisterDependOnAddon3(self):
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")
        registerDependOnAddon(dependancy_name=u"plop",
                              dependancy_profile=None,
                              profile=None)
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        loader_name = (DependanciesLoader.__module__ + "." +
                       DependanciesLoader.__name__)
        l = _loaders.profile_list[DEFAULT_PROFILE_NAME][loader_name]
        assert isinstance(l, DependanciesLoader)
        assert l.dep[0] == (u"plop", None,)

    # registerDependOnAddon with invalid dependancy_profile, profile None
    def testRegisterDependOnAddon4(self):
        with pytest.raises(RegisterException):
            registerDependOnAddon(dependancy_name="plop",
                                  dependancy_profile=object(),
                                  profile=None)

    # registerDependOnAddon with str dependancy_profile, profile None
    def testRegisterDependOnAddon5(self):
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")
        registerDependOnAddon(dependancy_name="plop",
                              dependancy_profile="tutu",
                              profile=None)
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        loader_name = (DependanciesLoader.__module__ + "." +
                       DependanciesLoader.__name__)
        l = _loaders.profile_list[DEFAULT_PROFILE_NAME][loader_name]
        assert isinstance(l, DependanciesLoader)
        assert l.dep[0] == ("plop", "tutu",)

    # registerDependOnAddon with unicode dependancy_profile, profile None
    def testRegisterDependOnAddon6(self):
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")
        registerDependOnAddon(dependancy_name=u"plop",
                              dependancy_profile=u"tutu",
                              profile=None)
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        loader_name = (DependanciesLoader.__module__ + "." +
                       DependanciesLoader.__name__)
        l = _loaders.profile_list[DEFAULT_PROFILE_NAME][loader_name]
        assert isinstance(l, DependanciesLoader)
        assert l.dep[0] == (u"plop", u"tutu",)

    # registerDependOnAddon with invalid dependancy_name, profile not None
    def testRegisterDependOnAddon7(self):
        with pytest.raises(RegisterException):
            registerDependOnAddon(dependancy_name=object(),
                                  dependancy_profile=None,
                                  profile="ahah")

    # registerDependOnAddon with str dependancy_name, profile not None
    def testRegisterDependOnAddon8(self):
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")
        registerDependOnAddon(dependancy_name="plop",
                              dependancy_profile=None,
                              profile="ahah")
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        loader_name = (DependanciesLoader.__module__ + "." +
                       DependanciesLoader.__name__)
        l = _loaders.profile_list["ahah"][loader_name]
        assert isinstance(l, DependanciesLoader)
        assert l.dep[0] == ("plop", None,)

    # registerDependOnAddon with unicode dependancy_name, profile not None
    def testRegisterDependOnAddon9(self):
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")
        registerDependOnAddon(dependancy_name=u"plop",
                              dependancy_profile=None,
                              profile="ahah")
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        loader_name = (DependanciesLoader.__module__ + "." +
                       DependanciesLoader.__name__)
        l = _loaders.profile_list["ahah"][loader_name]
        assert isinstance(l, DependanciesLoader)
        assert l.dep[0] == (u"plop", None,)

    # registerDependOnAddon with invalid dependancy_profile, profile not None
    def testRegisterDependOnAddon10(self):
        with pytest.raises(RegisterException):
            registerDependOnAddon(dependancy_name="plop",
                                  dependancy_profile=object(),
                                  profile="uhuh")

    # registerDependOnAddon with str dependancy_profile, profile not None
    def testRegisterDependOnAddon11(self):
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")
        registerDependOnAddon(dependancy_name="plop",
                              dependancy_profile="tutu",
                              profile="uhuh")
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        loader_name = (DependanciesLoader.__module__ + "." +
                       DependanciesLoader.__name__)
        l = _loaders.profile_list["uhuh"][loader_name]
        assert isinstance(l, DependanciesLoader)
        assert l.dep[0] == ("plop", "tutu",)

    # registerDependOnAddon with unicode dependancy_profile, profile not None
    def testRegisterDependOnAddon12(self):
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")
        registerDependOnAddon(dependancy_name=u"plop",
                              dependancy_profile=u"tutu",
                              profile="uhuh")
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        loader_name = (DependanciesLoader.__module__ + "." +
                       DependanciesLoader.__name__)
        l = _loaders.profile_list["uhuh"][loader_name]
        assert isinstance(l, DependanciesLoader)
        assert l.dep[0] == (u"plop", u"tutu",)

    # # DependanciesLoader # #

    # __init__
    def testDependanciesLoaderInit(self):
        assert hasattr(DependanciesLoader, "__init__")
        assert hasattr(DependanciesLoader.__init__, "__call__")
        assert isinstance(DependanciesLoader(None), DependanciesLoader)
        with pytest.raises(TypeError):
            DependanciesLoader(None, None)

    # load with zero dep
    def testDependanciesLoaderLoad1(self):
        dl = DependanciesLoader(None)
        dl.load(None)

    # load with dep and ADDONLIST_KEY not in env
    def testDependanciesLoaderLoad2(self):
        dl = DependanciesLoader(None)
        dl.dep.append(("addons.plop", None,))
        pc = ParameterContainer()
        pc.registerParameterManager("environment",
                                    EnvironmentParameterManager())
        with pytest.raises(LoadException):
            dl.load(pc)

    # load with dep, ADDONLIST_KEY defined in env, with dependancy_name
    # not satisfied
    def testDependanciesLoaderLoad3(self):
        dl = DependanciesLoader(None)
        dl.dep.append(("addons.plop", None,))
        pc = ParameterContainer()
        pc.registerParameterManager("environment",
                                    EnvironmentParameterManager())
        env_settings = EnvironmentLocalSettings(checker=DEFAULT_CHECKER)
        pc.environment.setParameter(
            ADDONLIST_KEY,
            EnvironmentParameter(value={}, settings=env_settings),
            local_param=False)
        with pytest.raises(ListOfException) as loe:
            dl.load(pc)
        
        assert len(loe.value.exceptions) is 1
        assert isinstance(loe.value.exceptions[0], LoadException)

    # load with dep, ADDONLIST_KEY defined in env, with dependancy_name
    # satisfied, dependancy_profile not satisfied
    def testDependanciesLoaderLoad4(self):
        dl = DependanciesLoader(None)
        dl.dep.append(("addons.plop", "profile.plap",))
        pc = ParameterContainer()
        pc.registerParameterManager("environment",
                                    EnvironmentParameterManager())
        env_settings = EnvironmentLocalSettings(checker=DEFAULT_CHECKER)
        param = pc.environment.setParameter(
            ADDONLIST_KEY,
            EnvironmentParameter(value={}, settings=env_settings),
            local_param=False)
        loader = MasterLoader("test.addon.name")
        param.getValue()["addons.plop"] = loader
        loader.profile_list[DEFAULT_PROFILE_NAME] = (None, STATE_LOADED,)
        with pytest.raises(ListOfException) as loe:
            dl.load(pc)

        assert len(loe.value.exceptions) is 1
        assert isinstance(loe.value.exceptions[0], LoadException)

    # load with dep, ADDONLIST_KEY defined in env, with dependancy_name
    # satisfied, dependancy_profile satisfied, loaded
    def testDependanciesLoaderLoad5(self):
        dl = DependanciesLoader(None)
        dl.dep.append(("addons.plop", "profile.plap",))
        pc = ParameterContainer()
        pc.registerParameterManager("environment",
                                    EnvironmentParameterManager())
        env_settings = EnvironmentLocalSettings(checker=DEFAULT_CHECKER)
        param = pc.environment.setParameter(
            ADDONLIST_KEY,
            EnvironmentParameter(value={}, settings=env_settings),
            local_param=False)
        loader = MasterLoader("test.addon.name")
        param.getValue()["addons.plop"] = loader
        loader.profile_list["profile.plap"] = (None, STATE_LOADED,)
        dl.load(pc)

    # load with dep, ADDONLIST_KEY defined in env, with dependancy_name
    # satisfied, dependancy_profile satisfied, not loaded
    def testDependanciesLoaderLoad6(self):
        dl = DependanciesLoader(None)
        dl.dep.append(("addons.plop", "profile.plap",))
        pc = ParameterContainer()
        pc.registerParameterManager("environment",
                                    EnvironmentParameterManager())
        env_settings = EnvironmentLocalSettings(checker=DEFAULT_CHECKER)
        param = pc.environment.setParameter(
            ADDONLIST_KEY,
            EnvironmentParameter(value={}, settings=env_settings),
            local_param=False)
        loader = MasterLoader("test.addon.name")
        param.getValue()["addons.plop"] = loader
        loader.profile_list["profile.plap"] = (None, STATE_UNLOADED,)
        with pytest.raises(ListOfException) as loe:
            dl.load(pc)

        assert len(loe.value.exceptions) is 1
        assert isinstance(loe.value.exceptions[0], LoadException)
