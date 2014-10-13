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
from pyshell.utils.coloration          import orange, green,bolt, red
from pyshell.arg.decorator             import shellMethod
from pyshell.arg.argchecker            import defaultInstanceArgChecker, listArgChecker, IntegerArgChecker, contextParameterChecker, parameterDynamicChecker
from pyshell.simpleProcess.postProcess import printColumn

@shellMethod(varLists = listArgChecker(parameterDynamicChecker("main")))
            #,bytePerLine = IntegerArgChecker(4)) #FIXME
def compareByteList(varLists, bytePerLine = 4):
    #TODO
        #it is possible to inject something else than byte in the list, check them
        
        #row header are missing
            #but what to write ? not possible to get the variable name here
        
        #column header are also missing
            #id row
            
        #make an easy way to convert to binary
        
        #padding does not work
        
        #

    if len(varLists) == 0:
        return
        
    maxSize = 0
    for varList in varLists:
        maxSize = max(maxSize, len(varList.getValue()))
    
    #compute line size   
    columnSize = 3 * bytePerLine + 2     
        
    lineParts = ["| "] * len(varLists)
    
    for i in range(0,maxSize):
        commonBytes = {}
        
        maxValue = 0
        maxKey = None
        for varList in varLists:
            varListValue = varList.getValue()
            
            if i >= len(varListValue):
                continue
        
            if varListValue[i] not in commonBytes:
                commonBytes[ varListValue[i] ] = 1
                
                if maxKey is None:
                    maxKey = varListValue[i]
                    maxValue = 1
            else:
                commonBytes[ varListValue[i] ] += 1
                
                if commonBytes[ varListValue[i] ] > maxValue:
                    maxValue = commonBytes[ varListValue[i] ]
                    maxKey = varListValue[i]

        for j in range(0, len(varLists)):
            varListValue = varLists[j].getValue()
            
            if len(commonBytes) == 1:
                if i >= len(varListValue):
                    lineParts[j] += orange("XX ")
                else:
                    lineParts[j] += "%02x "%int(varListValue[i])

            elif len(commonBytes) == len(varLists):
                if i >= len(varListValue):
                    lineParts[j] += orange("XX ")
                else:
                    lineParts[j] += red("%02x "%int(varListValue[i]))
            else:
                if i >= len(varListValue):
                    lineParts[j] += orange("XX ")
                else:
                    if varListValue[i] == maxKey:
                        lineParts[j] += "%02x "%int(varListValue[i])
                    else:
                        lineParts[j] += red("%02x "%int(varListValue[i]))
        
        if (i+1)% (bytePerLine) == 0:
            finalLine = ""
            for linePart in lineParts:
                finalLine += linePart
            
            finalLine += "|"
            
            printShell(finalLine)
            lineParts = ["| "] * len(varLists)
    
    if (i+1)%(bytePerLine) != 0:
        finalLine = ""
        for linePart in lineParts:
            #TODO len(linePart) doit etre calculé sans les codes ansi
                #voir autre part dans le code
        
            finalLine += linePart + " " * (columnSize - len(linePart))
        
        finalLine += "|"
        
        printShell(finalLine)
        

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
registerCommand( ( "compareByte",),  post=compareByteList) 


