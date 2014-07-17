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
    #hasdefault, getdefault, ... peuvent egalement balancer des exceptions
        #ça pourrait être interessant d'avoir également un argNumber
            #NON car si on joue avec les hasDefault, getDefault, c'est qu'il n'y a pas/plus de string token pour ces archecker là
                #juste besoin de l'arg name de destination
        
    #en plus de l'argNumber, cela pourrait être interessant d'avoir le argName de destination


from exception import *
from tries import tries
from tries.exception import ambiguousPathException
import collections # for collections.Hashable
from math import log
import os

ARGCHECKER_TYPENAME                 = "ArgChecker"
STRINGCHECKER_TYPENAME              = "String"
INTEGERCHECKER_TYPENAME             = "Integer"
LIMITEDINTEGERCHECKER_TYPENAME      = "Limited integer"
HEXACHECKER_TYPENAME                = "Hexadecimal"
BINARYCHECKER_TYPENAME              = "Binary"
FILEPATHCHECKER_TYPENAME            = "filePath"
LISTCHECKER_TYPENAME                = "List"
DEFAULTVALUE_TYPENAME               = "Default"
ENVIRONMENTDYNAMICCHECKER_TYPENAME  = "Environment dynamic"
CONTEXTDYNAMICCHECKER_TYPENAME      = "Context dynamic"
ENVIRONMENTCHECKER_TYPENAME         = "Environment"
CONTEXTCHECKER_TYPENAME             = "Context"
PARAMETERDYNAMICCHECKER_TYPENAME    = "Parameter dynamic"
PARAMETERCHECKER_TYPENAME           = "Parameter"
COMPLETEENVIRONMENTCHECKER_TYPENAME = "Complete Environment"
ENGINECHECKER_TYPENAME              = "Engine"
FLOATCHECKER_TYPENAME               = "Float"
BOOLEANCHECKER_TYPENAME             = "Boolean"
TOKENCHECKER_TYPENAME               = "Token"

###############################################################################################
##### ArgChecker ##############################################################################
###############################################################################################

class ArgChecker(object):
    def __init__(self,minimumSize = 1,maximumSize = 1,showInUsage=True, typeName = ARGCHECKER_TYPENAME):
        self.typeName    = typeName
        
        if minimumSize != None:
            if type(minimumSize) != int:
                raise argInitializationException("("+self.typeName+") Minimum size must be an integer, got type <"+str(type(minimumSize))+"> with the following value <"+str(minimumSize)+">")
                
            if minimumSize < 0:
                raise argInitializationException("("+self.typeName+") Minimum size must be a positive value, got <"+str(minimumSize)+">")
        
        if maximumSize != None:
            if type(maximumSize) != int:
                raise argInitializationException("("+self.typeName+") Maximum size must be an integer, got type <"+str(type(maximumSize))+"> with the following value <"+str(maximumSize)+">") 
        
            if maximumSize < 0:
                raise argInitializationException("("+self.typeName+") Maximum size must be a positive value, got <"+str(maximumSize)+">") 
    
        if minimumSize != None and maximumSize != None and maximumSize < minimumSize:
            raise argInitializationException("("+self.typeName+") Maximum size <"+str(maximumSize)+"> can not be smaller than Minimum size <"+str(minimumSize)+">") 
    
        self.minimumSize = minimumSize
        self.maximumSize = maximumSize
        self.hasDefault  = False
        self.default     = None
        self.showInUsage = showInUsage
        self.engine      = None
        
    def isVariableSize(self):
        return (self.minimumSize == self.maximumSize == None) or self.minimumSize != self.maximumSize
    
    def needData(self):
        return self.minimumSize != None and self.minimumSize > 0
        #return not (self.minimumSize == self.maximumSize == 0)
        
    def getValue(self,value,argNumber=None):
        return value #XXX override it if needed
        
    def getUsage(self):
        return "<any>"
        
    def getDefaultValue(self):
        if not self.hasDefaultValue():
            self._raiseArgException("there is no default value")
    
        return self.default
        
    def hasDefaultValue(self):
        return self.hasDefault
        
    def setDefaultValue(self,value):
        self.hasDefault = True
        
        if value == None:
            self.default = None
            return
            
        self.default = self.getValue(value) #will convert the value if needed
        
    def erraseDefaultValue(self):
        self.hasDefault = False
        self.default = None
        
    def setEngine(self, engine):
        self.engine = engine
        
    def _raiseIfEnvIsNotAvailable(self, argNumber=None):
        if self.engine is None:
            self._raiseArgException("can not get Environment, no engine linked to this argument instance", argNumber)
        
        if not hasattr(self.engine,"getEnv"):
            self._raiseArgException("can not get Environment, linked engine does not have a method to get the environment", argNumber)
            
        if self.engine.getEnv() == None:
            self._raiseArgException("can not get Environment, no environment linked to the engine", argNumber)
    
    def _isEnvAvailable(self):
        return not (self.engine == None or not hasattr(self.engine,"getEnv") or self.engine.getEnv() == None)
        
    def _raiseArgException(self, message, argNumber=None):
        raise argException("("+self.typeName+") Argument %s: "%("" if argNumber == None else str(argNumber)+str(self.minimum)) + message)
    
