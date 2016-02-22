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

from pyshell.system.procedure import getAbsoluteIndex


class TestProcedure(object):

    def setUp(self):
        pass

    # # Misc # #

    # getAbsoluteIndex, positiv value in the range
    def test_getAbsoluteIndex1(self):
        assert getAbsoluteIndex(4, 5) == 4

    # getAbsoluteIndex, positiv value out of range
    def test_getAbsoluteIndex2(self):
        assert getAbsoluteIndex(23, 5) == 23

    # getAbsoluteIndex, zero value
    def test_getAbsoluteIndex3(self):
        assert getAbsoluteIndex(0, 5) == 0

    # getAbsoluteIndex, negativ value in the range
    def test_getAbsoluteIndex4(self):
        assert getAbsoluteIndex(-3, 5) == 2

    # getAbsoluteIndex, negativ value out of range
    def test_getAbsoluteIndex5(self):
        assert getAbsoluteIndex(-23, 5) == 0

    # # TODO Procedure # #

    # # TODO ProcedureFromList # #

    # # TODO ProcedureFromFile # #
