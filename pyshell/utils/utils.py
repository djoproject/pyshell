#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
        
def ioctl_GWINSZ(fd):
    try:
        cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,'1234'))
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
    
def raiseIfInvalidKeyList(keyList, exceptionClass,packageName, methName):
    if not hasattr(keyList,"__iter__"):
        raise exceptionClass("("+packageName+") "+methName+", list of string is not iterable")

    for key in keyList:
        if type(key) != str and type(key) != unicode:
            raise exceptionClass("("+packageName+") "+methName+", only string or unicode key are allowed")
        
        #trim key
        key = key.strip()
        
        if len(key) == 0:
            raise exceptionClass("("+packageName+") "+methName+", empty key is not allowed")
            