class stringArgChecker(ArgChecker):
    def __init__(self, typeName = STRINGCHECKER_TYPENAME):
        ArgChecker.__init__(self,1,1,True, typeName)

    def getValue(self, value,argNumber=None):
        value = ArgChecker.getValue(self, value,argNumber)

        if value is None:
            self._raiseArgException("the string arg can't be None", argNumber)

        if type(value) != str and type(value) != unicode:
            if hasattr(value, "__str__"):
                return str(value)
        
            self._raiseArgException("this value <"+str(value)+"> is not a valid string, got type <"+str(type(value))+">", argNumber)
    
        return value
    
    def getUsage(self):
        return "<string>"

class IntegerArgChecker(ArgChecker):
    def __init__(self, minimum=None, maximum=None, typeName=INTEGERCHECKER_TYPENAME):
        ArgChecker.__init__(self,1,1,True,typeName)
        
        if not hasattr(self, "shortType"):
            self.shortType     = "int"
        
        if not hasattr(self, "bases"):
            self.bases = [10, 16, 2]
        
        if minimum != None and type(minimum) != int and type(minimum) != float:
            raise argInitializationException("("+self.typeName+") Minimum must be an integer or None, got <"+str(type(minimum))+">")
            
        if maximum != None and type(maximum) != int and type(maximum) != float:
            raise argInitializationException("("+self.typeName+") Maximum must be an integer or None, got <"+str(type(maximum))+">")
            
        if minimum != None and maximum != None and maximum < minimum:
            raise argInitializationException("("+self.typeName+") Maximum size <"+str(maximum)+"> can not be smaller than Minimum size <"+str(minimum)+">")
        
        self.minimum = minimum
        self.maximum = maximum

    def getValue(self, value,argNumber=None):
        value = ArgChecker.getValue(self, value,argNumber)
    
        if value == None:
            self._raiseArgException("the "+self.completeType.lower()+" arg can't be None", argNumber)
        
        castedValue = None
        if type(value) == int or type(value) == float or type(value) == bool:
            castedValue = int(value)
        elif type(value) == str or type(value) == unicode:
            for b in self.bases:
                try:
                    castedValue = int(value, b)
                    break
                except ValueError as ve:
                    continue

        if castedValue == None:
            self._raiseArgException("this arg is not a valid "+self.completeType.lower()+" or hexadecimal, got <"+str(value)+">", argNumber)

        if self.minimum != None:
            if castedValue < self.minimum:
                self._raiseArgException("the lowest value must be bigger or equal than <"+str(self.minimum) +">, got <"+str(value)+">", argNumber)
                
        if self.maximum != None:
            if castedValue > self.maximum:
                self._raiseArgException("the biggest value must be lower or equal than <"+str(self.maximum)+">, got <"+str(value)+">", argNumber)

        return castedValue
            
    def getUsage(self):
        if self.minimum != None:
            if self.maximum != None:
                return "<"+self.shortType+" "+str(self.minimum)+"-"+str(self.maximum)+">"
            return "<"+self.shortType+" "+str(self.minimum)+"-*>"
        else:
            if self.maximum != None:
                return "<"+self.shortType+" *-"+str(self.maximum)+">"
        return "<"+self.shortType+">"

