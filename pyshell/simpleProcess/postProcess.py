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

from pyshell.arg.decorator  import shellMethod
from pyshell.arg.argchecker import defaultInstanceArgChecker, listArgChecker, IntegerArgChecker, ArgChecker
from pyshell.utils.utils    import toHexString
from pyshell.utils.printing import printShell
import re

@shellMethod(result=listArgChecker(defaultInstanceArgChecker.getStringArgCheckerInstance())  )
def stringListResultHandler(result):
    if len(result) == 0:
        return
    
    ret = ""
    for i in result:
        ret += i +"\n"
        
    printShell(ret[:-1])

@shellMethod(result=ArgChecker())
def printResultHandler(result=None):
    if result != None:
        printShell(str(result))

@shellMethod(result=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def listResultHandler(result):
    if len(result) == 0:
        return

    ret = ""
    for i in result:
        ret += str(i) +"\n"

    printShell(ret[:-1])
        
@shellMethod(result=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def listFlatResultHandler(result):
    if len(result) == 0:
        printShell("")
        return

    s = ""
    for i in result:
        s += str(i) + " "
    
    printShell(s[:-1])

@shellMethod(string=listArgChecker(IntegerArgChecker(0,255)))
def printStringCharResult(string):
    s = ""
    for char in string:
        s += chr(char)
        
    printShell(s)

@shellMethod(byteList=listArgChecker(IntegerArgChecker(0,255)))
def printBytesAsString(byteList):
    if len(byteList) == 0:
        return byteList

    printShell(toHexString(byteList))
    
    return byteList

@shellMethod(listOfLine=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def printColumn(listOfLine):
    ansi_escape = re.compile(r'\x1b[^m]*m')

    if len(listOfLine) == 0:
        return

    #compute size
    size = {}
    for line in listOfLine:
        if type(line) == str or type(line) == unicode or not hasattr(line,"__getitem__"):
            if 0 not in size:
                size[0] = len(ansi_escape.sub('', str(line))) + 1
            else:
                size[0] = max(size[0],len(ansi_escape.sub('', str(line))) + 1)
        else:
            for index in range(0,len(line)):
                if index not in size:
                    size[index] = len(ansi_escape.sub('', str(line[index]))) + 1
                else:
                    size[index] = max(size[index], len(ansi_escape.sub('', str(line[index])))+1 )
    
    to_print = ""
    #print table
    for line in listOfLine:
        if type(line) == str or type(line) == unicode or not hasattr(line,"__getitem__"):
            to_print += str(line) + "\n"
            
            #no need of pading if the line has only one column
        else:
            line_to_print = ""
            for index in range(0,len(line)):
                padding = size[index] - len(ansi_escape.sub('', str(line[index])))
                
                #no padding on last column
                if index == len(size) - 1:
                    line_to_print += str(line[index])
                else:
                    line_to_print += str(line[index]) + " "*padding
                
            to_print +=  line_to_print + "\n"
     
    printShell(to_print[:-1])
    
