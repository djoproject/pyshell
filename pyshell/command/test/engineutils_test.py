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

from pyshell.command.exception import ExecutionException
from pyshell.command.utils import equalMap
from pyshell.command.utils import equalPath
from pyshell.command.utils import isAValidIndex
from pyshell.command.utils import isValidMap


class TestEngineUtils(object):

    def setUp(self):
        pass

    def test_equalPath(self):

        # different length
        path1 = [0, 1]
        path2 = [0]

        equals, sameLength, equalsCount, path1IsHigher = equalPath(
            path1, path2)
        assert not equals
        assert not sameLength
        assert equalsCount == 1
        assert path1IsHigher is None

        path2 = [0, 1]
        path1 = [0]

        equals, sameLength, equalsCount, path1IsHigher = equalPath(
            path1, path2)
        assert not equals
        assert not sameLength
        assert equalsCount == 1
        assert path1IsHigher is None

        # same path
        path1 = []
        path2 = []
        for i in range(1, 5):
            path1.append(i)
            path2.append(i)

            result = equalPath(path1, path2)
            equals, sameLength, equalsCount, path1IsHigher = result
            assert equals
            assert sameLength
            assert equalsCount == i
            assert path1IsHigher is None

        # same length but 2 is always higher
        path1 = []
        path2 = []
        for i in range(1, 5):
            path1.append(i)
            path2.append(i + 1)
            if len(path2) > 1:
                path2[-2] -= 1

            result = equalPath(path1, path2)
            equals, sameLength, equalsCount, path1IsHigher = result
            assert (not equals)
            assert sameLength
            assert equalsCount == (i - 1)
            assert (not path1IsHigher)

        # same length but 1 is always higher
        path1 = []
        path2 = []
        for i in range(1, 5):
            path2.append(i)
            path1.append(i + 1)
            if len(path1) > 1:
                path1[-2] -= 1

            result = equalPath(path1, path2)
            equals, sameLength, equalsCount, path1IsHigher = result
            assert (not equals)
            assert sameLength
            assert equalsCount == (i - 1)
            assert (path1IsHigher)

    def test_isAValidIndex(self):
        with pytest.raises(ExecutionException):
            isAValidIndex([], 43)
        with pytest.raises(ExecutionException):
            isAValidIndex([], -25)
        with pytest.raises(ExecutionException):
            isAValidIndex([], 0)

        with pytest.raises(ExecutionException):
            isAValidIndex([1, 2, 3, 4, 5], 43)
        with pytest.raises(ExecutionException):
            isAValidIndex([1, 2, 3, 4, 5], -25)
        with pytest.raises(ExecutionException):
            isAValidIndex([1, 2, 3, 4, 5], 5)
        with pytest.raises(ExecutionException):
            isAValidIndex([1, 2, 3, 4, 5], -6)
        isAValidIndex([1, 2, 3, 4, 5], 4)
        isAValidIndex([1, 2, 3, 4, 5], -5)
        isAValidIndex([1, 2, 3, 4, 5], 0)

    def test_equalMap(self):
        assert equalMap(None, None)
        assert not equalMap(None, [])
        assert not equalMap([], None)
        assert equalMap([], [])

        assert not equalMap([True, False, True], [False, True])
        assert not equalMap([True, False, True], [True, True, True])

        assert equalMap([True, False, True], [True, False, True])

    def test_isValidMap(self):
        assert isValidMap(None, 123)
        assert not isValidMap("", 123)
        assert not isValidMap(23, 123)
        assert not isValidMap(56.5, 123)
        assert not isValidMap(object(), 123)

        assert not isValidMap([1, 2, 3], 123)
        assert isValidMap([True, True, True], 3)
        assert not isValidMap([1, 2, 3], 3)
        assert not isValidMap([True, True, True, 42], 4)