class LimitedInteger(IntegerArgChecker):
    def __init__(self, amountOfBit=8, signed = False):
        if amountOfBit < 8:
            raise argInitializationException("("+LIMITEDINTEGERCHECKER_TYPENAME+") the amount of bit must at least be 8, got <"+str(amountOfBit)+">")
    
        if log(amountOfBit, 2)%1 != 0:
            raise argInitializationException("("+LIMITEDINTEGERCHECKER_TYPENAME+") only powers of 2 are allowed, 8, 16, 32, 64, ..., got <"+str(amountOfBit)+">")

        if signed:
            IntegerArgChecker.__init__(self, -(2**(amountOfBit-1)), (2**(amountOfBit-1))-1, True, LIMITEDINTEGERCHECKER_TYPENAME)
        else:
            IntegerArgChecker.__init__(self, 0x0, (2**amountOfBit) -1, True, LIMITEDINTEGERCHECKER_TYPENAME)

class hexaArgChecker(IntegerArgChecker):
    def __init__(self, minimum=None, maximum=None):
        self.bases = [16]
        self.shortType     = "hex"
        IntegerArgChecker.__init__(self, minimum,maximum, True, HEXACHECKER_TYPENAME)
        
class binaryArgChecker(IntegerArgChecker):
    def __init__(self, minimum=None, maximum=None):
        self.bases = [2]
        self.shortType     = "bin"
        IntegerArgChecker.__init__(self, minimum,maximum, True, BINARYCHECKER_TYPENAME)

class tokenValueArgChecker(stringArgChecker):
    def __init__(self, tokenDict, typename=TOKENCHECKER_TYPENAME):
        stringArgChecker.__init__(self, typename)
        if not isinstance(tokenDict, dict):
            raise argInitializationException("("+self.typeName+") tokenDict must be a dictionary, got <"+str(type(tokenDict))+">")
        
        self.localtries = tries()
        for k,v in tokenDict.iteritems():
            #key must be non empty string, value can be anything
            if type(k) != str and type(k) != unicode:
                raise argInitializationException("("+self.typeName+") a key in the dictionary is not a string: <"+str(k)+">, type: <"+str(type(k))+">")

            self.localtries.insert(k,v)
    
    def getValue(self, value,argNumber=None):
        value = super(tokenValueArgChecker,self).getValue(value,argNumber)

        try:
            node = self.localtries.search(value)
            if node == None:
                self._raiseArgException("this arg <"+str(value)+"> is not an existing token, valid token are ("+ ("|".join(self.localtries.getKeyList())) + ")", argNumber)
            return node.value
            
        except ambiguousPathException:
            self._raiseArgException("this arg <"+str(value)+"> is ambiguous, valid token are ("+ ("|".join(self.localtries.getKeyList())) + ")", argNumber)
        
    def getUsage(self):
        return "("+ ("|".join(self.localtries.getKeyList())) + ")"

class booleanValueArgChecker(tokenValueArgChecker):
    def __init__(self,TrueName=None,FalseName=None):
        if TrueName == None:
            TrueName = "true"
            
        if FalseName == None:
            FalseName = "false"
    
        #the constructor of tokenValueArgChecker will check if every keys are 
        tokenValueArgChecker.__init__(self,{TrueName:True,FalseName:False}, BOOLEANCHECKER_TYPENAME)
        self.TrueName = TrueName
        self.FalseName = FalseName
    
    def getValue(self,value,argNumber=None):
        if type(value) == bool:
            if value:
                value = self.TrueName
            else:
                value = self.FalseName
        else:
            value = str(value).lower()

        return tokenValueArgChecker.getValue(self,value,argNumber)
    
