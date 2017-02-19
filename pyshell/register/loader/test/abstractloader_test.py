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

from pyshell.register.exception import LoaderException
from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.profile.root import RootProfile


class TestAbstractLoader(object):

    def test_init(self):
        with pytest.raises(LoaderException):
            AbstractLoader()

    def test_getLoaderSignature(self):
        signature = AbstractLoader.getLoaderSignature()
        assert signature == ("pyshell.register.loader.abstractloader"
                             ".AbstractLoader")

    def test_createProfileInstance(self):
        root_profile = RootProfile()
        root_profile.setName("profile_name")
        assert AbstractLoader.createProfileInstance(root_profile) is None

    def test_load(self):
        AbstractLoader.load(profile_object=None, parameter_container=None)

    def test_unload(self):
        AbstractLoader.unload(profile_object=None, parameter_container=None)
