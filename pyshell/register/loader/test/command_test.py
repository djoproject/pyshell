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
from pyshell.register.exception import LoaderException
from pyshell.register.loader.command import CommandLoader
from pyshell.register.loader.exception import LoadException
from pyshell.register.loader.exception import UnloadException
from pyshell.register.profile.command import CommandLoaderProfile
from pyshell.system.container import ParameterContainer
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.environment import EnvironmentParameterManager
from pyshell.system.setting.environment import EnvironmentGlobalSettings
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.exception import ListOfException


def proPro():
    pass


class TestCommandLoaderMisc(object):
    # __init__, test without args
    def test_commandLoader1(self):
        with pytest.raises(LoaderException):
            CommandLoader()

    def test_profileCreation(self):
        profile = CommandLoader.createProfileInstance()
        assert isinstance(profile, CommandLoaderProfile)


class AbstractTestCommandLoader(object):
    # # CommandLoader # #

    def setup_method(self, method):
        self.cl = CommandLoader
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
        self.profile = CommandLoader.createProfileInstance()


class TestCommandLoaderLoad(AbstractTestCommandLoader):

    def test_noneContainer(self):
        with pytest.raises(LoadException):
            self.cl.load(parameter_container=None,
                         profile_object=self.profile)

    def test_containerWithoutEnv(self):
        container = ParameterContainer()
        with pytest.raises(LoadException):
            self.cl.load(parameter_container=container,
                         profile_object=self.profile)

    # load, ENVIRONMENT_LEVEL_TRIES_KEY does not exist
    def test_commandLoaderLoad1(self):
        params = ParameterContainer()
        params.registerParameterManager(ENVIRONMENT_ATTRIBUTE_NAME,
                                        EnvironmentParameterManager(params))

        with pytest.raises(LoadException):
            self.cl.load(parameter_container=params,
                         profile_object=self.profile)

    # load, execute without command and without stopTraversal, no global prefix
    def test_commandLoaderLoad2(self):
        self.cl.load(parameter_container=self.params,
                     profile_object=self.profile)

    # load, execute without command and without stopTraversal, global
    # prefix defined
    def test_commandLoaderLoad3(self):
        self.profile.setPrefix(("toto",))
        self.cl.load(parameter_container=self.params,
                     profile_object=self.profile)

    # load, try to insert an existing command, no global prefix
    def test_commandLoaderLoad4(self):
        key = ("plop", "plip",)
        self.mltries.insert(key, object())
        self.profile.addCmd(key,
                            MultiCommand())

        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params,
                         profile_object=self.profile)

    # load, try to insert an existing command, global prefix defined
    def test_commandLoaderLoad5(self):
        self.profile.setPrefix(("toto",))
        self.mltries.insert(("toto", "plop", "plip",), object())
        self.profile.addCmd(("plop", "plip",),
                            UniCommand(process=proPro))

        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params,
                         profile_object=self.profile)

    # load, insert a not existing command, no global prefix
    def test_commandLoaderLoad6(self):
        key = ("plop", "plip",)
        uc = self.profile.addCmd(key,
                                 UniCommand(process=proPro))
        self.cl.load(parameter_container=self.params,
                     profile_object=self.profile)
        search_result = self.mltries.searchNode(key, True)

        assert search_result is not None and search_result.isValueFound()
        assert uc is search_result.getValue()

    # load, insert a not existing command, global prefix defined
    def test_commandLoaderLoad7(self):
        self.profile.setPrefix(("toto",))
        uc = self.profile.addCmd(("plop", "plip",),
                                 UniCommand(process=proPro))
        self.cl.load(parameter_container=self.params,
                     profile_object=self.profile)
        search_result = self.mltries.searchNode(("toto", "plop", "plip",),
                                                True)

        assert search_result is not None and search_result.isValueFound()
        assert uc is search_result.getValue()

    # load, stopTraversal with command that does not exist, no global prefix
    def test_commandLoaderLoad8(self):
        self.profile.addStopTraversal(("toto",))
        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params,
                         profile_object=self.profile)

    # load, stopTraversal with command that does not exist, global
    # prefix defined
    def test_commandLoaderLoad9(self):
        self.profile.setPrefix(("plop",))
        self.profile.addStopTraversal(("toto",))
        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params,
                         profile_object=self.profile)

    # load, stopTraversal, command exist, no global prefix
    def test_commandLoaderLoad10(self):
        key = ("toto", "plop", "plip",)
        self.mltries.insert(key, object())
        self.profile.addStopTraversal(key)
        assert not self.mltries.isStopTraversal(key)
        self.cl.load(parameter_container=self.params,
                     profile_object=self.profile)
        assert self.mltries.isStopTraversal(key)

    # load, stopTraversal, command exist, global prefix defined
    def test_commandLoaderLoad11(self):
        key = ("toto", "plop", "plip",)
        self.profile.setPrefix(("toto",))
        self.mltries.insert(key, object())
        self.profile.addStopTraversal(("plop", "plip",))
        assert not self.mltries.isStopTraversal(key)
        self.cl.load(parameter_container=self.params,
                     profile_object=self.profile)
        assert self.mltries.isStopTraversal(key)

    # load, cmd exist, not raise if exist + not override
    def test_commandLoaderLoad12(self):
        key = ("toto", "plop", "plip",)
        self.mltries.insert(key, object())
        self.profile.addCmd(key, UniCommand(process=proPro))
        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params,
                         profile_object=self.profile)

    # load, cmd exist, raise if exist + not override
    def test_commandLoaderLoad13(self):
        key = ("toto", "plop", "plip",)
        self.mltries.insert(key, object())
        self.profile.addCmd(key,
                            UniCommand(process=proPro))
        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params,
                         profile_object=self.profile)

    # load, cmd exist, not raise if exist + override
    def test_commandLoaderLoad14(self):
        key = ("toto", "plop", "plip",)
        self.mltries.insert(key, object())
        self.profile.addCmd(key, UniCommand(process=proPro))
        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params,
                         profile_object=self.profile)

    # load, try to load an empty command
    def test_commandLoaderLoad15(self):
        self.profile.addCmd(("plop", "plip",),
                            MultiCommand())
        with pytest.raises(ListOfException):
            self.cl.load(parameter_container=self.params,
                         profile_object=self.profile)

    def test_stopTraversalAlreadyExist(self):
        key = ("toto", "plop", "plip",)
        self.profile.addCmd(key, UniCommand(process=proPro))
        self.profile.addStopTraversal(("toto",))
        self.mltries.insert(("toto", "plop", "titi",), object())
        self.mltries.setStopTraversal(("toto",), True)
        self.cl.load(parameter_container=self.params,
                     profile_object=self.profile)


