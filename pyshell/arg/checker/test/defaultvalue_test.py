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

from pyshell.arg.checker.defaultvalue import DefaultValueChecker


class TestDefaultArgChecker(object):

    def setup_method(self, method):
        self.checker = DefaultValueChecker("53")

    def test_get(self):
        assert "53" == self.checker.getValue("43")
        assert "53" == self.checker.getValue(52, 23)
        assert "53" == self.checker.getValue(0x52, 23)
        assert "53" == self.checker.getValue(52.33, 23)
        assert "53" == self.checker.getValue(True, 23)
        assert "53" == self.checker.getValue(False, 23)

    def test_usage(self):
        assert self.checker.getUsage() == "<any>"
