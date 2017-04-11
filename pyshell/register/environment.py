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

from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.register.loader.environment import EnvironmentLoader
from pyshell.register.utils.addon import getOrCreateProfile
from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.system.setting.environment import EnvironmentGlobalSettings


def _localGetAndInitCallerModule(profile=None):
    profile_loader = getOrCreateProfile(EnvironmentLoader, profile)
    return profile_loader


def setEnvironmentLoadPriority(value, profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    loader_profile.setLoadPriority(value)


def setEnvironmentUnloadPriority(value, profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    loader_profile.setUnloadPriority(value)


def registerEnvironment(env_key, env, profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    loader_profile.addParameter(env_key, env)


def registerEnvironmentAny(env_key, value, profile=None):
    checker = DefaultChecker.getArg()
    settings = EnvironmentGlobalSettings(checker=checker)
    param = EnvironmentParameter(value=value, settings=settings)
    registerEnvironment(env_key, param, profile=None)
    return param


def registerEnvironmentBoolean(env_key, value, profile=None):
    checker = DefaultChecker.getBoolean()
    settings = EnvironmentGlobalSettings(checker=checker)
    param = EnvironmentParameter(value=value, settings=settings)
    registerEnvironment(env_key, param, profile=None)
    return param


def registerEnvironmentFile(env_key, value, profile=None):
    checker = DefaultChecker.getFile()
    settings = EnvironmentGlobalSettings(checker=checker)
    param = EnvironmentParameter(value=value, settings=settings)
    registerEnvironment(env_key, param, profile=None)
    return param


def registerEnvironmentFloat(env_key, value, profile=None):
    checker = DefaultChecker.getFloat()
    settings = EnvironmentGlobalSettings(checker=checker)
    param = EnvironmentParameter(value=value, settings=settings)
    registerEnvironment(env_key, param, profile=None)
    return param


def registerEnvironmentInteger(env_key, value, profile=None):
    checker = DefaultChecker.getInteger()
    settings = EnvironmentGlobalSettings(checker=checker)
    param = EnvironmentParameter(value=value, settings=settings)
    registerEnvironment(env_key, param, profile=None)
    return param


def registerEnvironmentString(env_key, value, profile=None):
    checker = DefaultChecker.getString()
    settings = EnvironmentGlobalSettings(checker=checker)
    param = EnvironmentParameter(value=value, settings=settings)
    registerEnvironment(env_key, param, profile=None)
    return param


def registerEnvironmentListAny(env_key, value, profile=None):
    checker = ListArgChecker(DefaultChecker.getArg())
    settings = EnvironmentGlobalSettings(checker=checker)
    param = EnvironmentParameter(value=value, settings=settings)
    registerEnvironment(env_key, param, profile=None)
    return param


def registerEnvironmentListBoolean(env_key, value, profile=None):
    checker = ListArgChecker(DefaultChecker.getBoolean())
    settings = EnvironmentGlobalSettings(checker=checker)
    param = EnvironmentParameter(value=value, settings=settings)
    registerEnvironment(env_key, param, profile=None)
    return param


def registerEnvironmentListFile(env_key, value, profile=None):
    checker = ListArgChecker(DefaultChecker.getFile())
    settings = EnvironmentGlobalSettings(checker=checker)
    param = EnvironmentParameter(value=value, settings=settings)
    registerEnvironment(env_key, param, profile=None)
    return param


def registerEnvironmentListFloat(env_key, value, profile=None):
    checker = ListArgChecker(DefaultChecker.getFloat())
    settings = EnvironmentGlobalSettings(checker=checker)
    param = EnvironmentParameter(value=value, settings=settings)
    registerEnvironment(env_key, param, profile=None)
    return param


def registerEnvironmentListInteger(env_key, value, profile=None):
    checker = ListArgChecker(DefaultChecker.getInteger())
    settings = EnvironmentGlobalSettings(checker=checker)
    param = EnvironmentParameter(value=value, settings=settings)
    registerEnvironment(env_key, param, profile=None)
    return param


def registerEnvironmentListString(env_key, value, profile=None):
    checker = ListArgChecker(DefaultChecker.getString())
    settings = EnvironmentGlobalSettings(checker=checker)
    param = EnvironmentParameter(value=value, settings=settings)
    registerEnvironment(env_key, param, profile=None)
    return param
