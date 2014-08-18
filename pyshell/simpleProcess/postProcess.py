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

from pyshell.arg.decorator import shellMethod
from pyshell.arg.argchecker import defaultInstanceArgChecker, listArgChecker, IntegerArgChecker, ArgChecker
from pyshell.utils.utils import toHexString

@shellMethod(result=listArgChecker(defaultInstanceArgChecker.getStringArgCheckerInstance())  )
def stringListResultHandler(result):
    for i in result:
        print(i)

@shellMethod(result=ArgChecker())
def printResultHandler(result=None):
    if result != None:
        print(str(result))

@shellMethod(result=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def listResultHandler(result):
    for i in result:
        print(str(i))
        
@shellMethod(result=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def listFlatResultHandler(result):
    s = ""
    for i in result:
        s += str(i) + " "
    
    print(s)

@shellMethod(string=listArgChecker(IntegerArgChecker(0,255)))
def printStringCharResult(string):
    s = ""
    for char in string:
        s += chr(char)
        
    print(s)

@shellMethod(byteList=listArgChecker(IntegerArgChecker(0,255)))
def printBytesAsString(byteList):
    if len(byteList) == 0:
        return byteList

    print(toHexString(byteList))
    
    return byteList

@shellMethod(listOfLine=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def printColumn(listOfLine):
    #compute size
    size = {}
    for line in listOfLine:
        if type(line) == str or type(line) == unicode or not hasattr(line,"__getitem__"):
            if 0 not in size:
                size[0] = len(str(line)) + 1
            else:
                size[0] = max(size[0],len(str(line)) + 1)
        else:
            for index in range(0,len(line)):
                if index not in size:
                    size[index] = len(str(line[index])) + 1
                else:
                    size[index] = max(size[index], len(str(line[index]))+1 )
    
    #print table
    for line in listOfLine:
        if type(line) == str or type(line) == unicode or not hasattr(line,"__getitem__"):
            padding = size[0] - len(str(line))
            if len(size) == 1:
                print(str(line))
            else:
                print(str(line) + " "*padding)
        else:
            line_to_print = ""
            for index in range(0,len(line)):
                padding = size[index] - len(str(line[index]))
                
                #no padding on last column
                if index == len(size) - 1:
                    line_to_print += str(line[index])
                else:
                    line_to_print += str(line[index]) + " "*padding
                
            print line_to_print
     
    
