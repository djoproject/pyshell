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

from pyshell.utils.valuable import DefaultValuable
from pyshell.utils.valuable import SelectableValuable
from pyshell.utils.valuable import SimpleValuable
from pyshell.utils.valuable import Valuable

# README these tests could look stupid but it is very important for the
# whole application that these four class respect drasticaly this structure


class TestValuable(object):

    def test_valuable(self):
        v = Valuable()
        assert hasattr(v, "getValue")
        assert hasattr(v.getValue, "__call__")
        assert v.getValue() is None

    def test_selectableValuable(self):
        sv = SelectableValuable()

        assert hasattr(sv, "getValue")
        assert hasattr(sv.getValue, "__call__")
        assert sv.getValue() is None

        assert hasattr(sv, "getSelectedValue")
        assert hasattr(sv.getSelectedValue, "__call__")
        assert sv.getSelectedValue() is None

    def test_defaultValuable(self):
        d = DefaultValuable("plop")

        assert hasattr(d, "getValue")
        assert hasattr(d.getValue, "__call__")
        assert d.getValue() == "plop"

        assert hasattr(d, "getSelectedValue")
        assert hasattr(d.getSelectedValue, "__call__")
        assert d.getSelectedValue() == "plop"

    def test_simpleValuable(self):
        sv = SimpleValuable(42)

        assert hasattr(sv, "getValue")
        assert hasattr(sv.getValue, "__call__")
        assert sv.getValue() == 42

        assert hasattr(sv, "getSelectedValue")
        assert hasattr(sv.getSelectedValue, "__call__")
        assert sv.getSelectedValue() == 42

        assert sv.setValue(23) == 23
        assert sv.getValue() == 23
        assert sv.getSelectedValue() == 23