class floatTokenArgChecker(ArgChecker):
    def __init__(self, minimum=None, maximum=None):
        ArgChecker.__init__(self,1,1,True, FLOATCHECKER_TYPENAME)
    
        if minimum != None and type(minimum) != float and type(minimum) != int:
            raise argInitializationException("("+self.typeName+") Minimum must be a float or None, got <"+str(type(minimum))+">")
            
        if maximum != None and type(maximum) != float and type(maximum) != int:
            raise argInitializationException("("+self.typeName+") Maximum must be a float or None, got <"+str(type(maximum))+">")
            
        if minimum != None and maximum != None and maximum < minimum:
            raise argInitializationException("("+self.typeName+") Maximum <"+str(maximum)+"> can not be smaller than Minimum <"+str(minimum)+">")
    
        self.minimum = minimum
        self.maximum = maximum
    
    def getValue(self, value,argNumber=None):
        value = ArgChecker.getValue(self, value,argNumber)
    
        if value == None:
            self._raiseArgException("the float arg can't be None", argNumber)
        
        try:
            castedValue = float(value)
        except ValueError:
            self._raiseArgException("this arg is not a valid float or hexadecimal, got <"+str(value)+">", argNumber)
                
        if self.minimum != None:
            if castedValue < self.minimum:
                self._raiseArgException("the lowest value must be bigger or equal than <"+str(self.minimum) + ">, got <"+str(value)+">", argNumber)
                
        if self.maximum != None:
            if castedValue > self.maximum:
                self._raiseArgException("the biggest value must be lower or equal than <"+str(self.maximum)+ ">, got <"+str(value)+">", argNumber)

        return castedValue    
        
    def getUsage(self):
        if self.minimum != None:
            if self.maximum != None:
                return "<float "+str(self.minimum)+"-"+str(self.maximum)+">"
            return "<float "+str(self.minimum)+"-*.*>"
        else:
            if self.maximum != None:
                return "<float *.*-"+str(self.maximum)+">"
        return "<float>"

class engineChecker(ArgChecker):
    def __init__(self):
        ArgChecker.__init__(self,0,0,False, ENGINECHECKER_TYPENAME)
        
    def getValue(self,value,argNumber=None):
        return self.engine
        
    def usage(self):
        return ""
        
    def getDefaultValue(self):
        return self.engine
        
    def hasDefaultValue(self):
        return True
        
    def setDefaultValue(self,value):
        pass
        
    def erraseDefaultValue(self):
        pass

##

class completeEnvironmentChecker(ArgChecker):
    def __init__(self):
        ArgChecker.__init__(self,0,0,False, COMPLETEENVIRONMENTCHECKER_TYPENAME)
        
    def getValue(self,value,argNumber=None):
        self._raiseIfEnvIsNotAvailable(argNumber)
        return self.engine.getEnv()
        
    def usage(self):
        return ""
        
    def getDefaultValue(self):
        self._raiseIfEnvIsNotAvailable()
        return self.engine.getEnv()
        
    def hasDefaultValue(self):
        return self._isEnvAvailable()#n not isinstance(self.engine.getEnv(), ParameterManager)
        
    def setDefaultValue(self,value):
        pass
        
    def erraseDefaultValue(self):
        pass

