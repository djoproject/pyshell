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

from pyshell.register.profile.file import FileLoaderProfile
from pyshell.register.profile.root import RootProfile


class TestFileLoaderProfile(object):
    def setup_method(self, method):
        root_profile = RootProfile()
        root_profile.setName("profile_name")
        self.p = FileLoaderProfile(root_profile)

    def test_getLoadPriority(self):
        assert self.p.getLoadPriority() == float("inf")

    def test_getUnloadPriority(self):
        assert self.p.getUnloadPriority() == float("inf")
