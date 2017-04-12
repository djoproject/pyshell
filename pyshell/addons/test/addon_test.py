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

import pyshell.addons.addon as monkey_addon
from pyshell.addons.addon import addOnStartUp
from pyshell.addons.addon import downAddonInList
from pyshell.addons.addon import formatState
from pyshell.addons.addon import getAddonInformation
from pyshell.addons.addon import hardReload
from pyshell.addons.addon import listAddonFun
from pyshell.addons.addon import listOnStartUp
from pyshell.addons.addon import removeOnStartUp
from pyshell.addons.addon import setAddonPositionInList
from pyshell.addons.addon import unloadAddon
from pyshell.addons.addon import upAddonInList
from pyshell.addons.system import _loaders as _system_loaders
from pyshell.addons.test.failed_addon import RaisingOnLoadLoaded
from pyshell.addons.test.failed_addon import _loaders as _failers
from pyshell.addons.test.fake_addon import _loaders
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.profile.default import DefaultProfile
from pyshell.register.profile.root import RootProfile
from pyshell.system.manager.parent import ParentManager
from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.system.setting.environment import EnvironmentGlobalSettings
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E
from pyshell.utils.constants import STATE_LOADING
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.constants import STATE_UNLOADED_E
from pyshell.utils.constants import STATE_UNLOADING
from pyshell.utils.exception import ListOfException
from pyshell.utils.exception import PyshellException


class TestFormatState(object):
    def test_loadedWithoutError(self):
        p = RootProfile()
        p.setState(STATE_LOADING)
        p.setState(STATE_LOADED)
        assert "loaded" in formatState(p)

    def test_loadedWithError(self):
        p = RootProfile()
        p.setState(STATE_LOADING)
        p.setState(STATE_LOADED_E)
        assert "loaded with error" in formatState(p)

    def test_loadingWithoutError(self):
        p = RootProfile()
        p.setState(STATE_LOADING)
        assert "loading" in formatState(p)

    def test_unloadedWithoutError(self):
        p = RootProfile()
        p.setState(STATE_LOADING)
        p.setState(STATE_LOADED)
        p.setState(STATE_UNLOADING)
        p.setState(STATE_UNLOADED)
        assert "unloaded" in formatState(p)

    def test_unloadedWithError(self):
        p = RootProfile()
        p.setState(STATE_LOADING)
        p.setState(STATE_LOADED)
        p.setState(STATE_UNLOADING)
        p.setState(STATE_UNLOADED_E)
        assert "unloaded with error" in formatState(p)

    def test_unloadingWithoutError(self):
        p = RootProfile()
        p.setState(STATE_LOADING)
        p.setState(STATE_LOADED)
        p.setState(STATE_UNLOADING)
        assert "unloading" in formatState(p)

    def test_noStateWithoutError(self):
        p = RootProfile()
        assert "unknown state" in formatState(p)


class TestListAddonFun(object):
    def setup_method(self, method):
        self.params = ParentManager()
        self.addons = {"pyshell.addons.test.fake_addon": _loaders}

    def teardown_method(self, method):
        profile_object = _loaders.getRootLoaderProfile(profile_name=None)

        if profile_object.isLoaded():
            _loaders.unload(self.params)

    def test_noAddonLoaded(self):
        result = listAddonFun({})

        s = set()
        for i in range(1, len(result)):
            line = result[i]
            assert len(line) is 3
            assert line[0] not in s
            s.add(line[0])
            assert "none" in line[1]
            assert "-" in line[2]

    def test_addonInManagerButNeverUsed(self):
        result = listAddonFun(self.addons)
        assert len(result) > 1
        assert len(result[0]) is 3
        assert "Addon name" in result[0][0]
        assert "Last profile used" in result[0][1]
        assert "State" in result[0][2]

        found = False
        s = set()
        for i in range(1, len(result)):
            line = result[i]
            assert len(line) is 3
            assert line[0] not in s
            s.add(line[0])
            assert "none" in line[1]
            assert "-" in line[2]

            if "pyshell.addons.test.fake_addon" not in line[0]:
                found = True

        assert found

    def test_addonInManagetAndLoaded(self):
        _loaders.load(self.params)
        result = listAddonFun(self.addons)
        assert len(result) > 1
        assert len(result[0]) is 3
        assert "Addon name" in result[0][0]
        assert "Last profile used" in result[0][1]
        assert "State" in result[0][2]

        found = False
        s = set()
        for i in range(1, len(result)):
            line = result[i]
            assert len(line) is 3
            assert line[0] not in s
            s.add(line[0])

            if "pyshell.addons.test.fake_addon" not in line[0]:
                assert "none" in line[1]
                assert "-" in line[2]
                found = True
            else:
                assert "default" in line[1]
                assert "loaded" in line[2]
        assert found

    def test_emptyResult(self, monkeypatch):
        def fakeExist(path):
            return False

        monkeypatch.setattr(monkey_addon.os.path, 'exists', fakeExist)
        result = listAddonFun({})
        assert result == [("No addon available",)]

    def test_systemAddonInManagerButNeverUsed(self):
        self.addons.clear()
        self.addons["pyshell.addons.system"] = _system_loaders
        result = listAddonFun(self.addons)
        assert len(result) > 1
        assert len(result[0]) is 3
        assert "Addon name" in result[0][0]
        assert "Last profile used" in result[0][1]
        assert "State" in result[0][2]

        found = False
        s = set()
        for i in range(1, len(result)):
            line = result[i]
            assert len(line) is 3
            assert line[0] not in s
            s.add(line[0])
            assert "none" in line[1]
            assert "-" in line[2]

            if "pyshell.addons.system" not in line[0]:
                found = True

        assert found


