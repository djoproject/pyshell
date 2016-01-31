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

import os
import struct
import fcntl
import termios

from pyshell.utils.exception import DefaultPyshellException, SYSTEM_WARNING


def ioctl_GWINSZ(fd):
    try:
        cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
    except:
        return
    return cr


def getTerminalSize():
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)

            os.close(fd)
        except:
            pass

    if not cr:
        env = os.environ
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

    return int(cr[1]), int(cr[0])


def raiseIfInvalidKeyList(keyList, exceptionClass, packageName, methName):
    # TODO test if a simple string could be a valid keyList,
    # it shouldn't be the case

    if not hasattr(keyList, "__iter__"):
        raise exceptionClass("("+packageName+") "+methName+", list of string "
                             "is not iterable")

    for key in keyList:
        if type(key) != str and type(key) != unicode:
            raise exceptionClass("("+packageName+") "+methName+", only string "
                                 "or unicode key are allowed")

        # trim key
        key = key.strip()

        if len(key) == 0:
            raise exceptionClass("("+packageName+") "+methName+", empty key "
                                 "is not allowed")

    return keyList


def createParentDirectory(filePath):
    if not os.path.exists(os.path.dirname(filePath)):
        try:
            os.makedirs(os.path.dirname(filePath))
        except os.error as ose:
            raise DefaultPyshellException("fail to create directory tree '" +
                                          os.path.dirname(filePath)+"', " +
                                          str(ose),
                                          SYSTEM_WARNING)

    elif not os.path.isdir(os.path.dirname(filePath)):
        raise DefaultPyshellException("'"+os.path.dirname(filePath)+"' is not "
                                      "a directory, nothing will be saved",
                                      SYSTEM_WARNING)