class parameterChecker(ArgChecker):
    def __init__(self,keyname, parent = None, typeName = PARAMETERCHECKER_TYPENAME):
        ArgChecker.__init__(self,0,0,False, typeName)
        
        if keyname == None or (type(keyname) != str and type(keyname) != unicode) or not isinstance(keyname, collections.Hashable):
            raise argInitializationException("("+self.typeName+") keyname must be hashable string, got <"+str(keyname)+">")
        
        self.keyname = keyname
        self.parent = None
    
    def getValue(self,value,argNumber=None):
        self._raiseIfEnvIsNotAvailable(argNumber)
        env = self.engine.getEnv()

        if not env.hasParameter(self.keyname, self.parent):#self.keyname not in self.engine.getEnv():
            self._raiseArgException("the key <"+self.keyname+"> is not available but needed", argNumber)
    
        return env.getParameter(self.keyname, self.parent) #self.engine.getEnv()[self.keyname][0]
        
    def usage(self):
        return ""
        
    def getDefaultValue(self):
        self._raiseIfEnvIsNotAvailable()
        return self.engine.getEnv().getParameter(self.keyname, self.parent)#self.engine.getEnv()[self.keyname][0]
        
    def hasDefaultValue(self):
        self._raiseIfEnvIsNotAvailable()
        return self.engine.getEnv().hasParameter(self.keyname, self.parent)#self.keyname not in self.engine.getEnv()
        
    def setDefaultValue(self,value):
        pass
        
    def erraseDefaultValue(self):
        pass

class parameterDynamicChecker(ArgChecker):
    def __init__(self, parent = None, typeName = PARAMETERDYNAMICCHECKER_TYPENAME):
        ArgChecker.__init__(self,1,1,False, typeName)
        self.parent = parent
    
    def getValue(self,value,argNumber=None):
        self._raiseIfEnvIsNotAvailable(argNumber)
        if not isinstance(value, collections.Hashable):
            self._raiseArgException("keyname must be hashable, got <"+str(value)+">", argNumber)
        
        env = self.engine.getEnv()

        if not self.engine.getEnv().hasParameter(value, self.parent): #value not in self.engine.getEnv():
            self._raiseArgException("the key <"+self.keyname+"> is not available but needed", argNumber)
    
        return self.engine.getEnv().getParameter(self.keyname, self.parent) #self.engine.getEnv()[value][0]
    
    def hasDefaultValue(self):
        return False
        
    def setDefaultValue(self,value):
        pass
        
    def erraseDefaultValue(self):
        pass

class contextParameterChecker(parameterChecker):
    def __init__(self, keyname):
        parameterChecker.__init__(self, keyname, "context", CONTEXTCHECKER_TYPENAME)

class environmentParameterChecker(parameterChecker):
    def __init__(self, keyname):
        parameterChecker.__init__(self, keyname, "context", ENVIRONMENTCHECKER_TYPENAME)

class contextParameterDynamicChecker(parameterDynamicChecker):
    def __init__(self):
        parameterDynamicChecker.__init__(self, "context", CONTEXTDYNAMICCHECKER_TYPENAME)

class environmentParameterDynamicChecker(parameterDynamicChecker):
    def __init__(self):
        parameterDynamicChecker.__init__(self, "context", ENVIRONMENTDYNAMICCHECKER_TYPENAME)

class defaultValueChecker(ArgChecker):
    def __init__(self,value):
        ArgChecker.__init__(self,0,0,False, DEFAULTVALUE_TYPENAME)
        self.setDefaultValue(value)
    
    def setDefaultValue(self,value):
        self.hasDefault = True
        self.default = value #no check on the value...
    
    def getValue(self,value,argNumber=None):
        return self.getDefaultValue()

