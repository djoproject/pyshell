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

from pyshell.register.environment import registerEnvironment
from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.profile.default import DefaultProfile
from pyshell.utils.exception import DefaultPyshellException


registerEnvironment("env.failed.nothing", "nothing")


class RaisingOnLoadLoaded(AbstractLoader):
    @staticmethod
    def createProfileInstance(root_profile):
        return DefaultProfile(root_profile)

    @classmethod
    def load(cls, profile_object, parameter_container):
        raise DefaultPyshellException("ooops load")


_loaders.bindLoaderToProfile(RaisingOnLoadLoaded, None)  # noqa
