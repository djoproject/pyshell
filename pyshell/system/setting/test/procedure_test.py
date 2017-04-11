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

from pyshell.arg.checker.default import DefaultChecker
from pyshell.system.setting.procedure import DEFAULT_CHECKER
from pyshell.system.setting.procedure import ProcedureGlobalSettings
from pyshell.system.setting.procedure import ProcedureLocalSettings
from pyshell.system.setting.procedure import ProcedureSettings
from pyshell.utils.constants import ENABLE_ON_POST_PROCESS
from pyshell.utils.constants import ENABLE_ON_PRE_PROCESS
from pyshell.utils.constants import ENABLE_ON_PROCESS
from pyshell.utils.constants import SETTING_PROPERTY_ENABLEON
from pyshell.utils.constants import SETTING_PROPERTY_GRANULARITY
from pyshell.utils.exception import ParameterException


class ReadOnlyProcedureSettings(ProcedureSettings):
    def __init__(self):
        self._read_only_state = True
        ProcedureSettings.__init__(self)

    def setReadOnly(self, state):
        self._read_only_state = state

    def isReadOnly(self):
        return self._read_only_state


class TestProcedureSettings(object):
    def test_initNoneGranularity(self):
        s = ProcedureSettings(error_granularity=None)
        assert s.getErrorGranularity() == float('inf')

    def test_initInvalidGranularity(self):
        with pytest.raises(ParameterException):
            ProcedureSettings(error_granularity="toto")

    def test_initValidGranularity(self):
        s = ProcedureSettings(error_granularity=42)
        assert s.getErrorGranularity() == 42.0

    def test_initNoneEnableOn(self):
        s = ProcedureSettings(enable_on=None)
        assert s.isEnabledOnPreProcess()

    def test_initInvalidEnableOn(self):
        with pytest.raises(ParameterException):
            ProcedureSettings(enable_on=42)

    def test_initValidEnableOn(self):
        s = ProcedureSettings(enable_on=ENABLE_ON_POST_PROCESS)
        assert s.isEnabledOnPostProcess()

    def test_enableOnPreProcess(self):
        s = ProcedureSettings()
        assert s.isEnabledOnPreProcess()
        s.enableOnPreProcess()
        assert s.isEnabledOnPreProcess()
        s.enableOnPostProcess()
        assert not s.isEnabledOnPreProcess()

    def test_enableOnProcess(self):
        s = ProcedureSettings()
        assert not s.isEnabledOnProcess()
        s.enableOnProcess()
        assert s.isEnabledOnProcess()
        s.enableOnPostProcess()
        assert not s.isEnabledOnProcess()

    def test_enableOnPostProcess(self):
        s = ProcedureSettings()
        assert not s.isEnabledOnPostProcess()
        s.enableOnPostProcess()
        assert s.isEnabledOnPostProcess()
        s.enableOnPreProcess()
        assert not s.isEnabledOnPostProcess()

    def test_setEnableOnNoneValue(self):
        s = ProcedureSettings()
        assert s.isEnabledOnPreProcess()
        with pytest.raises(ParameterException):
            s.setEnableOn(value=None)
        assert s.isEnabledOnPreProcess()

    def test_setEnableOnInvalidValue(self):
        s = ProcedureSettings()
        assert s.isEnabledOnPreProcess()
        with pytest.raises(ParameterException):
            s.setEnableOn(value=42)
        assert s.isEnabledOnPreProcess()

    def test_setEnableOnValidValue(self):
        s = ProcedureSettings()
        assert s.isEnabledOnPreProcess()
        s.setEnableOn(value=ENABLE_ON_PROCESS)
        assert s.isEnabledOnProcess()

    def test_setEnableOnValidValueReadOnly(self):
        s = ReadOnlyProcedureSettings()
        assert s.isEnabledOnPreProcess()
        with pytest.raises(ParameterException):
            s.setEnableOn(value=ENABLE_ON_PROCESS)
        assert s.isEnabledOnPreProcess()

    def test_stopOnFirstError(self):
        s = ProcedureSettings()
        assert s.getErrorGranularity() == float('inf')
        s.neverStopIfErrorOccured()
        assert s.getErrorGranularity() == -1
        s.stopOnFirstError()
        assert s.getErrorGranularity() == float('inf')

    def test_neverStopIfErrorOccured(self):
        s = ProcedureSettings()
        assert s.getErrorGranularity() == float('inf')
        s.neverStopIfErrorOccured()
        assert s.getErrorGranularity() == -1

    def test_setErrorGranularityNoneValue(self):
        s = ProcedureSettings()
        with pytest.raises(ParameterException):
            s.setErrorGranularity(None)
        assert s.getErrorGranularity() == float('inf')

    def test_setErrorGranularityInvalidValue(self):
        s = ProcedureSettings()
        with pytest.raises(ParameterException):
            s.setErrorGranularity("toto")
        assert s.getErrorGranularity() == float('inf')

    def test_setErrorGranularityInvalidNegativValue(self):
        s = ProcedureSettings()
        with pytest.raises(ParameterException):
            s.setErrorGranularity(-55)

        with pytest.raises(ParameterException):
            s.setErrorGranularity(-2)

        assert s.getErrorGranularity() == float('inf')

    def test_setErrorGranularityValidNegativValue(self):
        s = ProcedureSettings()
        s.setErrorGranularity(-1)
        assert s.getErrorGranularity() == -1

    def test_setErrorGranularityValidPositivValue1(self):
        s = ProcedureSettings()
        s.setErrorGranularity(1)
        assert s.getErrorGranularity() == 1

    def test_setErrorGranularityValidPositivValue2(self):
        s = ProcedureSettings()
        s.setErrorGranularity(42)
        assert s.getErrorGranularity() == 42

    def test_setErrorGranularityValidPositivValue3(self):
        s = ProcedureSettings()
        s.setErrorGranularity(float('inf'))
        assert s.getErrorGranularity() == float('inf')

    def test_setErrorGranularityZeroValue(self):
        s = ProcedureSettings()
        s.setErrorGranularity(0)
        assert s.getErrorGranularity() == 0

    def test_getProperties(self):
        s = ProcedureSettings(error_granularity=42,
                              enable_on=ENABLE_ON_PROCESS)
        expected = {SETTING_PROPERTY_GRANULARITY: 42,
                    SETTING_PROPERTY_ENABLEON: 'enable_on_pro'}
        assert s.getProperties() == expected

    def test_getChecker(self):
        s = ProcedureSettings()
        assert s.getChecker() is DEFAULT_CHECKER

    def test_setChecker(self):
        int_checker = DefaultChecker.getInteger()
        s = ProcedureSettings()
        assert s.getChecker() is DEFAULT_CHECKER
        with pytest.raises(ParameterException):
            s.setChecker(checker=int_checker)
        assert s.getChecker() is DEFAULT_CHECKER

    def test_setListChecker(self):
        s = ProcedureSettings()
        assert not s.isListChecker()
        with pytest.raises(ParameterException):
            s.setListChecker(state=True)
        assert not s.isListChecker()

    def test_cloneWithoutParent(self):
        s = ProcedureSettings(
            error_granularity=56,
            enable_on=ENABLE_ON_POST_PROCESS)
        sc = s.clone()

        assert isinstance(sc, ProcedureSettings)
        assert s is not sc
        assert hash(s) == hash(sc)
        assert sc.isEnabledOnPostProcess()
        assert sc.getErrorGranularity() == 56