class TestUnloadAddon(object):
    def setup_method(self, method):
        self.params = ParentManager()
        self.addons = {}

    def test_notInDico(self, capsys):
        unloadAddon("toto", self.addons, self.params, profile_name=None)
        out, err = capsys.readouterr()
        assert "unknown addon" in out

    def test_successCase(self, capsys):
        _loaders.load(self.params)
        self.addons["pyshell.addons.test.fake_addon"] = _loaders
        unloadAddon("pyshell.addons.test.fake_addon",
                    self.addons,
                    self.params,
                    profile_name=None)
        out, err = capsys.readouterr()
        assert "unloaded !" in out


class RaisingOnUnloadLoaded(AbstractLoader):
    @staticmethod
    def createProfileInstance(root_profile):
        return DefaultProfile(root_profile)

    @classmethod
    def unload(cls, profile_object, parameter_container):
        raise Exception("ooops unload")


class RaisingListOnUnloadLoaded(AbstractLoader):
    @staticmethod
    def createProfileInstance(root_profile):
        return DefaultProfile(root_profile)

    @classmethod
    def unload(cls, profile_object, parameter_container):
        e = ListOfException()
        e.addException(Exception("ooops unload 1"))
        e.addException(Exception("ooops unload 2"))
        raise e


class TestHardReload(object):
    def setup_method(self, method):
        self.params = ParentManager()
        self.addons = {}

    def teardown_method(self, method):
        global _loaders, _failers
        addons = {"pyshell.addons.test.fake_addon": _loaders,
                  "pyshell.addons.test.failed_addon": _failers}

        for name in addons.keys():

            if name in self.addons:
                assert self.addons[name] is not addons[name]
                l = self.addons[name]
            else:
                l = addons[name]

            if name == "pyshell.addons.test.fake_addon":
                _loaders = l
            else:
                _failers = l

            profile_object = l.getRootLoaderProfile(profile_name=None)

            if profile_object.isLoaded():
                l.unload(self.params)

            assert profile_object.isUnloaded() or profile_object.hasNoState()

    def test_notInManagerAndNotAnExistingModule(self, capsys):
        hardReload("pyshell.plop.plip", self.addons, self.params)
        out, err = capsys.readouterr()
        assert "fail to retrieve addon module" in out

    def test_inManagerButNotLoaded(self, capsys):
        self.addons["pyshell.addons.test.fake_addon"] = _loaders
        hardReload("pyshell.addons.test.fake_addon", self.addons, self.params)
        out, err = capsys.readouterr()
        assert "hard reloaded !" in out

    def test_inManagerAndLoaded(self, capsys):
        _loaders.load(self.params)
        self.addons["pyshell.addons.test.fake_addon"] = _loaders
        hardReload("pyshell.addons.test.fake_addon", self.addons, self.params)
        out, err = capsys.readouterr()
        assert "hard reloaded !" in out

    def test_inManagerAndLoadedWithErrorOnUnload(self, capsys):
        _loaders.load(self.params)
        _loaders.bindLoaderToProfile(RaisingOnUnloadLoaded, None)
        self.addons["pyshell.addons.test.fake_addon"] = _loaders
        hardReload("pyshell.addons.test.fake_addon", self.addons, self.params)
        out, err = capsys.readouterr()
        expected = "error on addon 'pyshell.addons.test.fake_addon' unloading"
        assert expected in out
        assert "hard reloaded !" in out

    def test_inManagerAndLoadedWithErrorOnLoad(self, capsys):
        _failers.unbindLoaderToProfile(RaisingOnLoadLoaded, None)
        _failers.load(self.params)
        self.addons["pyshell.addons.test.failed_addon"] = _failers
        with pytest.raises(PyshellException):
            hardReload("pyshell.addons.test.failed_addon",
                       self.addons,
                       self.params)
        out, err = capsys.readouterr()
        assert "problems encountered during loading" in out

    def test_noLoaderFoundAfterReload(self, capsys):
        hardReload("os.path", self.addons, self.params)
        out, err = capsys.readouterr()
        assert "no loader found" in out


