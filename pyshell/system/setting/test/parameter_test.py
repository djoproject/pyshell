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

from pyshell.system.setting.parameter import ParameterGlobalSettings
from pyshell.system.setting.parameter import ParameterLocalSettings
from pyshell.system.setting.parameter import ParameterSettings
from pyshell.utils.exception import ParameterException


class TestParameterSettings(object):

    def setup_method(self, method):
        self.setHash = hash(ParameterSettings())

    # # Settings # #

    def test_settings1(self):
        s = ParameterSettings()

        assert not s.isReadOnly()
        assert s.isRemovable()
        assert s.isTransient()
        assert s.getProperties() == (("removable", True, ),
                                     ("readOnly", False, ),
                                     ("transient", True, ))
        assert hash(s) == self.setHash

    def test_settings2(self):
        s = ParameterSettings(read_only=False, removable=False)

        assert not s.isReadOnly()
        assert s.isRemovable()
        assert s.isTransient()
        assert s.getProperties() == (("removable", True, ),
                                     ("readOnly", False, ),
                                     ("transient", True, ))
        assert hash(s) == self.setHash

    def test_settings3(self):
        s = ParameterSettings(read_only=True, removable=True)

        assert not s.isReadOnly()
        assert s.isRemovable()
        assert s.isTransient()
        assert s.getProperties() == (("removable", True, ),
                                     ("readOnly", False, ),
                                     ("transient", True, ))
        assert hash(s) == self.setHash

    def test_settings4(self):
        s = ParameterSettings()
        s.setReadOnly(True)
        assert not s.isReadOnly()
        assert hash(s) == self.setHash

    def test_settings5(self):
        s = ParameterSettings()
        s.setReadOnly(False)
        assert not s.isReadOnly()
        assert hash(s) == self.setHash

    def test_settings6(self):
        s = ParameterSettings()
        s.setTransient(True)
        assert s.isTransient()
        assert hash(s) == self.setHash

    def test_settings7(self):
        s = ParameterSettings()
        s.setTransient(False)
        assert s.isTransient()
        assert hash(s) == self.setHash

    def test_settings8(self):
        s = ParameterSettings()
        s.setRemovable(True)
        assert s.isRemovable()
        assert hash(s) == self.setHash

    def test_settings9(self):
        s = ParameterSettings()
        s.setRemovable(False)
        assert s.isRemovable()
        assert hash(s) == self.setHash

    def test_cloneWithSource(self):
        source = ParameterSettings()
        to_clone = ParameterSettings()
        to_clone.clone(source)
        assert hash(source) == hash(to_clone)

    def test_cloneWithoutSource(self):
        s = ParameterSettings()
        sp = s.clone()

        assert s is not sp
        assert hash(s) == hash(sp)

    def test_getOppositeSettingClass(self):
        assert ParameterSettings._getOppositeSettingClass() is None


class TestParameterLocalSettings(object):

    def test_parameterLocalSettings1(self):
        ls = ParameterLocalSettings()
        assert ls.isRemovable()
        assert not ls.isReadOnly()

    def test_parameterLocalSettings2(self):
        ls = ParameterLocalSettings(read_only=True, removable=True)
        assert ls.isRemovable()
        assert ls.isReadOnly()

    def test_parameterLocalSettings3(self):
        ls = ParameterLocalSettings(read_only=False, removable=False)
        assert not ls.isRemovable()
        assert not ls.isReadOnly()

    def test_parameterLocalSettings4(self):
        ls = ParameterLocalSettings()
        ls.setRemovable(True)
        assert ls.isRemovable()

    def test_parameterLocalSettings5(self):
        ls = ParameterLocalSettings()
        ls.setRemovable(False)
        assert not ls.isRemovable()

    def test_parameterLocalSettings6(self):
        ls = ParameterLocalSettings()
        with pytest.raises(ParameterException):
            ls.setRemovable("plop")

    def test_parameterLocalSettings7(self):
        ls = ParameterLocalSettings(read_only=True)
        with pytest.raises(ParameterException):
            ls.setRemovable(True)

    def test_parameterLocalSettings8(self):
        ls = ParameterLocalSettings()
        ls.setReadOnly(True)
        assert ls.isReadOnly()

    def test_parameterLocalSettings9(self):
        ls = ParameterLocalSettings()
        ls.setReadOnly(False)
        assert not ls.isReadOnly()

    def test_parameterLocalSettings10(self):
        ls = ParameterLocalSettings()
        with pytest.raises(ParameterException):
            ls.setReadOnly("plop")

    def test_parameterLocalSettings11(self):
        ls = ParameterLocalSettings(read_only=True)
        with pytest.raises(ParameterException):
            ls._raiseIfReadOnly()

    def test_parameterLocalSettings12(self):
        ls = ParameterLocalSettings(read_only=True)
        with pytest.raises(ParameterException):
            ls._raiseIfReadOnly("plop")

    def test_parameterLocalSettings13(self):
        ls = ParameterLocalSettings(read_only=True)
        with pytest.raises(ParameterException):
            ls._raiseIfReadOnly("plop", "plip")

    def test_cloneWithSource(self):
        source = ParameterLocalSettings(read_only=True, removable=True)
        to_clone = ParameterLocalSettings(read_only=True, removable=False)

        assert source.isReadOnly()
        assert source.isRemovable()

        to_clone.clone(source)

        assert source.isReadOnly()
        assert not source.isRemovable()

    def test_cloneWithoutSource(self):
        gs = ParameterLocalSettings(read_only=False, removable=True)
        gsp = gs.clone()

        assert not gsp.isReadOnly()
        assert gsp.isRemovable()
        assert gs is not gsp
        assert hash(gs) == hash(gsp)

    def test_getGlobalFromLocal(self):
        ls = ParameterLocalSettings(read_only=True,
                                    removable=False)

        gs = ls.getGlobalFromLocal()
        assert gs.isReadOnly()
        assert not gs.isRemovable()


