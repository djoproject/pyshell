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

# TODO
#  add new test for allowed transition testing and forbidde several
#  addon loaded
#  remove old test irrelevant about transaction

import pytest

from pyshell.loader.abstractloader import AbstractLoader
from pyshell.loader.exception import RegisterException
from pyshell.loader.globalloader import GlobalLoader
from pyshell.loader.utils import getAndInitCallerModule


class SubAbstractLoader(AbstractLoader):
    pass


class TestUtils(object):

    def tearDown(self):
        global _loaders
        if "_loaders" in globals():
            del _loaders

    # ## getAndInitCallerModule ## #

    # getAndInitCallerModule, parent module does not have _loader THEN parent
    # module has _loader
    def test_getAndInitCallerModule1(self):
        global _loaders
        assert "_loaders" not in globals()
        loader1 = getAndInitCallerModule("getAndInitCallerModule1",
                                         SubAbstractLoader,
                                         profile=None,
                                         module_level=1)
        assert "_loaders" in globals()
        assert isinstance(_loaders, GlobalLoader)
        loader2 = getAndInitCallerModule("getAndInitCallerModule1",
                                         SubAbstractLoader,
                                         profile=None,
                                         module_level=1)
        assert loader1 is loader2

    # getAndInitCallerModule, parent module has _loader but with a wrong type
    def test_getAndInitCallerModule2(self):
        global _loaders
        _loaders = "plop"
        assert "_loaders" in globals()
        with pytest.raises(RegisterException):
            # level is 2 because we have to go outside of the assert module
            getAndInitCallerModule("getAndInitCallerModule1",
                                   AbstractLoader,
                                   profile=None,
                                   module_level=2)
