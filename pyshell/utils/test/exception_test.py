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

import pytest

from pyshell.utils.exception import ListOfException


class TestException(object):
    def testEmptyListOfException(self):
        l = ListOfException()
        assert not l.isThrowable()
        assert str(l) == "no error, this exception shouldn't be throwed"

    def testInvalidException(self):
        l = ListOfException()
        with pytest.raises(Exception):
            l.addException(("plop",))

    def testAddOneException(self):
        l = ListOfException()
        l.addException(Exception("plop"))
        assert len(l.exceptions) == 1

    def testAddSeveralExceptions(self):
        l = ListOfException()
        l.addException(Exception("plop"))
        l.addException(Exception("plip"))

        assert len(l.exceptions) == 2

        l2 = ListOfException()
        l2.addException(l)

        assert len(l2.exceptions) == 2
