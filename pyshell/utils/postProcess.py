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
#from pyshell.utils.utils    import toHexString
from pyshell.utils.printing import printShell, strLength
import re

@shellMethod(result=listArgChecker(defaultInstanceArgChecker.getStringArgCheckerInstance())  )
def stringListResultHandler(result):
    if len(result) == 0:
        return
    
    ret = ""
    for i in result:
        ret += i +"\n"
        
    printShell(ret[:-1])

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

    return result

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
        
    ret = ""
    for b in byteList:
        ret += "%-0.2X"%b
        
    printShell(ret)
    
    return byteList

def printColumnWithouHeader():
    pass #TODO (needed to list all parameter, see addon/parameter)

@shellMethod(listOfLine=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def printColumn(listOfLine):
    if len(listOfLine) == 0:
        return
    #compute size
    size = {}
    spaceToAdd = 2 #at least two space column separator
    
    for row_index in range(0,len(listOfLine)):
        line = listOfLine[row_index]
        
        if row_index == 1: #space to add to have the data column slighty on the right
            spaceToAdd += 1
        
        if type(line) == str or type(line) == unicode or not hasattr(line,"__getitem__"):
            if 0 not in size:
                size[0] = strLength(str(line)) + spaceToAdd
            else:
                size[0] = max(size[0],strLength(str(line)) + spaceToAdd)
        else:
            for column_index in range(0,len(line)):
                if column_index not in size:
                    size[column_index] = strLength(str(line[column_index])) + spaceToAdd
                else:
                    size[column_index] = max(size[column_index], strLength (str(line[column_index])) +spaceToAdd )
    
    to_print = ""
    #print table
    defaultPrefix = ""
    for row_index in range(0,len(listOfLine)):
        line = listOfLine[row_index]
        
        if row_index == 1:
            defaultPrefix = " "
        
        if type(line) == str or type(line) == unicode or not hasattr(line,"__getitem__"):
            to_print += defaultPrefix + str(line) + "\n"
            
            #no need of pading if the line has only one column
        else:
            line_to_print = ""
            for column_index in range(0,len(line)):
                padding = size[column_index] - strLength(str(line[column_index])) - len(defaultPrefix)
                
                #no padding on last column
                if column_index == len(size) - 1:
                    line_to_print += defaultPrefix + str(line[column_index])
                else:
                    line_to_print += defaultPrefix + str(line[column_index]) + " "*padding
                
            to_print +=  line_to_print + "\n"
     
    printShell(to_print[:-1])
    