class listArgChecker(ArgChecker):
    def __init__(self,checker,minimumSize=None,maximumSize=None):
        if not isinstance(checker, ArgChecker) or isinstance(checker, listArgChecker):
            raise argInitializationException("("+LISTCHECKER_TYPENAME+") checker must be an instance of ArgChecker but can not be an instance of listArgChecker, got <"+str(type(checker))+">")

        #checker must have a fixed size
        if checker.minimumSize != checker.maximumSize or checker.minimumSize == None or checker.minimumSize == 0:

            if checker.minimumSize is None:
                checkerSize = "]-Inf,"
            else:
                checkerSize = "["+str(checker.minimumSize)+","
                
            if checker.maximumSize is None:
                checkerSize += "+Inf["
            else:
                checkerSize += str(checker.maximumSize)+"]"
        
            raise argInitializationException("("+LISTCHECKER_TYPENAME+") checker must have a fixed size bigger than zero, got this sizer : "+checkerSize)
    
        if minimumSize != None and (minimumSize % checker.minimumSize)  != 0:
            raise argInitializationException("("+LISTCHECKER_TYPENAME+") the minimum size of the list <"+str(minimumSize)+"> is not a multiple of the checker size <"+str(checker.minimumSize)+">")
            
        if maximumSize != None and (maximumSize % checker.minimumSize)  != 0:
            raise argInitializationException("("+LISTCHECKER_TYPENAME+") the maximum size of the list <"+str(maximumSize)+"> is not a multiple of the checker size <"+str(checker.minimumSize)+">")
        
        ArgChecker.__init__(self,minimumSize,maximumSize, True, LISTCHECKER_TYPENAME)
        self.checker = checker
    
    def getValue(self,values,argNumber=None):    
        #check if it's a list
        if not hasattr(values, "__iter__"):#if not isinstance(values,list):
            self._raiseArgException("this arg is not a valid list, not iterable",argNumber)
        
        #len(values) must always be a multiple of self.checker.minimumSize
            #even if there is to much data, it is a sign of anomalies
        if (len(values) % self.checker.minimumSize)  != 0:
            self._raiseArgException("the size of the value list <"+str(len(values))+"> is not a multiple of the checker size <"+str(self.checker.minimumSize)+">",argNumber)
        
        #check the minimal size
        addAtEnd = []
        if self.minimumSize != None and len(values) < self.minimumSize:            
            #checker has default value ?
            if self.checker.hasDefaultValue():
                #build the missing part with the default value
                addAtEnd = ((self.minimumSize - len(values)) / self.checker.minimumSize) * [self.checker.getDefaultValue()]
            else:
                self._raiseArgException("need at least "+str(self.minimumSize))+" items, got "+str(len(values),argNumber)
        
        #build range limite and manage max size
        if self.maximumSize != None:
            if len(values) < self.maximumSize:
                msize = len(values)
            else:
                msize = self.maximumSize
        else:
            msize = len(values)
        
        #check every args
        ret = []
        if argNumber != None:
            for i in range(0,msize, self.checker.minimumSize):
                if self.checker.minimumSize == 1:
                    ret.append(self.checker.getValue(values[i],argNumber))
                else:
                    ret.append(self.checker.getValue(values[i:i+self.checker.minimumSize],argNumber))
                    
                argNumber += 1
        else:
            for i in range(0,msize, self.checker.minimumSize):
                if self.checker.minimumSize == 1:
                    ret.append(self.checker.getValue(values[i]))
                else:
                    ret.append(self.checker.getValue(values[i:i+self.checker.minimumSize]))
        
        #add the missing part
        ret.extend(addAtEnd)
        return ret 
    
    def getDefaultValue(self):
        if self.hasDefault:
            return self.default
    
        if self.minimumSize == None:
            return []
    
        if self.checker.hasDefaultValue():
            return [self.checker.getDefaultValue()] * self.minimumSize
        
        self._raiseArgException("getDefaultValue, there is no default value")
        
    def hasDefaultValue(self):
        return self.hasDefault or self.minimumSize == None or self.checker.hasDefaultValue()
    
    def getUsage(self):
        if self.minimumSize == None :
            if self.maximumSize == None :
                return "("+self.checker.getUsage()+" ... "+self.checker.getUsage()+")"
            elif self.maximumSize == 1:
                return "("+self.checker.getUsage()+")"
            elif self.maximumSize == 2:
                return "("+self.checker.getUsage()+"0 "+self.checker.getUsage()+"1)"
                
            return "("+self.checker.getUsage()+"0 ... "+self.checker.getUsage()+str(self.maximumSize-1)+")"
        else:
            if self.minimumSize == 0 and self.maximumSize == 1:
                return "("+self.checker.getUsage()+")" 
        
            if self.minimumSize == 1:
                if self.maximumSize == 1:
                    return self.checker.getUsage()
            
                part1 = self.checker.getUsage()+"0"
            elif self.minimumSize == 2:
                part1 = self.checker.getUsage() + "0 " + self.checker.getUsage()+"1"
            else:
                part1 = self.checker.getUsage() + "0 ... " + self.checker.getUsage()+str(self.minimumSize-1)
        
            if self.maximumSize == None :
                return part1 + " (... "+self.checker.getUsage()+")"
            else:
                notMandatorySpace = self.maximumSize - self.minimumSize
                if notMandatorySpace == 0:
                    return part1
                if notMandatorySpace == 1:
                    return part1 + " ("+self.checker.getUsage()+str(self.maximumSize-1)+")"
                elif notMandatorySpace == 2:
                    return part1 + " ("+self.checker.getUsage()+str(self.maximumSize-2)+""+self.checker.getUsage()+str(self.maximumSize-1)+")"
                else:
                    return part1 + " ("+self.checker.getUsage()+str(self.minimumSize)+" ... "+self.checker.getUsage()+str(self.maximumSize-1)+")"
                    
    def __str__(self):
        return "listArgChecker : "+str(self.checker)
        