class TestParameterGlobalSettings(object):

    def test_parameterGlobalSettings1(self):
        gs = ParameterGlobalSettings()
        assert not gs.isReadOnly()
        assert gs.isRemovable()
        assert not gs.isTransient()

    def test_parameterGlobalSettings2(self):
        gs = ParameterGlobalSettings(read_only=False,
                                     removable=False,
                                     transient=False)
        assert not gs.isReadOnly()
        assert not gs.isRemovable()
        assert not gs.isTransient()

    def test_parameterGlobalSettings3(self):
        gs = ParameterGlobalSettings(read_only=True,
                                     removable=True,
                                     transient=True)
        assert gs.isReadOnly()
        assert gs.isRemovable()
        assert gs.isTransient()

    def test_parameterGlobalSettings4(self):
        gs = ParameterGlobalSettings()
        gs.setTransient(True)
        assert gs.isTransient()

    def test_parameterGlobalSettings5(self):
        gs = ParameterGlobalSettings()
        gs.setTransient(False)
        assert not gs.isTransient()

    def test_parameterGlobalSettings6(self):
        gs = ParameterGlobalSettings()
        with pytest.raises(ParameterException):
            gs.setTransient("plop")

    def test_parameterGlobalSettings7(self):
        gs = ParameterGlobalSettings(read_only=True)
        with pytest.raises(ParameterException):
            gs.setTransient(True)

    def test_parameterGlobalSettings8(self):
        gs = ParameterGlobalSettings()
        gs.setStartingPoint("toto")
        assert gs.isEqualToStartingHash("toto")

    def test_parameterGlobalSettings9(self):
        gs = ParameterGlobalSettings()
        gs.setStartingPoint("toto")
        with pytest.raises(ParameterException):
            gs.setStartingPoint("toto")

    def test_cloneWithSource(self):
        source = ParameterGlobalSettings(read_only=True,
                                         removable=True,
                                         transient=False)
        source.setStartingPoint("source")

        to_clone = ParameterGlobalSettings(read_only=True,
                                           removable=True,
                                           transient=True)
        to_clone.setStartingPoint("to_clone")

        assert not source.isTransient()
        assert source.isReadOnly()

        to_clone.clone(source)

        assert source.isTransient()
        assert source.isReadOnly()
        assert source.isEqualToStartingHash("source")
        assert source.isRemovable()

    def test_cloneWithoutSource(self):
        gs = ParameterGlobalSettings(read_only=False,
                                     removable=True,
                                     transient=False)
        gs.setStartingPoint("toto")
        gsp = gs.clone()

        assert not gsp.isReadOnly()
        assert gsp.isRemovable()
        assert not gsp.isTransient()
        assert not gsp.isEqualToStartingHash("toto")
        assert gs is not gsp
        assert hash(gs) == hash(gsp)

    def test_getLocalFromGlobal(self):
        gs = ParameterGlobalSettings(read_only=True,
                                     removable=False,
                                     transient=True)

        ls = gs.getLocalFromGlobal()
        assert ls.isReadOnly()
        assert not ls.isRemovable()

    def test_getGlobalFromLocal(self):
        gs = ParameterGlobalSettings(read_only=True,
                                     removable=False,
                                     transient=True)

        with pytest.raises(AttributeError):
            gs.getGlobalFromLocal()
