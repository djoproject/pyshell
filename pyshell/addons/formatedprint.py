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

from pyshell.loader.command    import registerStopHelpTraversalAt, registerCommand, registerSetGlobalPrefix
from pyshell.arg.decorator     import shellMethod
from pyshell.arg.argchecker    import defaultInstanceArgChecker, listArgChecker, IntegerArgChecker, contextParameterChecker, parameterDynamicChecker
from pyshell.utils.postProcess import printColumn
from pyshell.utils.exception   import USER_ERROR, DefaultPyshellException
from pyshell.utils.printing    import printShell, warning, strLength, formatOrange, formatRed
from math                      import log

@shellMethod(varLists  = listArgChecker(defaultInstanceArgChecker.getStringArgCheckerInstance()),
            parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
            bytePerLine = IntegerArgChecker(4))
def compareByteList(varLists, bytePerLine = 4, parameters = None):
    #TODO
        #it is possible to inject something else than byte in the list, check them
            #DONE!
            #test it
                            
        #make an easy way to convert to binary
            #replace byte size from 3 to 9
            #replace conversion from hex to bin
            #replace empty string XX
            #coloration must occured on bit not on whole byte
            #convert each byte list to binary stream
                
    if len(varLists) == 0:
        return

    byteListChecker = listArgChecker(IntegerArgChecker(0,255))

    varListsValues = {}
    for i in range(0, len(varLists)):
        varKey = varLists[i]
        if not parameters.hasParameter(varKey):
            raise DefaultPyshellException("unknown variable '"+str(varKey)+"'", )

        varListsValues[varKey] = byteListChecker.getValue(parameters.getParameter(varKey).getValue(), i, varKey)
    
    #get the size of the bigger list of byte
    maxSize = 0
    for varName, varList in varListsValues.items():
        maxSize = max(maxSize, len(varList))

    #get the number of line
    lineCount = int(maxSize / bytePerLine) 

    if (maxSize % bytePerLine) > 0:
        lineCount += 1

    idColumnSize = int(log(lineCount,10)) + 1
    idLine = 0

    #compute line width   
        #an hexa number is printed with two number and one space
        #a first pipe
        #then a space
        #the final pipe is not in the calculus
    columnSize = 3 * bytePerLine + 2     
    lineParts = ["| "] * len(varListsValues)

    titleColumn = " " * (idColumnSize+1)

    for varName, varList in varListsValues.items(): 
        titleColumn += "| " + varName[0:columnSize-2] + " " * (columnSize - len(varName) - 2) 

    
    printShell(titleColumn + "|")
    for i in range(0,maxSize):

        commonBytesHight = {}
        maxKeyHigh = None
        maxValueHigh = 0

        commonBytesLow   = {}
        maxKeyLow = None
        maxValueLow = 0

        for varName, varListValue in varListsValues.items():            
            if i >= len(varListValue):
                continue
        
            hight = int(varListValue[i])&0xF0
            low = int(varListValue[i])&0x0F

            if hight not in commonBytesHight:
                commonBytesHight[ hight ] = 1
                
                if maxKeyHigh is None:
                    maxKeyHigh = hight
                    maxValueHigh = 1
            else:
                commonBytesHight[ hight ] += 1
                
                if commonBytesHight[ hight ] > maxValueHigh:
                    maxKeyHigh = hight
                    maxValueHigh = commonBytesHight[ hight ]
            
            if low not in commonBytesLow:
                commonBytesLow[ low ] = 1
                
                if maxKeyLow is None:
                    maxKeyLow = low
                    maxValueLow = 1
            else:
                commonBytesLow[ low ] += 1
                
                if commonBytesLow[ low ] > maxValueLow:
                    maxKeyLow = low
                    maxValueLow = commonBytesLow[ low ]

        j = -1
        for varName,varListValue in varListsValues.items():
            j += 1         
            #high
            if len(commonBytesHight) == 1:
                if i >= len(varListValue):
                    lineParts[j] += formatOrange("xx ")
                    continue

                lineParts[j] += "%x"%((int(varListValue[i])&0xF0)>>4)

            elif len(commonBytesHight) == len(varListValue):
                if i >= len(varListValue):
                    lineParts[j] += formatOrange("xx ")
                    continue

                lineParts[j] += formatRed("%x"%((int(varListValue[i])&0xF0)>>4))
            else:
                if i >= len(varListValue):
                    lineParts[j] += formatOrange("xx ")
                    continue

                if varListValue[i] == maxKeyHigh:
                    lineParts[j] += "%x"%((int(varListValue[i])&0xF0)>>4)
                else:
                    lineParts[j] += formatRed("%x"%((int(varListValue[i])&0xF0)>>4))

            #low
            if len(commonBytesLow) == 1:
                lineParts[j] += "%x "%(int(varListValue[i])&0x0F)

            elif len(commonBytesLow) == len(varListValue):
                lineParts[j] += formatRed("%x "%(int(varListValue[i])&0x0F))
            else:
                if varListValue[i] == maxKeyLow:
                    lineParts[j] += "%x "%(int(varListValue[i])&0x0F)
                else:
                    lineParts[j] += formatRed("%x "%(int(varListValue[i])&0x0F))
        
        #new line
        if (i+1)% (bytePerLine) == 0:
            finalLine = ""
            for linePart in lineParts:
                finalLine += linePart
            
            finalLine += "|"
            
            idLineStr = str(idLine)
            idLineStr = " "*(idColumnSize - len(idLineStr) - 1) + idLineStr + " "
            printShell(idLineStr + finalLine)
            idLine += 1
            lineParts = ["| "] * len(varListsValues)
    
    #we do not finish on a complete line, add padding
    if (i+1)%(bytePerLine) != 0:
        finalLine = ""
        for linePart in lineParts:        
            finalLine += linePart + " " * (columnSize - strLength(linePart))
        
        finalLine += "|"
        
        idLineStr = str(idLine)
        idLineStr = " "*(idColumnSize - len(idLineStr) - 1) + idLineStr + " "
        printShell(idLineStr + finalLine)
        

@shellMethod(bytelist = listArgChecker(IntegerArgChecker(0,255)),
             bytePerLine =IntegerArgChecker(4,16))
def printByteTable(bytelist, bytePerLine = 4):
    if len(bytelist) == 0:
        warning("empty list of byte")
        
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
                ascii += formatOrange(".") 
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


