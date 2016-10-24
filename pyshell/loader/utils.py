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

from pyshell.loader.abstractloader import AbstractLoader
from pyshell.loader.exception import LoaderException

def getNearestModule():
    nearest_frame = None
    for record in inspect.stack():
        frame, path, line_number, parent_stmp, line_string, unknown = record
        if parent_stmp == "<module>":
            nearest_frame = frame
            break

    if nearest_frame is None:
        excmsg = ("(utils) getNearestModule, fail to find the nearest frame")
        raise LoaderException(excmsg)

    mod = inspect.getmodule(nearest_frame)
    return mod


def getRootLoader(class_definition=None):
    mod = getNearestModule()

    if class_definition is not None and not inspect.isclass(class_definition):
        excmsg = ("(utils) getRootLoader, the provided argument is not"
                  " a class definition")
        raise LoaderException(excmsg)

    if hasattr(mod, "_loaders"):
        if (class_definition is not None and
           not isinstance(mod._loaders, class_definition)):
            excmsg = ("(utils) getRootLoader, the stored loader in"
                      " the module '"+str(mod)+"' is not an instance of "
                      "'"+class_definition.__name__+"', get '"+
                      str(type(mod._loaders))+"'")
            raise LoaderException(excmsg)
        elif not isinstance(mod._loaders, AbstractLoader):
            excmsg = ("(utils) getRootLoader, the stored loader in"
                      " the module '"+str(mod)+"' is not an instance of "
                      "AbstractLoader, get '"+str(type(mod._loaders))+"'")
            raise LoaderException(excmsg)
                
        return mod._loaders

    elif class_definition is not None:
        master = class_definition(mod.__name__)
        setattr(mod, "_loaders", master)
        return master

    else:
        return None


def getLoaderSignature(class_definition):
    if not inspect.isclass(class_definition):
        excmsg = ("(utils) getLoaderSignature, the provided argument is not"
                  " a class definition")
        raise LoaderException(excmsg)
    return class_definition.__module__ + "." + class_definition.__name__