class TestGetAddonInformation(object):
    def setup_method(self, method):
        self.params = ParentManager()
        self.addons = {}
        _loaders.load(self.params)
        self.addons["pyshell.addons.test.fake_addon"] = _loaders

        settings = EnvironmentGlobalSettings(transient=False,
                                             read_only=False,
                                             removable=False,
                                             checker=IntegerArgChecker(0))

        self.tab_size = EnvironmentParameter(value=4, settings=settings)

    def teardown_method(self, method):
        if _loaders.isLoaderBindedToProfile(RaisingOnUnloadLoaded, None):
            _loaders.unbindLoaderToProfile(RaisingOnUnloadLoaded, None)

        if _loaders.isLoaderBindedToProfile(RaisingListOnUnloadLoaded, None):
            _loaders.unbindLoaderToProfile(RaisingListOnUnloadLoaded, None)

        profile_object = _loaders.getRootLoaderProfile(profile_name=None)

        if profile_object.isLoaded():
            _loaders.unload(self.params)

    def test_moduleDoesNotExist(self, capsys):
        getAddonInformation("pyshell.toto.titi",
                            self.addons,
                            self.tab_size)

        out, err = capsys.readouterr()
        assert "fail to import addon" in out

    def test_noLoaderInModule(self, capsys):
        getAddonInformation("os.path",
                            self.addons,
                            self.tab_size)

        out, err = capsys.readouterr()
        assert "no loader found" in out

    def test_loaded(self):
        result = getAddonInformation("pyshell.addons.test.fake_addon",
                                     self.addons,
                                     self.tab_size)
        assert len(result) is 6
        assert result[0] == "Addon 'pyshell.addons.test.fake_addon'"
        assert result[1] == "    Profile 'default': loaded"
        assert result[2] == "        Loader 'EnvironmentLoader' (status=ok)"
        assert result[3] == "            Content count=<1>:"
        assert result[4] == "                env.fake.nothing"
        assert result[5] == ""

    def test_notLoadedAndNotRegistered(self):
        _loaders.unload(self.params)
        del self.addons["pyshell.addons.test.fake_addon"]
        result = getAddonInformation("pyshell.addons.test.fake_addon",
                                     self.addons,
                                     self.tab_size)
        assert len(result) is 6
        assert result[0] == "Addon 'pyshell.addons.test.fake_addon'"
        assert result[1] == "    Profile 'default': unloaded"
        assert result[2] == "        Loader 'EnvironmentLoader' (status=ok)"
        assert result[3] == "            Content count=<1>:"
        assert result[4] == "                env.fake.nothing"
        assert result[5] == ""

    def test_singleException(self):
        _loaders.bindLoaderToProfile(RaisingOnUnloadLoaded, None)
        try:
            _loaders.unload(self.params)
        except:
            pass
        result = getAddonInformation("pyshell.addons.test.fake_addon",
                                     self.addons,
                                     self.tab_size)

        assert len(result) is 18
        assert result[0] == "Addon 'pyshell.addons.test.fake_addon'"
        assert result[1] == "    Profile 'default': unloaded with error"
        assert result[2] == "        Loader 'EnvironmentLoader' (status=ok)"
        assert result[3] == "            Content count=<1>:"
        assert result[4] == "                env.fake.nothing"
        assert result[5] == ""
        assert result[6] == ("        Loader 'RaisingOnUnloadLoaded' (status="
                             "error)")
        assert result[7] == "            Error(s) count=<1>:"
        assert result[8] == "                * ooops unload"
        assert result[9] == ""
        assert result[10] == ("                Traceback (most recent call "
                              "last):")
        expected = ('pyshell/register/loader/internal.py", line 59, in '
                    '_innerLoad')
        assert expected in result[11]
        assert result[12] == ("                    meth_to_call(loader_profile"
                              ", parameter_container)")
        expected = 'pyshell/addons/test/addon_test.py", line 234, in unload'
        assert expected in result[13]
        assert result[14] == ('                    raise Exception("ooops '
                              'unload")')
        assert result[15] == "                Exception: ooops unload"
        assert result[16] == "                "
        assert result[17] == ""

    def test_listOfException(self):
        _loaders.bindLoaderToProfile(RaisingListOnUnloadLoaded, None)
        try:
            _loaders.unload(self.params)
        except Exception:
            pass
        result = getAddonInformation("pyshell.addons.test.fake_addon",
                                     self.addons,
                                     self.tab_size)

        assert len(result) is 11
        assert result[0] == "Addon 'pyshell.addons.test.fake_addon'"
        assert result[1] == "    Profile 'default': unloaded with error"
        assert result[2] == "        Loader 'EnvironmentLoader' (status=ok)"
        assert result[3] == "            Content count=<1>:"
        assert result[4] == "                env.fake.nothing"
        assert result[5] == ""
        assert result[6] == ("        Loader 'RaisingListOnUnloadLoaded' "
                             "(status=error)")
        assert result[7] == "            Error(s) count=<2>:"
        assert result[8] == "                * ooops unload 1"
        assert result[9] == "                * ooops unload 2"
        assert result[10] == ""


