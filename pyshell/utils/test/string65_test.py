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

from pyshell.utils.parsing import Parser
from pyshell.utils.string65 import escapeString


class TestEscaping(object):
    def test_escaping1(self):
        original = "plop"
        s = escapeString(original)
        assert s == "\"plop\""
        p = Parser(s)
        p.parse()
        assert p == [((original,), (), (),)]

    def test_escaping2(self):
        original = "$p\"l$o\\p"
        s = escapeString(original)
        assert s == "\"\\$p\\\"l$o\\\\p\""
        p = Parser(s)
        p.parse()
        assert p == [((original,), (), (),)]

    def test_escaping3(self):
        original = "-a$b | cde\nfg\\hi& "
        s = escapeString(original, False)
        assert s == "\\-a\\$b\\ \\|\\ cde\\\nfg\\\\hi\\&\\ "
        p = Parser(s)
        p.parse()
        assert p == [((original,), (), (),)]
