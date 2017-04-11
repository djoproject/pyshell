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


import pyshell.addons.system as monkey_system
from pyshell.addons.system import loadAddonFun
from pyshell.addons.system import loadAddonOnStartUp
from pyshell.addons.system import loadAll
from pyshell.control import ControlCenter
from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADING
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.constants import STATE_UNLOADING
from pyshell.utils.exception import PyshellException

failed_loaders = None
fake_loaders = None


def setup_module(module):
    """
        little hack against the hardreload test from addon, pytest executes
        every files to collect the tests before to execute them.  At the same
        times, it will execute the import statement and load the loaders.  But
        the hardreload test will update the reloaded modules.  Executing these
        imports at test runing time allows to retrieve the last version of
        the _loaders

        system tests shouldnt care about retrieving the last version of the
        _loaders but the loadAddon methods will use this last version, so if
        we want to work with the same object in the test, the latest version
        is needed.
    """
    global fake_loaders, failed_loaders
    from pyshell.addons.test.failed_addon import _loaders as failed_loaders
    from pyshell.addons.test.fake_addon import _loaders as fake_loaders


NOTICE = None
ERROR = None
WARNING = None


def notice(msg):
    global NOTICE
    NOTICE = msg


def error(msg):
    global ERROR
    ERROR = msg


def warning(msg):
    global WARNING
    WARNING = msg


@pytest.fixture(autouse=True)
def retrieveOutput(monkeypatch):
    monkeypatch.setattr(monkey_system, "notice", notice)
    monkeypatch.setattr(monkey_system, "error", error)
    monkeypatch.setattr(monkey_system, "warning", warning)


class TestLoadAddonFun(object):
    def setup_method(self, method):
        global NOTICE, ERROR, WARNING
        NOTICE = ERROR = WARNING = None

        self.params = ControlCenter()

    def teardown_method(self, method):
        alist = []
        alist.append(fake_loaders)
        alist.append(failed_loaders)

        for loader in alist:
            if not loader.hasProfile(profile_name=None):
                continue

            profile_object = loader.getRootLoaderProfile(profile_name=None)

            if profile_object.isLoaded():
                loader.unload(container=self.params, profile_name=None)
            elif profile_object.isLoading():
                profile_object.setState(STATE_LOADED)
                profile_object.setState(STATE_UNLOADING)
                profile_object.setState(STATE_UNLOADED)

            loader.getInformations().setLastProfileUsed(None)

    def test_addonDoesNotExist(self):
        loadAddonFun(name="toto",
                     parameters=self.params,
                     profile_name=None)

        assert NOTICE is None
        assert ERROR is not None
        assert WARNING is None
        assert "fail to load" in ERROR

    def test_noLoaderInModule(self):
        loadAddonFun(name="os.path",
                     parameters=self.params,
                     profile_name=None)

        assert NOTICE is None
        assert ERROR is not None
        assert WARNING is None
        assert "no loader found" in ERROR

    def test_newAddon(self, monkeypatch):
        loadAddonFun(name="pyshell.addons.test.fake_addon",
                     parameters=self.params,
                     profile_name=None)

        assert NOTICE is not None
        assert ERROR is None
        assert WARNING is None
        assert "loaded !" in NOTICE

    def test_profileUnknown(self):
        loadAddonFun(name="pyshell.addons.test.fake_addon",
                     parameters=self.params,
                     profile_name="plop")
        assert NOTICE is None
        assert ERROR is not None
        assert WARNING is None
        assert "no profile named" in ERROR

    def test_addonAlreadyLoaded(self):
        loadAddonFun(name="pyshell.addons.test.fake_addon",
                     parameters=self.params,
                     profile_name=None)

        loadAddonFun(name="pyshell.addons.test.fake_addon",
                     parameters=self.params,
                     profile_name=None)
        assert WARNING is not None
        assert "is already loaded" in WARNING

    def test_addonAlreadyLoading(self):
        assert NOTICE is None
        assert ERROR is None
        assert WARNING is None

        loadAddonFun(name="pyshell.addons.test.fake_addon",
                     parameters=self.params,
                     profile_name=None)

        assert NOTICE is not None
        assert ERROR is None
        assert WARNING is None
        assert "pyshell.addons.test.fake_addon loaded !" in NOTICE

        addons = self.params.getAddonManager()
        loader = addons["pyshell.addons.test.fake_addon"]
        profile_object = loader.getRootLoaderProfile(profile_name=None)

        assert profile_object.isLoaded()
        loader.unload(container=self.params, profile_name=None)
        assert profile_object.isUnloaded()

        profile_object.setState(STATE_LOADING)

        loadAddonFun(name="pyshell.addons.test.fake_addon",
                     parameters=self.params,
                     profile_name=None)

        assert WARNING is not None
        assert "is loading !" in WARNING

    def test_anotherProfileIsAlreadyLoaded(self):
        loadAddonFun(name="pyshell.addons.test.fake_addon",
                     parameters=self.params,
                     profile_name=None)

        addons = self.params.getAddonManager()
        loader = addons["pyshell.addons.test.fake_addon"]
        loader.createProfile(profile_name="toto")

        loadAddonFun(name="pyshell.addons.test.fake_addon",
                     parameters=self.params,
                     profile_name="toto")

        assert ERROR is not None
        assert "profile 'default' is not unloaded" in ERROR

    def test_errorOnLoad(self):
        with pytest.raises(PyshellException):
            loadAddonFun(name="pyshell.addons.test.failed_addon",
                         parameters=self.params,
                         profile_name=None)

        assert NOTICE is None
        assert ERROR is None
        assert WARNING is not None
        assert "problems encountered during loading" in WARNING


