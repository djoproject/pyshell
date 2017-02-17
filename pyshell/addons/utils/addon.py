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

from pyshell.utils.constants import ADDONLIST_KEY
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_UNLOADED


def tryToGetDicoFromParameters(parameters):
    param = parameters.environment.getParameter(ADDONLIST_KEY,
                                                perfect_match=True)
    if param is None:
        raise Exception("no addon list defined")

    return param.getValue()


def tryToGetAddonFromDico(addon_dico, name):
    if name not in addon_dico:
        raise Exception("unknown addon '"+str(name)+"'")

    return addon_dico[name]


def tryToGetAddonFromParameters(parameters, name):
    return tryToGetAddonFromDico(tryToGetDicoFromParameters(parameters),
                                 name)


def tryToImportLoaderFromFile(name):
    try:
        mod = __import__(name, fromlist=["_loaders"], level=0)
    except ImportError as ie:
        raise Exception(
            "fail to load addon '" +
            str(name) +
            "', reason: " +
            str(ie))

    if not hasattr(mod, "_loaders"):
        raise Exception("invalid addon '"+str(name)+"', no loader found. "
                        "don't forget to register something in the addon")

    return mod._loaders


def formatState(state, printok, printwarning, printerror):
    if state == STATE_LOADED:
        return printok(state)
    elif state == STATE_UNLOADED:
        return printwarning(state)
    else:
        return printerror(state)