class TestProcedureLocalSettings(object):
    def test_initWithNotDefaultValue(self):
        s = ProcedureLocalSettings(
            read_only=True,
            removable=False,
            error_granularity=33,
            enable_on=ENABLE_ON_PRE_PROCESS)

        assert s.isReadOnly()
        assert not s.isRemovable()
        assert s.getErrorGranularity() == 33
        assert s.isEnabledOnPreProcess()

    def test_cloneWithoutParent(self):
        s = ProcedureLocalSettings(
            read_only=True,
            removable=False,
            error_granularity=56,
            enable_on=ENABLE_ON_POST_PROCESS)
        sc = s.clone()

        assert isinstance(sc, ProcedureLocalSettings)
        assert s is not sc
        assert hash(s) == hash(sc)
        assert sc.isReadOnly()
        assert not sc.isRemovable()
        assert sc.isEnabledOnPostProcess()
        assert sc.getErrorGranularity() == 56

    def test_getGlobalFromLocal(self):
        ls = ProcedureLocalSettings(
            read_only=True,
            removable=False,
            error_granularity=99,
            enable_on=ENABLE_ON_POST_PROCESS)

        gs = ls.getGlobalFromLocal()

        assert type(gs) is ProcedureGlobalSettings
        assert gs.isReadOnly()
        assert not gs.isRemovable()
        assert gs.isEnabledOnPostProcess()
        assert gs.getErrorGranularity() == 99


class TestProcedureGlobalSettings(object):
    def test_initWithNotDefaultValue(self):
        s = ProcedureGlobalSettings(
            read_only=True,
            removable=False,
            transient=True,
            error_granularity=66,
            enable_on=ENABLE_ON_PROCESS)

        assert s.isReadOnly()
        assert not s.isRemovable()
        assert s.isTransient()
        assert s.getErrorGranularity() == 66
        assert s.isEnabledOnProcess()

    def test_cloneWithoutParent(self):
        s = ProcedureGlobalSettings(
            error_granularity=56,
            enable_on=ENABLE_ON_POST_PROCESS)
        sc = s.clone()

        assert isinstance(sc, ProcedureGlobalSettings)
        assert s is not sc
        assert hash(s) == hash(sc)
        assert sc.isEnabledOnPostProcess()
        assert sc.getErrorGranularity() == 56

    def test_getGlobalFromLocal(self):
        gs = ProcedureGlobalSettings(
            read_only=True,
            removable=False,
            error_granularity=333,
            enable_on=ENABLE_ON_PRE_PROCESS)

        ls = gs.getLocalFromGlobal()

        assert type(ls) is ProcedureLocalSettings
        assert ls.isReadOnly()
        assert not ls.isRemovable()
        assert ls.isEnabledOnPreProcess()
        assert ls.getErrorGranularity() == 333
