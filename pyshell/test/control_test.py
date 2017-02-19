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

from threading import Thread
from threading import current_thread

import pytest

from pyshell.control import ControlCenter
from pyshell.control import MAIN_LEVEL
from pyshell.control import PROCEDURE_LEVEL
from pyshell.register.loader.environment import EnvironmentLoader
from pyshell.register.utils.addon import AddonLoader
from pyshell.utils.abstract.flushable import Flushable
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.constants import STATE_UNLOADING
from pyshell.utils.exception import DefaultPyshellException


class FakeFlushable(Flushable):
    def __init__(self, container):
        self.flushed = False

    def flush(self):
        self.flushed = True


class TestControlCenter(object):
    def test_controlCenter1(self):
        pc = ControlCenter()
        assert pc.isMainThread()
        assert pc.getCurrentId() == (current_thread().ident, "main",)

    # isMainThread, true
    def test_controlCenter16(self):
        pc = ControlCenter()
        assert pc.isMainThread()

    # isMainThread, false
    def test_controlCenter17(self):
        pc = ControlCenter()

        def testNotInMainThread(pc):
            assert not pc.isMainThread()

        t = Thread(target=testNotInMainThread, args=(pc,))
        t.start()
        t.join()

    def test_increment(self):
        pc = ControlCenter()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

        pc.incrementLevel()

        tid, level = pc.getCurrentId()
        assert level is PROCEDURE_LEVEL

    def test_decrement(self):
        pc = ControlCenter()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

        pc.decrementLevel()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

    def test_incrementThenDecrement(self):
        pc = ControlCenter()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

        pc.incrementLevel()

        tid, level = pc.getCurrentId()
        assert level is PROCEDURE_LEVEL

        pc.decrementLevel()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

    def test_twoConsecutiveIncrement(self):
        pc = ControlCenter()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

        pc.incrementLevel()

        tid, level = pc.getCurrentId()
        assert level is PROCEDURE_LEVEL

        with pytest.raises(DefaultPyshellException):
            pc.incrementLevel()

        tid, level = pc.getCurrentId()
        assert level is PROCEDURE_LEVEL

    def test_twoConsecutiveDecrement(self):
        pc = ControlCenter()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

        pc.decrementLevel()
        pc.decrementLevel()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

    def test_checkForSetGlobalParameterUnknownGroupName(self):
        pc = ControlCenter()
        with pytest.raises(DefaultPyshellException):
            pc.checkForSetGlobalParameter("unknown group_name", "loader_name")

    def test_checkForSetGlobalParameterUnknwonLoaderName(self):
        pc = ControlCenter()
        pc.getAddonManager()["group name"] = AddonLoader("group name")
        with pytest.raises(DefaultPyshellException):
            pc.checkForSetGlobalParameter("group name", "loader_name")

    def test_checkForSetGlobalParameterNoLoadedProfile(self):
        pc = ControlCenter()
        pc.getAddonManager()["group name"] = AddonLoader("group name")
        with pytest.raises(DefaultPyshellException):
            pc.checkForSetGlobalParameter("group name",
                                          ENVIRONMENT_ATTRIBUTE_NAME)

    def test_checkForSetGlobalParameterProfileNotInValidState(self):
        pc = ControlCenter()
        addon_loader = AddonLoader("group name")
        addon_loader.createProfile("test.profile")
        pc.getAddonManager()["group name"] = addon_loader
        addon_loader.load(container=pc, profile_name="test.profile")
        root_profile = addon_loader.getRootLoaderProfile("test.profile")
        root_profile.setState(STATE_UNLOADING)
        with pytest.raises(DefaultPyshellException):
            pc.checkForSetGlobalParameter("group name",
                                          ENVIRONMENT_ATTRIBUTE_NAME)

    def test_checkForSetGlobalParameterNotYetBinded(self):
        pc = ControlCenter()
        addon_loader = AddonLoader("group name")
        addon_loader.createProfile("test.profile")
        pc.getAddonManager()["group name"] = addon_loader
        addon_loader.load(container=pc, profile_name="test.profile")
        addon_loader.getRootLoaderProfile("test.profile")
        pc.checkForSetGlobalParameter("group name",
                                      ENVIRONMENT_ATTRIBUTE_NAME)
        assert addon_loader.isLoaderBindedToProfile(EnvironmentLoader,
                                                    "test.profile")

    def test_checkForSetGlobalParameterAlreadyBinded(self):
        pc = ControlCenter()
        addon_loader = AddonLoader("group name")
        addon_loader.createProfile("test.profile")
        pc.getAddonManager()["group name"] = addon_loader
        addon_loader.load(container=pc, profile_name="test.profile")
        addon_loader.getRootLoaderProfile("test.profile")
        pc.checkForSetGlobalParameter("group name",
                                      ENVIRONMENT_ATTRIBUTE_NAME)
        assert addon_loader.isLoaderBindedToProfile(EnvironmentLoader,
                                                    "test.profile")
        pc.checkForSetGlobalParameter("group name",
                                      ENVIRONMENT_ATTRIBUTE_NAME)

    def test_checkForUnsetGlobalParameterUnknownGroupName(self):
        pc = ControlCenter()
        with pytest.raises(DefaultPyshellException):
            pc.checkForUnsetGlobalParameter("unknown group_name",
                                            "loader_name")

    def test_checkForUnsetGlobalParameterNoLoadedProfile(self):
        pc = ControlCenter()
        pc.getAddonManager()["group name"] = AddonLoader("group name")
        with pytest.raises(DefaultPyshellException):
            pc.checkForUnsetGlobalParameter("group name",
                                            ENVIRONMENT_ATTRIBUTE_NAME)

    def test_checkForUnsetGlobalParameterProfileNotInValidState(self):
        pc = ControlCenter()
        addon_loader = AddonLoader("group name")
        addon_loader.createProfile("test.profile")
        pc.getAddonManager()["group name"] = addon_loader
        addon_loader.load(container=pc, profile_name="test.profile")
        root_profile = addon_loader.getRootLoaderProfile("test.profile")
        root_profile.setState(STATE_UNLOADING)
        root_profile.setState(STATE_UNLOADED)
        with pytest.raises(DefaultPyshellException):
            pc.checkForUnsetGlobalParameter("group name",
                                            ENVIRONMENT_ATTRIBUTE_NAME)

    def test_checkForUnsetGlobalParameterValidCase(self):
        pc = ControlCenter()
        addon_loader = AddonLoader("group name")
        addon_loader.createProfile("test.profile")
        pc.getAddonManager()["group name"] = addon_loader
        addon_loader.load(container=pc, profile_name="test.profile")
        addon_loader.getRootLoaderProfile("test.profile")
        pc.checkForUnsetGlobalParameter("group name",
                                        ENVIRONMENT_ATTRIBUTE_NAME)
