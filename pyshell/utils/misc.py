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

import fcntl
import os
import struct
import termios

from pyshell.utils.exception import DefaultPyshellException, SYSTEM_WARNING


def ioctlGwinsz(fd):
    try:
        cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
    except:
        return
    return cr


def getTerminalSize():
    cr = ioctlGwinsz(0) or ioctlGwinsz(1) or ioctlGwinsz(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctlGwinsz(fd)

            os.close(fd)
        except:
            pass

    if not cr:
        env = os.environ
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

    return int(cr[1]), int(cr[0])


def createParentDirectory(file_path):
    if not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path))
        except os.error as ose:
            raise DefaultPyshellException("fail to create directory tree '" +
                                          os.path.dirname(file_path)+"', " +
                                          str(ose),
                                          SYSTEM_WARNING)

    elif not os.path.isdir(os.path.dirname(file_path)):
        raise DefaultPyshellException("'"+os.path.dirname(file_path)+"' is not"
                                      " a directory, nothing will be saved",
                                      SYSTEM_WARNING)
