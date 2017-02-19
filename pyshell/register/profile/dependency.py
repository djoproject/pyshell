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

from pyshell.register.profile.default import DefaultProfile
from pyshell.register.profile.exception import RegisterException
from pyshell.utils.raises import raiseIfNotString


class DependencyLoaderProfile(DefaultProfile):
    def __init__(self, root_profile):
        DefaultProfile.__init__(self, root_profile)
        self.dep = {}

    def addDependency(self, addon_name, profile_name=None):
        raiseIfNotString(addon_name,
                         "addon_name",
                         RegisterException,
                         "addDependency",
                         self.__class__.__name__)

        if profile_name is not None:
            raiseIfNotString(profile_name,
                             "profile_name",
                             RegisterException,
                             "addDependency",
                             self.__class__.__name__)

        if addon_name in self.dep:
            excmsg = ("("+self.__class__.__name__+") addDependency, the "
                      "addon '"+addon_name+"' is already registered as a"
                      " dependency.")
            raise RegisterException(excmsg)

        self.dep[addon_name] = profile_name
