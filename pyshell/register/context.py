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

from pyshell.arg.checker.default import DefaultChecker
from pyshell.register.loader.context import ContextLoader
from pyshell.register.utils.addon import getOrCreateProfile
from pyshell.system.parameter.context import ContextParameter
from pyshell.system.setting.context import ContextGlobalSettings


def _localGetAndInitCallerModule(profile=None):
    profile_loader = getOrCreateProfile(ContextLoader, profile)
    return profile_loader


def setContextLoadPriority(value, profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    loader_profile.setLoadPriority(value)


def setContextUnloadPriority(value, profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    loader_profile.setUnloadPriority(value)


def registerContext(context_key, context, profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    loader_profile.addParameter(context_key, context)


def registerContextAny(context_key, value, profile=None):
    checker = DefaultChecker.getArg()
    settings = ContextGlobalSettings(checker=checker)
    param = ContextParameter(value=value, settings=settings)
    registerContext(context_key, param, profile=None)
    return param


def registerContextBoolean(context_key, value, profile=None):
    checker = DefaultChecker.getBoolean()
    settings = ContextGlobalSettings(checker=checker)
    param = ContextParameter(value=value, settings=settings)
    registerContext(context_key, param, profile=None)
    return param


def registerContextFile(context_key, value, profile=None):
    checker = DefaultChecker.getFile()
    settings = ContextGlobalSettings(checker=checker)
    param = ContextParameter(value=value, settings=settings)
    registerContext(context_key, param, profile=None)
    return param


def registerContextFloat(context_key, value, profile=None):
    checker = DefaultChecker.getFloat()
    settings = ContextGlobalSettings(checker=checker)
    param = ContextParameter(value=value, settings=settings)
    registerContext(context_key, param, profile=None)
    return param


def registerContextInteger(context_key, value, profile=None):
    checker = DefaultChecker.getInteger()
    settings = ContextGlobalSettings(checker=checker)
    param = ContextParameter(value=value, settings=settings)
    registerContext(context_key, param, profile=None)
    return param


def registerContextString(context_key, value, profile=None):
    checker = DefaultChecker.getString()
    settings = ContextGlobalSettings(checker=checker)
    param = ContextParameter(value=value, settings=settings)
    registerContext(context_key, param, profile=None)
    return param
