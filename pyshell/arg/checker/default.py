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

from threading import Lock

from pyshell.arg.checker.argchecker import ArgChecker
from pyshell.arg.checker.boolean import BooleanValueArgChecker
from pyshell.arg.checker.file import FilePathArgChecker
from pyshell.arg.checker.float import FloatArgChecker
from pyshell.arg.checker.integer import BinaryArgChecker
from pyshell.arg.checker.integer import HexaArgChecker
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.arg.checker.integer import LimitedInteger
from pyshell.arg.checker.key import KeyArgChecker
from pyshell.arg.checker.string43 import StringArgChecker


class DefaultChecker(object):
    _lock = Lock()

    DEFAULTCHECKER_DICO = {ArgChecker.getTypeName(): None,
                           BooleanValueArgChecker.getTypeName(): None,
                           FilePathArgChecker.getTypeName(): None,
                           FloatArgChecker.getTypeName(): None,
                           BinaryArgChecker.getTypeName(): None,
                           HexaArgChecker.getTypeName(): None,
                           IntegerArgChecker.getTypeName(): None,
                           LimitedInteger.getTypeName(): None,
                           KeyArgChecker.getTypeName(): None,
                           StringArgChecker.getTypeName(): None}

    @classmethod
    def _getCheckerInstance(cls, classdef):
        key = classdef.getTypeName()
        if cls.DEFAULTCHECKER_DICO[key] is None:
            with cls._lock:
                if cls.DEFAULTCHECKER_DICO[key] is None:
                    cls.DEFAULTCHECKER_DICO[key] = classdef()
                    cls.DEFAULTCHECKER_DICO[key].setDefaultValueEnable(False)

        return cls.DEFAULTCHECKER_DICO[key]

    @classmethod
    def getArg(cls):
        return cls._getCheckerInstance(ArgChecker)

    @classmethod
    def getBoolean(cls):
        return cls._getCheckerInstance(BooleanValueArgChecker)

    @classmethod
    def getFile(cls):
        return cls._getCheckerInstance(FilePathArgChecker)

    @classmethod
    def getFloat(cls):
        return cls._getCheckerInstance(FloatArgChecker)

    @classmethod
    def getBinary(cls):
        return cls._getCheckerInstance(BinaryArgChecker)

    @classmethod
    def getHexa(cls):
        return cls._getCheckerInstance(HexaArgChecker)

    @classmethod
    def getInteger(cls):
        return cls._getCheckerInstance(IntegerArgChecker)

    @classmethod
    def getLimitedInteger(cls):
        return cls._getCheckerInstance(LimitedInteger)

    @classmethod
    def getKey(cls):
        return cls._getCheckerInstance(KeyArgChecker)

    @classmethod
    def getString(cls):
        return cls._getCheckerInstance(StringArgChecker)
