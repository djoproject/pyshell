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

from tries import multiLevelTries

from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.command.command import MultiCommand
from pyshell.command.command import UniCommand
from pyshell.loader.command import CommandLoader
from pyshell.loader.command import _localGetAndInitCallerModule
from pyshell.loader.command import registerAnInstanciatedCommand
from pyshell.loader.command import registerAndCreateEmptyMultiCommand
from pyshell.loader.command import registerCommand
from pyshell.loader.command import registerResetTempPrefix
from pyshell.loader.command import registerSetGlobalPrefix
from pyshell.loader.command import registerSetTempPrefix
from pyshell.loader.command import registerStopHelpTraversalAt
from pyshell.loader.exception import LoadException
from pyshell.loader.exception import RegisterException
from pyshell.loader.exception import UnloadException
from pyshell.loader.masterloader import MasterLoader
from pyshell.loader.utils import getNearestModule
from pyshell.system.container import ParameterContainer
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.environment import EnvironmentParameterManager
from pyshell.system.setting.environment import EnvironmentGlobalSettings
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.exception import ListOfException


def loader(profile=None):
    return _localGetAndInitCallerModule(profile)


def prePro():
    pass


def proPro():
    pass


def postPro():
    pass


class TestRegisterCommand(object):

    def teardown_method(self, method):
        mod = getNearestModule()
        if hasattr(mod, "_loaders"):
            delattr(mod, "_loaders")

    def preTest(self):
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")

    def postTest(self, profile):
        mod = getNearestModule()
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        assert isinstance(_loaders, MasterLoader)
        assert hasattr(_loaders, "profile_list")
        assert isinstance(_loaders.profile_list, dict)
        assert profile in _loaders.profile_list
        profile_loaders = _loaders.profile_list[profile]

        loader_key = CommandLoader.__module__ + "." + CommandLoader.__name__

        assert isinstance(profile_loaders, dict)
        assert loader_key in profile_loaders

        l = profile_loaders[loader_key]
        assert isinstance(l, CommandLoader)

        return l

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
        assert isinstance(a, CommandLoader)

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
        assert isinstance(a, CommandLoader)
        assert isinstance(c, CommandLoader)

    # # registering # #

    # registerSetGlobalPrefix with invalid key_list, with profile None
    def test_registerSetGlobalPrefix1(self):
        with pytest.raises(RegisterException):
            registerSetGlobalPrefix(object(), None)

    # registerSetGlobalPrefix with invalid key_list, with profile not None
    def test_registerSetGlobalPrefix2(self):
        with pytest.raises(RegisterException):
            registerSetGlobalPrefix(object(), "None")

    # registerSetGlobalPrefix with valid key_list, with profile None
    def test_registerSetGlobalPrefix3(self):
        self.preTest()
        registerSetGlobalPrefix(("plop", "plip",), None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert hasattr(l, "prefix")
        assert l.prefix == ("plop", "plip",)

    # registerSetGlobalPrefix with valid key_list, with profile not None
    def test_registerSetGlobalPrefix4(self):
        self.preTest()
        registerSetGlobalPrefix(("plop", "plip",), "None")
        l = self.postTest("None")
        assert hasattr(l, "prefix")
        assert l.prefix == ("plop", "plip",)

    # registerSetTempPrefix with invalid key_list, with profile None
    def test_registerSetTempPrefix1(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerSetTempPrefix(key_list=object(), profile=None)
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")

    # registerSetTempPrefix with invalid key_list, with profile not None
    def test_registerSetTempPrefix2(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerSetTempPrefix(key_list=object(), profile="None")
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")

    # registerSetTempPrefix with valid key_list, with profile None
    def test_registerSetTempPrefix3(self):
        self.preTest()
        registerSetTempPrefix(key_list=("tutu", "toto",), profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert hasattr(l, "TempPrefix")
        assert l.TempPrefix == ("tutu", "toto",)

    # registerSetTempPrefix with valid key_list, with profile not None
    def test_registerSetTempPrefix4(self):
        self.preTest()
        registerSetTempPrefix(key_list=("tutu", "toto",), profile="None")
        l = self.postTest("None")
        assert hasattr(l, "TempPrefix")
        assert l.TempPrefix == ("tutu", "toto",)

    # registerResetTempPrefix with temp prefix set, with profile None
    def test_registerResetTempPrefix1(self):
        self.preTest()
        registerSetTempPrefix(key_list=("tutu", "toto",), profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert hasattr(l, "TempPrefix")
        assert l.TempPrefix == ("tutu", "toto",)
        registerResetTempPrefix(profile=None)
        assert l.TempPrefix is None

    # registerResetTempPrefix with temp prefix set, with profile not None
    def test_registerResetTempPrefix2(self):
        self.preTest()
        registerSetTempPrefix(key_list=("tutu", "toto",), profile="None")
        l = self.postTest("None")
        assert hasattr(l, "TempPrefix")
        assert l.TempPrefix == ("tutu", "toto",)
        registerResetTempPrefix(profile="None")
        assert l.TempPrefix is None

    # registerResetTempPrefix without temp prefix set, with profile None
    def test_registerResetTempPrefix3(self):
        self.preTest()
        registerResetTempPrefix(profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert hasattr(l, "TempPrefix")
        assert l.TempPrefix is None

    # registerResetTempPrefix without temp prefix set, with profile not None
    def test_registerResetTempPrefix4(self):
        self.preTest()
        registerResetTempPrefix(profile="None")
        l = self.postTest("None")
        assert hasattr(l, "TempPrefix")
        assert l.TempPrefix is None
    # registerAnInstanciatedCommand with invalid command type, with
    # profile None

    def test_registerAnInstanciatedCommand1(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerAnInstanciatedCommand(key_list=("plop",),
                                          cmd="tutu",
                                          profile=None)
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")

    # registerAnInstanciatedCommand with invalid command type, with profile
    # not None
    def test_registerAnInstanciatedCommand2(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerAnInstanciatedCommand(key_list=("plop",),
                                          cmd="tutu",
                                          profile="None")
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")

    # registerAnInstanciatedCommand with invalid key_list, with profile None
    def test_registerAnInstanciatedCommand3(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerAnInstanciatedCommand(key_list=object(),
                                          cmd=MultiCommand(),
                                          profile=None)
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")

    # registerAnInstanciatedCommand with invalid key_list, with profile
    # not None
    def test_registerAnInstanciatedCommand4(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerAnInstanciatedCommand(key_list=object(),
                                          cmd=MultiCommand(),
                                          profile="None")
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")

    # registerAnInstanciatedCommand with valid args, with profile None
    def test_registerAnInstanciatedCommand5(self):
        self.preTest()
        key = ("plop", "plip",)
        mc = MultiCommand()
        registerAnInstanciatedCommand(key_list=key,
                                      cmd=mc,
                                      profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == mc

    # registerAnInstanciatedCommand with valid args, with profile not None
    def test_registerAnInstanciatedCommand6(self):
        self.preTest()
        key = ("plop", "plip",)
        mc = MultiCommand()
        registerAnInstanciatedCommand(key_list=key,
                                      cmd=mc,
                                      profile="None")
        l = self.postTest("None")
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == mc

    # registerAnInstanciatedCommand with valid args and registerSetTempPrefix,
    # with profile None
    def test_registerAnInstanciatedCommand7(self):
        self.preTest()
        key = ("plup", "plop", "plip",)
        mc = MultiCommand()
        registerSetTempPrefix(("plup",))
        registerAnInstanciatedCommand(key_list=("plop", "plip",),
                                      cmd=mc,
                                      profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == mc

    # registerAnInstanciatedCommand with valid args and registerSetTempPrefix,
    # with profile not None
    def test_registerAnInstanciatedCommand8(self):
        self.preTest()
        key = ("plup", "plop", "plip",)
        mc = MultiCommand()
        registerSetTempPrefix(("plup",), profile="None")
        registerAnInstanciatedCommand(key_list=("plop", "plip",),
                                      cmd=mc,
                                      profile="None")
        l = self.postTest("None")
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == mc

    # registerAnInstanciatedCommand with valid args and
    # registerSetGlobalPrefix, with profile None
    def test_registerAnInstanciatedCommand9(self):
        self.preTest()
        key = ("plop", "plip",)
        mc = MultiCommand()
        registerSetGlobalPrefix(("plup",), profile=None)
        registerAnInstanciatedCommand(key_list=key,
                                      cmd=mc,
                                      profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == mc
        assert hasattr(l, "prefix")
        assert l.prefix == ("plup",)

    # registerAnInstanciatedCommand with valid args and
    # registerSetGlobalPrefix, with profile not None
    def test_registerAnInstanciatedCommand10(self):
        self.preTest()
        key = ("plop", "plip",)
        mc = MultiCommand()
        registerSetGlobalPrefix(("plup",), profile="None")
        registerAnInstanciatedCommand(key_list=key,
                                      cmd=mc,
                                      profile="None")
        l = self.postTest("None")
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == mc
        assert hasattr(l, "prefix")
        assert l.prefix == ("plup",)

    # registerCommand with invalid key_list, with profile None
    def test_registerCommand1(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerCommand(key_list=object(),
                            pre=None,
                            pro=proPro,
                            post=None,
                            profile=None)
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")

    # registerCommand with invalid key_list, with profile not None
    def test_registerCommand2(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerCommand(key_list=object(),
                            pre=None,
                            pro=proPro,
                            post=None,
                            profile="None")
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")

    # registerCommand test pre/pro/post, with profile None
    def test_registerCommand5(self):
        self.preTest()
        key = ("plip",)
        c = registerCommand(key_list=key,
                            pre=prePro,
                            pro=proPro,
                            post=postPro,
                            profile=None)
        self.postTest(DEFAULT_PROFILE_NAME)

        assert isinstance(c, MultiCommand)
        assert len(c) == 1
        co, a, e = c[0]

        assert co.preProcess is prePro
        assert co.process is proPro
        assert co.postProcess is postPro

    # registerCommand test pre/pro/post, with profile not None
    def test_registerCommand6(self):
        self.preTest()
        key = ("plip",)
        c = registerCommand(key_list=key,
                            pre=prePro,
                            pro=proPro,
                            post=postPro,
                            profile="None")
        self.postTest("None")

        assert isinstance(c, MultiCommand)
        assert len(c) == 1
        co, a, e = c[0]

        assert co.preProcess is prePro
        assert co.process is proPro
        assert co.postProcess is postPro

    # registerCommand with valid args and registerSetTempPrefix,
    # with profile None
    def test_registerCommand9(self):
        self.preTest()
        key = ("plup", "plop", "plip",)
        registerSetTempPrefix(key_list=("plup", "plop",), profile=None)
        c = registerCommand(key_list=("plip",),
                            pre=None,
                            pro=proPro,
                            post=None,
                            profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == c

    # registerCommand with valid args and registerSetTempPrefix,
    # with profile not None
    def test_registerCommand10(self):
        self.preTest()
        key = ("plup", "plop", "plip",)
        registerSetTempPrefix(key_list=("plup", "plop",), profile="None")
        c = registerCommand(key_list=("plip",),
                            pre=None,
                            pro=proPro,
                            post=None,
                            profile="None")
        l = self.postTest("None")
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == c

    # registerCommand with valid args and registerSetGlobalPrefix,
    # with profile None
    def test_registerCommand11(self):
        self.preTest()
        key = ("plip",)
        registerSetGlobalPrefix(key_list=("plup", "plop",), profile=None)
        c = registerCommand(key_list=key,
                            pre=None,
                            pro=proPro,
                            post=None,
                            profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)

        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == c

    # registerCommand with valid args and registerSetGlobalPrefix,
    # with profile not None
    def test_registerCommand12(self):
        self.preTest()
        key = ("plip",)
        registerSetGlobalPrefix(key_list=("plup", "plop",), profile="None")
        c = registerCommand(key_list=key,
                            pre=None,
                            pro=proPro,
                            post=None,
                            profile="None")
        l = self.postTest("None")

        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == c

    # registerCreateMultiCommand with invalid key_list, with profile None
    def test_registerCreateMultiCommand1(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerAndCreateEmptyMultiCommand(key_list=object(),
                                               profile=None)
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")

    # registerCreateMultiCommand with invalid key_list, with profile not None
    def test_registerCreateMultiCommand2(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerAndCreateEmptyMultiCommand(key_list=object(),
                                               profile="None")
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")

    # registerCreateMultiCommand with valid args and registerSetTempPrefix,
    # with profile None
    def test_registerCreateMultiCommand7(self):
        self.preTest()
        key = ("plup", "plop", "plip",)
        registerSetTempPrefix(key_list=("plup", "plop",), profile=None)
        mc = registerAndCreateEmptyMultiCommand(key_list=("plip",),
                                                profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == mc

    # registerCreateMultiCommand with valid args and registerSetTempPrefix,
    # with profile not None
    def test_registerCreateMultiCommand8(self):
        self.preTest()
        key = ("plup", "plop", "plip",)
        registerSetTempPrefix(key_list=("plup", "plop",), profile="None")
        mc = registerAndCreateEmptyMultiCommand(key_list=("plip",),
                                                profile="None")
        l = self.postTest("None")
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == mc

    # registerCreateMultiCommand with valid args and registerSetGlobalPrefix,
    # with profile None
    def test_registerCreateMultiCommand9(self):
        self.preTest()
        key = ("plip",)
        registerSetGlobalPrefix(key_list=("plup", "plop",), profile=None)
        mc = registerAndCreateEmptyMultiCommand(key_list=key,
                                                profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == mc

    # registerCreateMultiCommand with valid args and registerSetGlobalPrefix,
    # with profile not None
    def test_registerCreateMultiCommand10(self):
        self.preTest()
        key = ("plip",)
        registerSetGlobalPrefix(key_list=("plup", "plop",), profile="None")
        mc = registerAndCreateEmptyMultiCommand(key_list=key,
                                                profile="None")
        l = self.postTest("None")
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert key in l.cmdDict
        assert l.cmdDict[key] == mc

    # registerStopHelpTraversalAt with invalid key_list, with profile None
    def test_registerStopHelpTraversalAt1(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerStopHelpTraversalAt(key_list=object(), profile=None)
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")

    # registerStopHelpTraversalAt with invalid key_list, with profile not None
    def test_registerStopHelpTraversalAt2(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerStopHelpTraversalAt(key_list=object(), profile="None")
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")

    # registerStopHelpTraversalAt with valid args and NO predefined prefix,
    # with profile None
    def test_registerStopHelpTraversalAt3(self):
        self.preTest()
        key = ("kikoo", "lol",)
        registerStopHelpTraversalAt(key_list=key, profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert hasattr(l, "stoplist")
        assert isinstance(l.stoplist, set)
        assert key in l.stoplist

    # registerStopHelpTraversalAt with valid args and NO predefined prefix,
    # with profile not None
    def test_registerStopHelpTraversalAt4(self):
        self.preTest()
        key = ("kikoo", "lol",)
        registerStopHelpTraversalAt(key_list=key, profile="None")
        l = self.postTest("None")
        assert hasattr(l, "stoplist")
        assert isinstance(l.stoplist, set)
        assert key in l.stoplist

    # registerStopHelpTraversalAt with valid args and registerSetTempPrefix,
    # with profile None
    def test_registerStopHelpTraversalAt5(self):
        self.preTest()
        key = ("plup", "kikoo", "lol",)
        registerSetTempPrefix(key_list=("plup",), profile=None)
        registerStopHelpTraversalAt(key_list=("kikoo", "lol",), profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert hasattr(l, "stoplist")
        assert isinstance(l.stoplist, set)
        assert key in l.stoplist

    # registerStopHelpTraversalAt with valid args and registerSetTempPrefix,
    # with profile not None
    def test_registerStopHelpTraversalAt6(self):
        self.preTest()
        key = ("plup", "kikoo", "lol",)
        registerSetTempPrefix(key_list=("plup",), profile="None")
        registerStopHelpTraversalAt(key_list=("kikoo", "lol",), profile="None")
        l = self.postTest("None")
        assert hasattr(l, "stoplist")
        assert isinstance(l.stoplist, set)
        assert key in l.stoplist

    # registerStopHelpTraversalAt with valid args and registerSetGlobalPrefix,
    # with profile None
    def test_registerStopHelpTraversalAt7(self):
        self.preTest()
        key = ("kikoo", "lol",)
        registerSetGlobalPrefix(key_list=("plup",), profile=None)
        registerStopHelpTraversalAt(key_list=key, profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert hasattr(l, "stoplist")
        assert isinstance(l.stoplist, set)
        assert key in l.stoplist

    # registerStopHelpTraversalAt with valid args and registerSetGlobalPrefix,
    # with profile not None
    def test_registerStopHelpTraversalAt8(self):
        self.preTest()
        key = ("kikoo", "lol",)
        registerSetGlobalPrefix(key_list=("plup",), profile="None")
        registerStopHelpTraversalAt(key_list=key, profile="None")
        l = self.postTest("None")
        assert hasattr(l, "stoplist")
        assert isinstance(l.stoplist, set)
        assert key in l.stoplist


class TestCommandLoader(object):
    # # CommandLoader # #

    def setup_method(self, method):
        self.cl = CommandLoader(None)
        self.params = ParameterContainer()
        self.params.registerParameterManager(
            ENVIRONMENT_ATTRIBUTE_NAME,
            EnvironmentParameterManager(self.params))
        self.mltries = multiLevelTries()
        ctype = DefaultInstanceArgChecker.getArgCheckerInstance()
        self.params.environment.setParameter(
            ENVIRONMENT_LEVEL_TRIES_KEY,
            EnvironmentParameter(value=self.mltries,
                                 settings=EnvironmentGlobalSettings(
                                     transient=True,
                                     read_only=True,
                                     removable=False,
                                     checker=ctype)),
            local_param=False)

    # __init__, test without args
    def test_commandLoader1(self):
        CommandLoader(None)

    # addCmd, with temp prefix
    def test_commandLoaderAddCmd1(self):
        self.cl.TempPrefix = ("plop",)
        mc = self.cl.addCmd(("plip",),
                            MultiCommand())
        assert ("plop", "plip",) in self.cl.cmdDict
        assert self.cl.cmdDict[("plop", "plip",)] == mc

    # addCmd, whithout temp prefix
    def test_commandLoaderAddCmd2(self):
        self.cl.TempPrefix = None
        mc = self.cl.addCmd(("plip",),
                            MultiCommand())
        assert ("plip",) in self.cl.cmdDict
        assert self.cl.cmdDict[("plip",)] == mc

    # load, ENVIRONMENT_LEVEL_TRIES_KEY does not exist
    def test_commandLoaderLoad1(self):
        params = ParameterContainer()
        params.registerParameterManager(ENVIRONMENT_ATTRIBUTE_NAME,
                                        EnvironmentParameterManager(params))

        with pytest.raises(LoadException):
            self.cl.load(parameter_container=params, profile=None)

    # load, execute without command and without stopTraversal, no global prefix
    def test_commandLoaderLoad2(self):
        self.cl.load(parameter_container=self.params, profile=None)

    # load, execute without command and without stopTraversal, global
    # prefix defined
    def test_commandLoaderLoad3(self):
        self.cl.prefix = ("toto",)
        self.cl.load(parameter_container=self.params, profile=None)

    # load, try to insert an existing command, no global prefix
    def test_commandLoaderLoad4(self):
        key = ("plop", "plip",)
        self.mltries.insert(key, object())
        self.cl.addCmd(key,
                       MultiCommand())

        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params, profile=None)

    # load, try to insert an existing command, global prefix defined
    def test_commandLoaderLoad5(self):
        self.cl.prefix = ("toto",)
        self.mltries.insert(("toto", "plop", "plip",), object())
        self.cl.addCmd(("plop", "plip",),
                       UniCommand(process=proPro))

        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params, profile=None)

    # load, insert a not existing command, no global prefix
    def test_commandLoaderLoad6(self):
        key = ("plop", "plip",)
        uc = self.cl.addCmd(key,
                            UniCommand(process=proPro))
        self.cl.load(parameter_container=self.params, profile=None)
        search_result = self.mltries.searchNode(key, True)

        assert search_result is not None and search_result.isValueFound()
        assert uc is search_result.getValue()

    # load, insert a not existing command, global prefix defined
    def test_commandLoaderLoad7(self):
        self.cl.prefix = ("toto",)
        uc = self.cl.addCmd(("plop", "plip",),
                            UniCommand(process=proPro))
        self.cl.load(parameter_container=self.params, profile=None)
        search_result = self.mltries.searchNode(("toto", "plop", "plip",),
                                                True)

        assert search_result is not None and search_result.isValueFound()
        assert uc is search_result.getValue()

    # load, stopTraversal with command that does not exist, no global prefix
    def test_commandLoaderLoad8(self):
        self.cl.stoplist.add(("toto",))
        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params, profile=None)

    # load, stopTraversal with command that does not exist, global
    # prefix defined
    def test_commandLoaderLoad9(self):
        self.cl.prefix = ("plop",)
        self.cl.stoplist.add(("toto",))
        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params, profile=None)

    # load, stopTraversal, command exist, no global prefix
    def test_commandLoaderLoad10(self):
        key = ("toto", "plop", "plip",)
        self.mltries.insert(key, object())
        self.cl.stoplist.add(key)
        assert not self.mltries.isStopTraversal(key)
        self.cl.load(parameter_container=self.params, profile=None)
        assert self.mltries.isStopTraversal(key)

    # load, stopTraversal, command exist, global prefix defined
    def test_commandLoaderLoad11(self):
        key = ("toto", "plop", "plip",)
        self.cl.prefix = ("toto",)
        self.mltries.insert(key, object())
        self.cl.stoplist.add(("plop", "plip",))
        assert not self.mltries.isStopTraversal(key)
        self.cl.load(parameter_container=self.params, profile=None)
        assert self.mltries.isStopTraversal(key)

    # load, cmd exist, not raise if exist + not override
    def test_commandLoaderLoad12(self):
        key = ("toto", "plop", "plip",)
        self.mltries.insert(key, object())
        uc = self.cl.addCmd(key,
                            UniCommand(process=proPro))
        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params, profile=None)

    # load, cmd exist, raise if exist + not override
    def test_commandLoaderLoad13(self):
        key = ("toto", "plop", "plip",)
        self.mltries.insert(key, object())
        self.cl.addCmd(key,
                       UniCommand(process=proPro))
        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params, profile=None)

    # load, cmd exist, not raise if exist + override
    def test_commandLoaderLoad14(self):
        key = ("toto", "plop", "plip",)
        self.mltries.insert(key, object())
        uc = self.cl.addCmd(key,
                            UniCommand(process=proPro))
        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params, profile=None)

    # load, try to load an empty command
    def test_commandLoaderLoad15(self):
        self.cl.addCmd(("plop", "plip",),
                       MultiCommand())
        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params, profile=None)

    # unload, ENVIRONMENT_LEVEL_TRIES_KEY does not exist
    def test_commandLoaderUnload1(self):
        params = ParameterContainer()
        params.registerParameterManager(ENVIRONMENT_ATTRIBUTE_NAME,
                                        EnvironmentParameterManager(params))

        with pytest.raises(UnloadException):
            self.cl.unload(parameter_container=params, profile=None)

    # unload, nothing to do
    def test_commandLoaderUnload2(self):
        self.cl.loadedCommand = []
        self.cl.loadedStopTraversal = []
        self.cl.unload(parameter_container=self.params, profile=None)

    # unload, command does not exist
    def test_commandLoaderUnload3(self):
        self.cl.loadedCommand = []
        self.cl.loadedStopTraversal = []
        self.cl.loadedCommand.append(("toto", "plop", "plip",))
        with pytest.raises(ListOfException):
            self.cl.unload(parameter_container=self.params, profile=None)

    # unload, command exists
    def test_commandLoaderUnload4(self):
        key = ("toto", "plop", "plip",)
        self.cl.loadedCommand = []
        self.cl.loadedStopTraversal = []
        self.cl.loadedCommand.append(key)
        self.mltries.insert(key, object())

        self.cl.unload(parameter_container=self.params, profile=None)

        search_result = self.mltries.searchNode(key, True)

        assert search_result is None or not search_result.isValueFound()

    # unload, stopTraversal, path does not exist
    def test_commandLoaderUnload5(self):
        self.cl.loadedCommand = []
        self.cl.loadedStopTraversal = []
        self.cl.loadedStopTraversal.append(("toto", "plop", "plip",))
        self.cl.unload(parameter_container=self.params, profile=None)

    # unload, stopTraversal, path exists
    def test_commandLoaderUnload6(self):
        key = ("toto", "plop", "plip",)
        self.cl.loadedCommand = []
        self.cl.loadedStopTraversal = []
        self.cl.loadedStopTraversal.append(key)
        self.mltries.insert(key, object())
        self.mltries.setStopTraversal(key, True)

        self.cl.unload(parameter_container=self.params, profile=None)

        assert not self.mltries.isStopTraversal(key)
