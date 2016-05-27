#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

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

import inspect

from pyshell.loader.exception import RegisterException
from pyshell.loader.globalloader import GlobalLoader


def getAndInitCallerModule(caller_loader_key,
                           caller_loader_class_definition,
                           profile=None,
                           module_level=3):
    frm = inspect.stack()[module_level]
    mod = inspect.getmodule(frm[0])

    if hasattr(mod, "_loaders"):
        # must be an instance of GlobalLoader
        if not isinstance(mod._loaders, GlobalLoader):
            excmsg = ("(loader) getAndInitCallerModule, the stored loader in"
                      " the module '"+str(mod)+"' is not an instance of "
                      "GlobalLoader, get '"+str(type(mod._loaders))+"'")
            raise RegisterException(excmsg)
    else:
        # init loaders dictionnary
        setattr(mod, "_loaders", GlobalLoader())

        # add the always existing loader here
        # ===>

        # <===

    return mod._loaders.getOrCreateLoader(caller_loader_key,
                                          caller_loader_class_definition,
                                          profile)
