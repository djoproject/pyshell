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

# TODO  use os.path.join in place of string concatenation

import os
import shutil
import tempfile

import pytest

from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.misc import createParentDirectory


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


class TestMisc(object):
    def test_createParentDirectory1(self):
        file_path = tempfile.gettempdir() + os.sep + "plop.txt"
        assert os.path.exists(tempfile.gettempdir())
        assert not os.path.exists(file_path)
        createParentDirectory(file_path)
        assert os.path.exists(tempfile.gettempdir())
        assert not os.path.exists(file_path)

    def test_createParentDirectory2(self):
        shutil.rmtree(tempfile.gettempdir() + os.sep + "toto", True)

        path = os.sep.join(("toto", "tata", "titi", "test.txt"))
        path = tempfile.gettempdir() + os.sep + path

        assert not os.path.exists(os.path.dirname(path))
        assert not os.path.exists(path)

        createParentDirectory(path)

        assert os.path.exists(os.path.dirname(path))
        assert not os.path.exists(path)

        shutil.rmtree(tempfile.gettempdir() + os.sep + "toto", True)

    def test_createParentDirectory3(self):
        shutil.rmtree(tempfile.gettempdir() + os.sep + "toto", True)
        os.makedirs(tempfile.gettempdir() + os.sep + "toto")
        touch(tempfile.gettempdir() + os.sep + "toto" + os.sep + "plop")
        path = (tempfile.gettempdir() + os.sep + "toto" + os.sep + "plop" +
                os.sep + "test.txt")
        with pytest.raises(DefaultPyshellException):
            createParentDirectory(path)
        shutil.rmtree(tempfile.gettempdir() + os.sep + "toto", True)
