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

from pyshell.command.command import MultiCommand
from pyshell.register.command import registerAnInstanciatedCommand
from pyshell.register.command import registerAndCreateEmptyMultiCommand
from pyshell.register.command import registerCommand
from pyshell.register.command import registerResetTempPrefix
from pyshell.register.command import registerSetGlobalPrefix
from pyshell.register.command import registerSetTempPrefix
from pyshell.register.command import registerStopHelpTraversalAt
from pyshell.register.command import setCommandLoadPriority
from pyshell.register.command import setCommandUnloadPriority
from pyshell.register.loader.command import CommandLoader
from pyshell.register.profile.exception import RegisterException
from pyshell.register.utils.addon import AddonLoader
from pyshell.register.utils.module import getNearestModule
from pyshell.utils.constants import DEFAULT_PROFILE_NAME


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
        return mod

    def postTest(self, profile=None):
        mod = getNearestModule()
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        assert isinstance(_loaders, AddonLoader)
        assert _loaders.hasProfile(profile)
        assert _loaders.isLoaderBindedToProfile(CommandLoader, profile)

        profile_object = _loaders.getLoaderProfile(CommandLoader, profile)

        return profile_object

    def test_setCommandLoadPriorityDefaultProfile(self):
        self.preTest()
        setCommandLoadPriority(66)
        profile = self.postTest()
        assert profile.getLoadPriority() == 66

    def test_setCommandUnloadPriorityDefaultProfile(self):
        self.preTest()
        setCommandUnloadPriority(77)
        profile = self.postTest()
        assert profile.getUnloadPriority() == 77

    def test_setCommandLoadPriorityCustomProfile(self):
        self.preTest()
        setCommandLoadPriority(44, profile="plop")
        profile = self.postTest("plop")
        assert profile.getLoadPriority() == 44

    def test_setCommandUnloadPriorityCustomProfile(self):
        self.preTest()
        setCommandUnloadPriority(55, profile="plop")
        profile = self.postTest("plop")
        assert profile.getUnloadPriority() == 55

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
        l = self.postTest()
        assert l.getTempPrefix() is None

    # registerSetTempPrefix with invalid key_list, with profile not None
    def test_registerSetTempPrefix2(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerSetTempPrefix(key_list=object(), profile="None")
        l = self.postTest(profile="None")
        assert l.getTempPrefix() is None

    # registerSetTempPrefix with valid key_list, with profile None
    def test_registerSetTempPrefix3(self):
        self.preTest()
        registerSetTempPrefix(key_list=("tutu", "toto",), profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert l.getTempPrefix() == ("tutu", "toto",)

    # registerSetTempPrefix with valid key_list, with profile not None
    def test_registerSetTempPrefix4(self):
        self.preTest()
        registerSetTempPrefix(key_list=("tutu", "toto",), profile="None")
        l = self.postTest("None")
        assert l.getTempPrefix() == ("tutu", "toto",)

    # registerResetTempPrefix with temp prefix set, with profile None
    def test_registerResetTempPrefix1(self):
        self.preTest()
        registerSetTempPrefix(key_list=("tutu", "toto",), profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert l.getTempPrefix() == ("tutu", "toto",)
        registerResetTempPrefix(profile=None)
        assert l.getTempPrefix() is None

    # registerResetTempPrefix with temp prefix set, with profile not None
    def test_registerResetTempPrefix2(self):
        self.preTest()
        registerSetTempPrefix(key_list=("tutu", "toto",), profile="None")
        l = self.postTest("None")
        assert l.getTempPrefix() == ("tutu", "toto",)
        registerResetTempPrefix(profile="None")
        assert l.getTempPrefix() is None

    # registerResetTempPrefix without temp prefix set, with profile None
    def test_registerResetTempPrefix3(self):
        self.preTest()
        registerResetTempPrefix(profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert l.getTempPrefix() is None

    # registerResetTempPrefix without temp prefix set, with profile not None
    def test_registerResetTempPrefix4(self):
        self.preTest()
        registerResetTempPrefix(profile="None")
        l = self.postTest("None")
        assert l.getTempPrefix() is None

    # registerAnInstanciatedCommand with invalid command type, with
    # profile None
    def test_registerAnInstanciatedCommand1(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerAnInstanciatedCommand(key_list=("plop",),
                                          cmd="tutu",
                                          profile=None)
        l = self.postTest()
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert len(l.cmdDict) == 0

    # registerAnInstanciatedCommand with invalid command type, with profile
    # not None
    def test_registerAnInstanciatedCommand2(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerAnInstanciatedCommand(key_list=("plop",),
                                          cmd="tutu",
                                          profile="None")
        l = self.postTest(profile="None")
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert len(l.cmdDict) == 0

    # registerAnInstanciatedCommand with invalid key_list, with profile None
    def test_registerAnInstanciatedCommand3(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerAnInstanciatedCommand(key_list=object(),
                                          cmd=MultiCommand(),
                                          profile=None)
        l = self.postTest(profile=None)
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert len(l.cmdDict) == 0

    # registerAnInstanciatedCommand with invalid key_list, with profile
    # not None
    def test_registerAnInstanciatedCommand4(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerAnInstanciatedCommand(key_list=object(),
                                          cmd=MultiCommand(),
                                          profile="None")
        l = self.postTest(profile="None")
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert len(l.cmdDict) == 0

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
        l = self.postTest()
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert len(l.cmdDict) == 0

    # registerCommand with invalid key_list, with profile not None
    def test_registerCommand2(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerCommand(key_list=object(),
                            pre=None,
                            pro=proPro,
                            post=None,
                            profile="None")
        l = self.postTest(profile="None")
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert len(l.cmdDict) == 0

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
        l = self.postTest()
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert len(l.cmdDict) == 0

    # registerCreateMultiCommand with invalid key_list, with profile not None
    def test_registerCreateMultiCommand2(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerAndCreateEmptyMultiCommand(key_list=object(),
                                               profile="None")
        l = self.postTest(profile="None")
        assert hasattr(l, "cmdDict")
        assert isinstance(l.cmdDict, dict)
        assert len(l.cmdDict) == 0

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
        self.postTest()

    # registerStopHelpTraversalAt with invalid key_list, with profile not None
    def test_registerStopHelpTraversalAt2(self):
        self.preTest()
        with pytest.raises(RegisterException):
            registerStopHelpTraversalAt(key_list=object(), profile="None")
        self.postTest(profile="None")

    # registerStopHelpTraversalAt with valid args and NO predefined prefix,
    # with profile None
    def test_registerStopHelpTraversalAt3(self):
        self.preTest()
        key = ("kikoo", "lol",)
        registerStopHelpTraversalAt(key_list=key, profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert l.hasStopTraversal(key)

    # registerStopHelpTraversalAt with valid args and NO predefined prefix,
    # with profile not None
    def test_registerStopHelpTraversalAt4(self):
        self.preTest()
        key = ("kikoo", "lol",)
        registerStopHelpTraversalAt(key_list=key, profile="None")
        l = self.postTest("None")
        assert l.hasStopTraversal(key)

    # registerStopHelpTraversalAt with valid args and registerSetTempPrefix,
    # with profile None
    def test_registerStopHelpTraversalAt5(self):
        self.preTest()
        key = ("plup", "kikoo", "lol",)
        registerSetTempPrefix(key_list=("plup",), profile=None)
        registerStopHelpTraversalAt(key_list=("kikoo", "lol",), profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert l.hasStopTraversal(key)

    # registerStopHelpTraversalAt with valid args and registerSetTempPrefix,
    # with profile not None
    def test_registerStopHelpTraversalAt6(self):
        self.preTest()
        key = ("plup", "kikoo", "lol",)
        registerSetTempPrefix(key_list=("plup",), profile="None")
        registerStopHelpTraversalAt(key_list=("kikoo", "lol",), profile="None")
        l = self.postTest("None")
        assert l.hasStopTraversal(key)

    # registerStopHelpTraversalAt with valid args and registerSetGlobalPrefix,
    # with profile None
    def test_registerStopHelpTraversalAt7(self):
        self.preTest()
        key = ("kikoo", "lol",)
        registerSetGlobalPrefix(key_list=("plup",), profile=None)
        registerStopHelpTraversalAt(key_list=key, profile=None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        assert l.hasStopTraversal(key)

    # registerStopHelpTraversalAt with valid args and registerSetGlobalPrefix,
    # with profile not None
    def test_registerStopHelpTraversalAt8(self):
        self.preTest()
        key = ("kikoo", "lol",)
        registerSetGlobalPrefix(key_list=("plup",), profile="None")
        registerStopHelpTraversalAt(key_list=key, profile="None")
        l = self.postTest("None")
        assert l.hasStopTraversal(key)
