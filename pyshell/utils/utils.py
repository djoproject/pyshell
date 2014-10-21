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

#FIXME toHexString already exist in apdu.misc.util...
 
from string import rstrip
import os

PACK = 1
HEX = 2
UPPERCASE = 4
COMMA = 8

def toHexString(bytes=[], format=0):
    #for byte in tuple(bytes): 
    #    pass 

    if not isinstance(bytes,list): 
        raise TypeError('not a list of bytes') 

    if bytes == None or bytes == []: 
        return "" 
    else: 
        pformat = "%-0.2X" 
        if COMMA & format: 
            pformat = pformat + "," 
        pformat = pformat + " " 
        if PACK & format: 
            pformat = rstrip(pformat) 
        if HEX & format: 
            if UPPERCASE & format: 
                pformat = "0X" + pformat 
            else: 
                pformat = "0x" + pformat 
                    
        return rstrip(rstrip(reduce(lambda a, b: a + pformat % ((b + 256) % 256), [""] + bytes)), ',')
        
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
        
        #TODO trim key
        
        if len(key) == 0:
            raise exceptionClass("("+packageName+") "+methName+", empty key is not allowed")
            