class TestAddonOnStartup(object):
    def setup_method(self, method):
        liste = ["toto", "titi"]
        self.startup_list = EnvironmentParameter(value=liste)

    def test_addOnStartUpNotAModule(self, capsys):
        addOnStartUp("pyshell.toto.titi", self.startup_list)
        out, err = capsys.readouterr()
        assert "fail to import addon" in out

    def test_addOnStartUpNoLoader(self, capsys):
        addOnStartUp("os.path", self.startup_list)
        out, err = capsys.readouterr()
        assert "no loader found" in out

    def test_addOnStartUpAlreadyInTheList(self):
        val = ["pyshell.addons.test.fake_addon"]
        startup_list = EnvironmentParameter(value=val)
        addOnStartUp("pyshell.addons.test.fake_addon", startup_list)
        assert startup_list.getValue() == ["pyshell.addons.test.fake_addon"]

    def test_addOnStartUpNotInTheList(self):
        addOnStartUp("pyshell.addons.test.fake_addon", self.startup_list)
        result = self.startup_list.getValue()
        assert result == ["toto", "titi", "pyshell.addons.test.fake_addon"]

    def test_removeOnStartUpNotInTheList(self):
        removeOnStartUp("plop", self.startup_list)
        assert self.startup_list.getValue() == ["toto", "titi"]

    def test_removeOnStartUpInTheList(self):
        removeOnStartUp("toto", self.startup_list)
        assert self.startup_list.getValue() == ["titi"]

    def test_listOnStartUpEmptyList(self):
        result = listOnStartUp(EnvironmentParameter(value=[]))
        assert len(result) == 0

    def test_listOnStartUpNotEmptyList(self):
        result = listOnStartUp(self.startup_list)
        assert len(result) == 3

        assert len(result[0]) == 2
        assert "Order" in result[0][0]
        assert "Addon name" in result[0][1]

        assert len(result[1]) == 2
        assert result[1][0] == "0"
        assert result[1][1] == "toto"

        assert len(result[2]) == 2
        assert result[2][0] == "1"
        assert result[2][1] == "titi"

    def test_downAddonInListNotInList(self):
        with pytest.raises(Exception):
            downAddonInList("plop", self.startup_list)
        assert self.startup_list.getValue() == ["toto", "titi"]

    def test_downAddonInListAlreadyAtTheEnd(self):
        downAddonInList("titi", self.startup_list)
        assert self.startup_list.getValue() == ["toto", "titi"]

    def test_downAddonInListNotAtTheEnd(self):
        downAddonInList("toto", self.startup_list)
        assert self.startup_list.getValue() == ["titi", "toto"]

    def test_upAddonInListNotInList(self):
        with pytest.raises(Exception):
            upAddonInList("plop", self.startup_list)
        assert self.startup_list.getValue() == ["toto", "titi"]

    def test_upAddonInListAlreadyAtTheBeginning(self):
        upAddonInList("toto", self.startup_list)
        assert self.startup_list.getValue() == ["toto", "titi"]

    def test_upAddonInListNotAtTheBeginning(self):
        upAddonInList("titi", self.startup_list)
        assert self.startup_list.getValue() == ["titi", "toto"]

    def test_setAddonPositionInListNotInList(self):
        with pytest.raises(Exception):
            setAddonPositionInList("plop", 0, self.startup_list)
        assert self.startup_list.getValue() == ["toto", "titi"]

    def test_setAddonPositionInListNegativIndex(self):
        setAddonPositionInList("titi", -23, self.startup_list)
        assert self.startup_list.getValue() == ["titi", "toto"]

    def test_setAddonPositionInListTooBigIndex(self):
        setAddonPositionInList("toto", 4000, self.startup_list)
        assert self.startup_list.getValue() == ["titi", "toto"]

    def test_setAddonPositionInListNormalCase(self):
        setAddonPositionInList("toto", 1, self.startup_list)
        assert self.startup_list.getValue() == ["titi", "toto"]
