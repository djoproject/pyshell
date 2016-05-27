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

from pyshell.loader.abstractloader import AbstractLoader


class TestAbstractLoader(object):
    # AbstractLoader, load, exist, test args
    def test_abstractLoader2(self):
        al = AbstractLoader()
        assert al, "load"
        assert al.load, "__call__"
        assert al.load(None) is None
        assert al.load(None, None) is None
        with pytest.raises(TypeError):
            al.load(None, None, None)

    # AbstractLoader, unload, exist, test args
    def test_abstractLoader3(self):
        al = AbstractLoader()
        assert al, "unload"
        assert al.unload, "__call__"
        assert al.unload(None) is None
        assert al.unload(None, None) is None
        with pytest.raises(TypeError):
            al.unload(None, None, None)

    def test_priorities(self):
        al = AbstractLoader(load_priority=42, unload_priority=83)
        assert al.getLoadPriority() == 42
        assert al.getUnloadPriority() == 83