class TestloadAddonOnStartUp(object):
    def setup_method(self, method):
        global NOTICE, ERROR, WARNING
        NOTICE = ERROR = WARNING = None
        self.params = ControlCenter()

    def teardown_method(self, method):
        alist = []
        alist.append(fake_loaders)
        alist.append(failed_loaders)

        for loader in alist:
            if not loader.hasProfile(profile_name=None):
                continue

            profile_object = loader.getRootLoaderProfile(profile_name=None)

            if profile_object.isLoaded():
                try:
                    loader.unload(container=self.params, profile_name=None)
                except:
                    pass
            elif profile_object.isLoading():
                profile_object.setState(STATE_LOADED)
                profile_object.setState(STATE_UNLOADING)
                profile_object.setState(STATE_UNLOADED)

            loader.getInformations().setLastProfileUsed(None)

    def test_noneAddonList(self):
        loadAddonOnStartUp(params=self.params,
                           addon_list_on_start_up=None,
                           profile_name=None)

    def test_emptyAddonList(self):
        list_env = EnvironmentParameter(value=[])
        loadAddonOnStartUp(params=self.params,
                           addon_list_on_start_up=list_env,
                           profile_name=None)

    def test_notEmptyListAndError(self):
        list_env = EnvironmentParameter(value=["toto"])
        loadAddonOnStartUp(params=self.params,
                           addon_list_on_start_up=list_env,
                           profile_name=None)
        assert NOTICE is None
        assert ERROR is not None
        assert WARNING is None

        assert "fail to load" in ERROR

    def test_notEmptyListAndSuccess(self):
        startup_list = []
        startup_list.append("pyshell.addons.test.fake_addon")
        list_env = EnvironmentParameter(value=startup_list)
        loadAddonOnStartUp(params=self.params,
                           addon_list_on_start_up=list_env,
                           profile_name=None)

    def test_notEmptyListAndAddonInManagerButNeverUsed(self):
        addons = self.params.getAddonManager()
        addons["pyshell.addons.test.fake_addon"] = fake_loaders
        startup_list = []
        startup_list.append("pyshell.addons.test.fake_addon")
        list_env = EnvironmentParameter(value=startup_list)
        loadAddonOnStartUp(params=self.params,
                           addon_list_on_start_up=list_env,
                           profile_name=None)

    def test_notEmptyListAndOneAddonIsAlreadyLoaded(self):
        loadAddonFun(name="pyshell.addons.test.fake_addon",
                     parameters=self.params,
                     profile_name=None)

        addons = self.params.getAddonManager()
        addons["pyshell.addons.test.fake_addon"] = fake_loaders
        startup_list = []
        startup_list.append("pyshell.addons.test.fake_addon")
        list_env = EnvironmentParameter(value=startup_list)
        loadAddonOnStartUp(params=self.params,
                           addon_list_on_start_up=list_env,
                           profile_name=None)

    def test_notEmptyListAndOneAddonHasErrorOnLoading(self):
        startup_list = []
        startup_list.append("pyshell.addons.test.failed_addon")
        list_env = EnvironmentParameter(value=startup_list)
        with pytest.raises(PyshellException):
            loadAddonOnStartUp(params=self.params,
                               addon_list_on_start_up=list_env,
                               profile_name=None)

        assert NOTICE is None
        assert ERROR is None
        assert WARNING is not None

        assert "problems encountered during loading" in WARNING


class TestLoadAll(object):
    def setup_method(self, method):
        global NOTICE, ERROR, WARNING
        NOTICE = ERROR = WARNING = None
        self.params = ControlCenter()

    def teardown_method(self, method):
        alist = []
        alist.append(fake_loaders)
        alist.append(failed_loaders)

        for loader in alist:
            if not loader.hasProfile(profile_name=None):
                continue

            profile_object = loader.getRootLoaderProfile(profile_name=None)

            if profile_object.isLoaded():
                try:
                    loader.unload(container=self.params, profile_name=None)
                except:
                    pass
            elif profile_object.isLoading():
                profile_object.setState(STATE_LOADED)
                profile_object.setState(STATE_UNLOADING)
                profile_object.setState(STATE_UNLOADED)

            loader.getInformations().setLastProfileUsed(None)

    def test_nothingLoaded(self):
        startup_list = []
        startup_list.append("pyshell.addons.test.fake_addon")
        startup_list.append("pyshell.addons.test.failed_addon")
        list_env = EnvironmentParameter(value=startup_list)

        with pytest.raises(PyshellException):
            loadAll(self.params, list_env, profile_name=None)

    def test_fakeAddonAlreadyLoaded(self):
        startup_list = []
        startup_list.append("pyshell.addons.test.fake_addon")
        list_env = EnvironmentParameter(value=startup_list)
        loadAddonOnStartUp(params=self.params,
                           addon_list_on_start_up=list_env,
                           profile_name=None)

        startup_list = []
        startup_list.append("pyshell.addons.test.fake_addon")
        startup_list.append("pyshell.addons.test.failed_addon")
        list_env = EnvironmentParameter(value=startup_list)

        with pytest.raises(PyshellException):
            loadAll(self.params, list_env, profile_name=None)
