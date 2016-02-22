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

from pyshell.system.settings import GlobalSettings
from pyshell.system.settings import LocalSettings
from pyshell.system.settings import Settings
from pyshell.utils.exception import ParameterException


class TestSettings(object):

    def setup_method(self, method):
        self.setHash = hash(Settings())

    # # Settings # #

    def test_settings1(self):
        s = Settings()

        assert not s.isReadOnly()
        assert s.isRemovable()
        assert s.isTransient()
        assert s.getProperties() == (("removable", True, ),
                                     ("readOnly", False, ),
                                     ("transient", True, ))
        assert hash(s) == self.setHash

    def test_settings2(self):
        s = Settings(read_only=False, removable=False)

        assert not s.isReadOnly()
        assert s.isRemovable()
        assert s.isTransient()
        assert s.getProperties() == (("removable", True, ),
                                     ("readOnly", False, ),
                                     ("transient", True, ))
        assert hash(s) == self.setHash

    def test_settings3(self):
        s = Settings(read_only=True, removable=True)

        assert not s.isReadOnly()
        assert s.isRemovable()
        assert s.isTransient()
        assert s.getProperties() == (("removable", True, ),
                                     ("readOnly", False, ),
                                     ("transient", True, ))
        assert hash(s) == self.setHash

    def test_settings4(self):
        s = Settings()
        s.setReadOnly(True)
        assert not s.isReadOnly()
        assert hash(s) == self.setHash

    def test_settings5(self):
        s = Settings()
        s.setReadOnly(False)
        assert not s.isReadOnly()
        assert hash(s) == self.setHash

    def test_settings6(self):
        s = Settings()
        s.setTransient(True)
        assert s.isTransient()
        assert hash(s) == self.setHash

    def test_settings7(self):
        s = Settings()
        s.setTransient(False)
        assert s.isTransient()
        assert hash(s) == self.setHash

    def test_settings8(self):
        s = Settings()
        s.setRemovable(True)
        assert s.isRemovable()
        assert hash(s) == self.setHash

    def test_settings9(self):
        s = Settings()
        s.setRemovable(False)
        assert s.isRemovable()
        assert hash(s) == self.setHash

    def test_settings10(self):
        s = Settings()
        assert s.getLoaders() is None
        s.addLoader("plop")
        assert s.getLoaders() is None
        assert hash(s) == self.setHash

    def test_settings11(self):
        s = Settings()
        s.mergeFromPreviousSettings(Settings())
        assert s.getLoaders() is None
        assert hash(s) == self.setHash

    # # LocalSettings # #

    def test_localSettings1(self):
        ls = LocalSettings()
        assert ls.isRemovable()
        assert not ls.isReadOnly()

    def test_localSettings2(self):
        ls = LocalSettings(read_only=True, removable=True)
        assert ls.isRemovable()
        assert ls.isReadOnly()

    def test_localSettings3(self):
        ls = LocalSettings(read_only=False, removable=False)
        assert not ls.isRemovable()
        assert not ls.isReadOnly()

    def test_localSettings4(self):
        ls = LocalSettings()
        ls.setRemovable(True)
        assert ls.isRemovable()

    def test_localSettings5(self):
        ls = LocalSettings()
        ls.setRemovable(False)
        assert not ls.isRemovable()

    def test_localSettings6(self):
        ls = LocalSettings()
        with pytest.raises(ParameterException):
            ls.setRemovable("plop")

    def test_localSettings7(self):
        ls = LocalSettings(read_only=True)
        with pytest.raises(ParameterException):
            ls.setRemovable(True)

    def test_localSettings8(self):
        ls = LocalSettings()
        ls.setReadOnly(True)
        assert ls.isReadOnly()

    def test_localSettings9(self):
        ls = LocalSettings()
        ls.setReadOnly(False)
        assert not ls.isReadOnly()

    def test_localSettings10(self):
        ls = LocalSettings()
        with pytest.raises(ParameterException):
            ls.setReadOnly("plop")

    def test_localSettings11(self):
        ls = LocalSettings(read_only=True)
        with pytest.raises(ParameterException):
            ls._raiseIfReadOnly()

    def test_localSettings12(self):
        ls = LocalSettings(read_only=True)
        with pytest.raises(ParameterException):
            ls._raiseIfReadOnly("plop")

    def test_localSettings13(self):
        ls = LocalSettings(read_only=True)
        with pytest.raises(ParameterException):
            ls._raiseIfReadOnly("plop", "plip")

    # # GlobalSettings # #

    def test_globalSettings1(self):
        gs = GlobalSettings()
        assert not gs.isReadOnly()
        assert gs.isRemovable()
        assert not gs.isTransient()

    def test_globalSettings2(self):
        gs = GlobalSettings(read_only=False, removable=False, transient=False)
        assert not gs.isReadOnly()
        assert not gs.isRemovable()
        assert not gs.isTransient()

    def test_globalSettings3(self):
        gs = GlobalSettings(read_only=True, removable=True, transient=True)
        assert gs.isReadOnly()
        assert gs.isRemovable()
        assert gs.isTransient()

    def test_globalSettings4(self):
        gs = GlobalSettings()
        gs.setTransient(True)
        assert gs.isTransient()

    def test_globalSettings5(self):
        gs = GlobalSettings()
        gs.setTransient(False)
        assert not gs.isTransient()

    def test_globalSettings6(self):
        gs = GlobalSettings()
        with pytest.raises(ParameterException):
            gs.setTransient("plop")

    def test_globalSettings7(self):
        gs = GlobalSettings(read_only=True)
        with pytest.raises(ParameterException):
            gs.setTransient(True)

    def test_globalSettings8(self):
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        assert gs.isEqualToStartingHash("toto")

    def test_globalSettings9(self):
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        with pytest.raises(ParameterException):
            gs.setStartingPoint("toto", "tutu", "tata")

    def test_globalSettings10(self):
        gs = GlobalSettings()
        assert gs.getLoaders() is None
        gs.addLoader("plop")
        gs.addLoader("plop")
        gs.addLoader("plop")
        gs.addLoader("plup")
        assert tuple(sorted(gs.getLoaders())) == ("plop", "plup")

    # mergeFromPreviousSettings, settings is None
    def test_globalSettings11(self):
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        gs.addLoader("plop")
        gs.addLoader("plup")

        gs.mergeFromPreviousSettings(None)

        assert tuple(sorted(gs.getLoaders())) == ("plop", "plup")
        assert gs.isEqualToStartingHash("toto")

    # mergeFromPreviousSettings, settings is not an instance of GlobalSettings
    def test_globalSettings12(self):
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        gs.addLoader("plop")
        gs.addLoader("plup")

        with pytest.raises(ParameterException):
            gs.mergeFromPreviousSettings(object())

    # mergeFromPreviousSettings, no loader in self, no loader in settings
    def test_globalSettings13(self):
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")

        gs2 = GlobalSettings()
        gs2.setStartingPoint("plop", "plup", "plap")

        gs.mergeFromPreviousSettings(gs2)

        assert gs.getLoaders() is None
        assert gs.isEqualToStartingHash("plop")

    # mergeFromPreviousSettings, loader in self, no loader in settings
    def test_globalSettings14(self):
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        gs.addLoader("plop")
        gs.addLoader("plup")

        gs2 = GlobalSettings()
        gs2.setStartingPoint("plop", "plup", "plap")

        gs.mergeFromPreviousSettings(gs2)

        assert tuple(sorted(gs.getLoaders())) == ("plop", "plup")
        assert gs.isEqualToStartingHash("plop")

    # mergeFromPreviousSettings, no loader in self, loader in settings
    def test_globalSettings15(self):
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")

        gs2 = GlobalSettings()
        gs2.setStartingPoint("plop", "plup", "plap")
        gs2.addLoader("lolo")
        gs2.addLoader("lulu")

        gs.mergeFromPreviousSettings(gs2)

        assert tuple(sorted(gs.getLoaders())) == ("lolo", "lulu")
        assert gs.isEqualToStartingHash("plop")

    # mergeFromPreviousSettings, loader in self, loader in settings
    def test_globalSettings16(self):
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        gs.addLoader("plop")
        gs.addLoader("plup")

        gs2 = GlobalSettings()
        gs2.setStartingPoint("plop", "plup", "plap")
        gs2.addLoader("plop")
        gs2.addLoader("lolo")
        gs2.addLoader("lulu")

        gs.mergeFromPreviousSettings(gs2)

        assert tuple(sorted(gs.getLoaders())) == ("lolo",
                                                  "lulu",
                                                  "plop",
                                                  "plup")
        assert gs.isEqualToStartingHash("plop")
