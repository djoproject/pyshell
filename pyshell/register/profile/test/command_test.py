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

from pyshell.command.command import MultiCommand
from pyshell.register.profile.command import CommandLoaderProfile
from pyshell.register.profile.exception import RegisterException
from pyshell.register.profile.root import RootProfile


class TestCommandLoaderProfile(object):

    def setup_method(self, method):
        root_profile = RootProfile()
        root_profile.setName("profile_name")
        self.cl = CommandLoaderProfile(root_profile)

    def test_setInvalidTempPrefix(self):
        with pytest.raises(RegisterException):
            self.cl.setTempPrefix(object)

    def test_setTempPrefix(self):
        self.cl.setTempPrefix(("plop",))
        assert self.cl.getTempPrefix() == ("plop",)

    def test_unsetTempPrefix(self):
        self.cl.setTempPrefix(("plop",))
        assert self.cl.getTempPrefix() == ("plop",)
        self.cl.unsetTempPrefix()
        assert self.cl.getTempPrefix() is None

    def test_setInvalidPrefix(self):
        with pytest.raises(RegisterException):
            self.cl.setPrefix(object)

    def test_setPrefix(self):
        self.cl.setPrefix(("plop",))
        assert self.cl.getPrefix() == ("plop",)

    def test_addInvalidStopTraversal(self):
        with pytest.raises(RegisterException):
            self.cl.addStopTraversal(object)

    def test_addStopTraversalWithTempPrefix(self):
        self.cl.setTempPrefix(("plop",))
        self.cl.addStopTraversal(("titi", "tata",))
        assert self.cl.hasStopTraversal(("plop", "titi", "tata",))

    def test_addStopTraversalWithoutTempPrefix(self):
        self.cl.unsetTempPrefix()
        self.cl.addStopTraversal(("titi", "tata",))
        assert self.cl.hasStopTraversal(("titi", "tata",))

    def test_invalidHasStopTraversal(self):
        with pytest.raises(RegisterException):
            self.cl.hasStopTraversal(object)

    def test_addCmdWithInvalidKey(self):
        with pytest.raises(RegisterException):
            self.cl.addCmd(object, MultiCommand())

    def test_addCmdWithInvalidCommand(self):
        with pytest.raises(RegisterException):
            self.cl.addCmd(("titi", "tata",), object)

    def test_addCmdWithTempPrefix(self):
        self.cl.setTempPrefix(("plop",))
        self.cl.addCmd(("titi", "tata",), MultiCommand())
        assert self.cl.hasCmd(("plop", "titi", "tata",))

    def test_addCmdWithoutTempPrefix(self):
        self.cl.unsetTempPrefix()
        self.cl.addCmd(("titi", "tata",), MultiCommand())
        assert self.cl.hasCmd(("titi", "tata",))

    def test_addCmdWithExistingKey(self):
        self.cl.addCmd(("titi", "tata",), MultiCommand())
        assert self.cl.hasCmd(("titi", "tata",))

        with pytest.raises(RegisterException):
            self.cl.addCmd(("titi", "tata",), MultiCommand())
