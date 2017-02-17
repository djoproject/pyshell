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

from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.raises import raiseIfInvalidKeyList


class TestKeyList(object):
    def test_raiseIfInvalidKeyList1(self):
        with pytest.raises(DefaultPyshellException):
            raiseIfInvalidKeyList("toto",
                                  DefaultPyshellException,
                                  "package",
                                  "method")

    def test_raiseIfInvalidKeyList2(self):
        with pytest.raises(DefaultPyshellException):
            raiseIfInvalidKeyList(("toto", "tata", u"titi", 42),
                                  DefaultPyshellException,
                                  "package",
                                  "method")

    def test_raiseIfInvalidKeyList3(self):
        with pytest.raises(DefaultPyshellException):
            raiseIfInvalidKeyList(("toto", "tata", u"titi", ""),
                                  DefaultPyshellException,
                                  "package",
                                  "method")

    def test_raiseIfInvalidKeyList4(self):
        assert raiseIfInvalidKeyList(("toto", "tata", u"titi",),
                                     DefaultPyshellException,
                                     "package",
                                     "method") == ("toto", "tata", u"titi",)
