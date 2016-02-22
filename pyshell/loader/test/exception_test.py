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

from pyshell.loader.exception import LoadException
from pyshell.loader.exception import RegisterException


def raiseLoadException():
    raise LoadException("plop")


def raiseRegisterException():
    raise RegisterException("plip")


class ExceptionTest(object):

    def test_registerException(self):
        with pytest.raises(RegisterException):
            raiseRegisterException()

    def test_loadException(self):
        with pytest.raises(LoadException):
            raiseLoadException()