class TestCommandLoaderUnload(AbstractTestCommandLoader):
    def test_noneContainer(self):
        with pytest.raises(UnloadException):
            self.cl.unload(parameter_container=None,
                           profile_object=self.profile)

    def test_containerWithoutEnv(self):
        container = ParameterContainer()
        with pytest.raises(UnloadException):
            self.cl.unload(parameter_container=container,
                           profile_object=self.profile)

    # unload, ENVIRONMENT_LEVEL_TRIES_KEY does not exist
    def test_commandLoaderUnload1(self):
        params = ParameterContainer()
        params.registerParameterManager(ENVIRONMENT_ATTRIBUTE_NAME,
                                        EnvironmentParameterManager(params))

        with pytest.raises(UnloadException):
            self.cl.unload(parameter_container=params,
                           profile_object=self.profile)

    # unload, nothing to do
    def test_commandLoaderUnload2(self):
        self.profile.loadedCommand = []
        self.profile.loadedStopTraversal = []
        self.cl.unload(parameter_container=self.params,
                       profile_object=self.profile)

    # unload, command does not exist
    def test_commandLoaderUnload3(self):
        self.profile.loadedCommand = []
        self.profile.loadedStopTraversal = []
        self.profile.loadedCommand.append(("toto", "plop", "plip",))
        with pytest.raises(ListOfException):
            self.cl.unload(parameter_container=self.params,
                           profile_object=self.profile)

    # unload, command exists
    def test_commandLoaderUnload4(self):
        key = ("toto", "plop", "plip",)
        self.profile.loadedCommand = []
        self.profile.loadedStopTraversal = []
        self.profile.loadedCommand.append(key)
        self.mltries.insert(key, object())

        self.cl.unload(parameter_container=self.params,
                       profile_object=self.profile)

        search_result = self.mltries.searchNode(key, True)

        assert search_result is None or not search_result.isValueFound()

    # unload, stopTraversal, path does not exist
    def test_commandLoaderUnload5(self):
        self.profile.loadedCommand = []
        self.profile.loadedStopTraversal = []
        self.profile.loadedStopTraversal.append(("toto", "plop", "plip",))
        self.cl.unload(parameter_container=self.params,
                       profile_object=self.profile)

    # unload, stopTraversal, path exists
    def test_commandLoaderUnload6(self):
        key = ("toto", "plop", "plip",)
        self.profile.loadedCommand = []
        self.profile.loadedStopTraversal = []
        self.profile.loadedStopTraversal.append(key)
        self.mltries.insert(key, object())
        self.mltries.setStopTraversal(key, True)

        self.cl.unload(parameter_container=self.params,
                       profile_object=self.profile)

        assert not self.mltries.isStopTraversal(key)
