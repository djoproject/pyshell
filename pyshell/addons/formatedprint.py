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

#TODO
    #comparison between two byte list
        #comparison on bit or byte
    
    #look after pattern
    
    #...

from pyshell.loader.command            import registerStopHelpTraversalAt, registerCommand, registerSetGlobalPrefix
from pyshell.utils.printing            import printShell, warning
from pyshell.utils.coloration          import orange,bolt
from pyshell.arg.decorator             import shellMethod
from pyshell.arg.argchecker            import listArgChecker, IntegerArgChecker, contextParameterChecker
from pyshell.simpleProcess.postProcess import printColumn

@shellMethod(bytelist = listArgChecker(IntegerArgChecker(0,255)),
             execution_context = contextParameterChecker("execution"))
             #FIXME ,bytePerLine =IntegerArgChecker(4,16))
def printByteTable(bytelist, bytePerLine = 5,execution_context=None):
    if len(bytelist) == 0:
        warning("empty list of byte")
    
    if execution_context.getSelectedValue() == "shell":
        title = bolt
        unknownChar = orange
    else:
        title = nocolor
        unknownChar = nocolor
    
    byteColumnSize = 3 * bytePerLine
    asciiColumnSize = bytePerLine + 2
    decimalColumnSize = 4 * bytePerLine + 1
    binarryColumnSize = 9 * bytePerLine
    
    #print header line
    printShell("Hex"+ " " * (byteColumnSize - 3) + "|" + " Char "+ " " * (asciiColumnSize - 6) + "|" + " Dec" + " " * (decimalColumnSize - 4) + "|" + " Bin")
    
    for i in range(0, len(bytelist), bytePerLine):
        hexa = ""
        ascii = ""
        intString = ""
        binString = ""
        subByteList = bytelist[i:i+bytePerLine]
        
        for h in subByteList:
            
            tmp = "%x"%h
            while len(tmp) < 2:
                tmp = "0"+tmp
            
            hexa += tmp+" "
            
            if h < 33 or h > 126:
                ascii += unknownChar(".") 
            else:
                ascii += chr(h)
            
            tmp = str(h)
            while len(tmp) < 3:
                tmp = "0"+tmp
            
            intString += tmp+" "
            
            tmp = bin(h)[2:]
            while len(tmp) < 8:
                tmp = "0"+tmp
            binString += tmp+" "
            
        printShell(hexa+ " " * (byteColumnSize - len(hexa)) +"| "+ascii+ " " * (asciiColumnSize - len(subByteList) -1)+"| "+intString+ " " * (decimalColumnSize - len(intString) -1)+"| "+binString)
                
registerSetGlobalPrefix( ("printing", ) )
registerStopHelpTraversalAt( () )
registerCommand( ( "bytelist",),  post=printByteTable) 