class filePathArgChecker(stringArgChecker):
    def __init__(self, exist=None, readable=None, writtable=None, isFile=None):
        stringArgChecker.__init__(self, FILEPATHCHECKER_TYPENAME)
    
        if exist != None and type(exist) != bool:
            raise argInitializationException("("+self.typeName+") exist must be None or a boolean, got <"+str(type(exist))+">")
            
        if readable != None and type(readable) != bool:
            raise argInitializationException("("+self.typeName+") readable must be None or a boolean, got <"+str(type(readable))+">")
            
        if writtable != None and type(writtable) != bool:
            raise argInitializationException("("+self.typeName+") writtable must be None or a boolean, got <"+str(type(writtable))+">")
            
        self.exist     = exist
        self.readable  = readable
        self.writtable = writtable

    def getValue(self, value,argNumber=None):
        path = stringArgChecker.getValue(self, value,argNumber)

        fileExist = None
        
        #TODO isFile
        
        #exist
        if self.exist is not None:
            fileExist = os.access(path, os.F_OK)
            
            if self.exist and not fileExist:
                self._raiseArgException("keyname must be hashable, got <"+str(value)+">",argNumber)
                
            if not self.exist and fileExist:
                pass #raise file does not exist and must
                
        #readable
        if self.readable is not None:
            if fileExist is None:
                fileExist = os.access(path, os.F_OK)
                
            if not fileExist:
                pass #raise, not exist and must be readable
            
            readable = os.access(path, os.R_OK)
            
            if self.readable and not readable:
                pass #no read access to this file and need it
            
            if not self.readable and readable:
                pass #read access available and don't wanted
        
        #writtable
        if self.writtable is not None:
            #XXX return False if path does not exist...
            writtable = os.access(path, os.W_OK)
            
            if self.writtable and not writtable:
                pass #no writtable access to this file and need it
            
            if not self.writtable and writtable:
                pass #writtable access available and don't wanted
        
        return value
    
    def getUsage(self):
        return "<file_path>"
        
class keyStoreTranslatorArgChecker(stringArgChecker):
    def __init__(self, keySize = None, byteKey=True):
        stringArgChecker.__init__(self, FILEPATHCHECKER_TYPENAME)
        
        if keySize != None:
            if type(keySize) != int:
                raise argInitializationException("("+self.typeName+") keySize must be an integer, got <"+str(type(keySize))+">")
                
            if type(keySize) < 0:
                raise argInitializationException("("+self.typeName+") keySize must be bigger than 0, got <"+str(tkeySize)+">")
        
        if byteKey == None or type(byteKey) != bool:
            raise argInitializationException("("+self.typeName+") byteKey must be a boolean, got <"+str(type(byteKey))+">")
            
        self.byteKey = byteKey
        
    def getValue(self, value,argNumber=None):
        value = stringArgChecker.getValue(self, value,argNumber)

        #TODO
        self._raiseArgException("Key store is not yet implemented", argNumber)
        
        return value
        
        
