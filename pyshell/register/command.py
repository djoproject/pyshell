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

from pyshell.command.command import MultiCommand
from pyshell.command.command import UniCommand
from pyshell.register.loader.command import CommandLoader
from pyshell.register.utils.addon import getOrCreateProfile


def _localGetAndInitCallerModule(profile=None):
    profile_loader = getOrCreateProfile(CommandLoader, profile)
    return profile_loader


def setCommandLoadPriority(value, profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    loader_profile.setLoadPriority(value)


def setCommandUnloadPriority(value, profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    loader_profile.setUnloadPriority(value)


def registerSetGlobalPrefix(key_list, profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    loader_profile.setPrefix(key_list)


def registerSetTempPrefix(key_list, profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    loader_profile.setTempPrefix(key_list)


def registerResetTempPrefix(profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    loader_profile.unsetTempPrefix()


def registerAnInstanciatedCommand(key_list, cmd, profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    loader_profile.addCmd(key_list, cmd)
    return cmd


def registerCommand(key_list, pre=None, pro=None, post=None, profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    cmd = UniCommand(pre, pro, post)
    loader_profile.addCmd(key_list, cmd)
    return cmd


def registerAndCreateEmptyMultiCommand(key_list, profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    cmd = MultiCommand()
    loader_profile.addCmd(key_list, cmd)
    return cmd


def registerStopHelpTraversalAt(key_list=(), profile=None):
    loader_profile = _localGetAndInitCallerModule(profile)
    loader_profile.addStopTraversal(key_list)
