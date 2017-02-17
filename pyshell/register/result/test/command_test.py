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

import pytest

from pyshell.register.loader.exception import UnloadException
from pyshell.register.result.command import CommandResult


class TestCommandResult(object):
    def test_constructor1(self):
        CommandResult(["com"])

    def test_constructor2(self):
        CommandResult(["com"], "section_name")

    def test_constructor3(self):
        CommandResult(["com"], "section_name", set(["addon"]))

    def test_constructorError1(self):
        with pytest.raises(UnloadException):
            CommandResult(42)

    def test_constructorError2(self):
        with pytest.raises(UnloadException):
            CommandResult([])

    def test_constructorError3(self):
        with pytest.raises(UnloadException):
            CommandResult(["com"], "section_name", set([42]))

    def test_constructorError4(self):
        with pytest.raises(UnloadException):
            CommandResult(["com"], "section_name", 42)
