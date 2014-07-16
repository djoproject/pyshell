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

#FIXME already exist in apdu.misc.util...
 
from string import rstrip

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
