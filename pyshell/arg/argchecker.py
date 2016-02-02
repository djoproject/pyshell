#!/usr/bin/env python -t
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
    #create an argchecker to check if the value is an instance of
    #create an argchecker to check if the value is a type of
    #and when it will be done, look after listargchecker(defaultargchecker()) and replace them if possible

    #create a checker to instanciate a class instance from a number of parameter

from tries                   import tries
from tries.exception         import ambiguousPathException
import collections # for collections.Hashable
from math                    import log
import os
from threading               import Lock

from pyshell.arg.exception   import *
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME, CONTEXT_ATTRIBUTE_NAME, VARIABLE_ATTRIBUTE_NAME, KEY_ATTRIBUTE_NAME
from pyshell.utils.key       import CryptographicKey

#string argchecker definition
ARGCHECKER_TYPENAME                  = "any"
STRINGCHECKER_TYPENAME               = "string"
INTEGERCHECKER_TYPENAME              = "integer"
LIMITEDINTEGERCHECKER_TYPENAME       = "limited integer"
HEXACHECKER_TYPENAME                 = "hexadecimal"
BINARYCHECKER_TYPENAME               = "binary"
FILEPATHCHECKER_TYPENAME             = "filePath"
LISTCHECKER_TYPENAME                 = "list"
DEFAULTVALUE_TYPENAME                = "default"
ENVIRONMENTDYNAMICCHECKER_TYPENAME   = "environment dynamic"
CONTEXTDYNAMICCHECKER_TYPENAME       = "context dynamic"
VARIABLEDYNAMICCHECKER_TYPENAME      = "variable dynamic"
ENVIRONMENTCHECKER_TYPENAME          = "environment"
CONTEXTCHECKER_TYPENAME              = "context"
VARIABLECHECKER_TYPENAME             = "variable"
PARAMETERDYNAMICCHECKER_TYPENAME     = "parameter dynamic"
PARAMETERCHECKER_TYPENAME            = "parameter"
COMPLETEENVIRONMENTCHECKER_TYPENAME  = "complete Environment"
ENGINECHECKER_TYPENAME               = "engine"
FLOATCHECKER_TYPENAME                = "float"
BOOLEANCHECKER_TYPENAME              = "boolean"
TOKENCHECKER_TYPENAME                = "token"
KEYCHECKER_TYPENAME                  = "key"
KEYTRANSLATORCHECKER_TYPENAME       = "keyTranslator"
KEYTRASNLATORCHECKER_TYPENAME        = "keyTranslator"
KEYTRANSLATORDYNAMICCHECKER_TYPENAME = "keyTranslator dynamic"

class defaultInstanceArgChecker(object):
    _lock = Lock()
    ARGCHECKER           = None
    STRINGARGCHECKER     = None
    INTEGERARGCHECKER    = None
    BOOLEANCHECKER       = None
    FLOATCHECKER         = None
    ENVCHECKER           = None
    KEYCHECKER           = None
    KEYTRANSLATORCHECKER = None
    ENGINECHECKER        = None
    FILECHECKER          = None

    DEFAULTCHECKER_DICO  ={ARGCHECKER_TYPENAME          :None,
                           STRINGCHECKER_TYPENAME       :None,
                           INTEGERCHECKER_TYPENAME      :None,
                           BOOLEANCHECKER_TYPENAME      :None,
                           FLOATCHECKER_TYPENAME        :None,
                           ENVIRONMENTCHECKER_TYPENAME  :None,
                           KEYCHECKER_TYPENAME          :None,
                           ENGINECHECKER_TYPENAME       :None,
                           FILEPATHCHECKER_TYPENAME     :None}

    @staticmethod
    def _getCheckerInstance(key, classdef):
        if defaultInstanceArgChecker.DEFAULTCHECKER_DICO[key] is None:
            with defaultInstanceArgChecker._lock:
                if defaultInstanceArgChecker.DEFAULTCHECKER_DICO[key] is None:
                    defaultInstanceArgChecker.DEFAULTCHECKER_DICO[key] = classdef()
                    defaultInstanceArgChecker.DEFAULTCHECKER_DICO[key].setDefaultValueEnable(False)

        return defaultInstanceArgChecker.DEFAULTCHECKER_DICO[key]

    @staticmethod
    def getArgCheckerInstance():
        return defaultInstanceArgChecker._getCheckerInstance(ARGCHECKER_TYPENAME, ArgChecker)

    @staticmethod
    def getStringArgCheckerInstance():
        return defaultInstanceArgChecker._getCheckerInstance(STRINGCHECKER_TYPENAME, stringArgChecker)

    @staticmethod
    def getIntegerArgCheckerInstance():
        return defaultInstanceArgChecker._getCheckerInstance(INTEGERCHECKER_TYPENAME, IntegerArgChecker)

    @staticmethod
    def getbooleanValueArgCheckerInstance():
        return defaultInstanceArgChecker._getCheckerInstance(BOOLEANCHECKER_TYPENAME, booleanValueArgChecker)

    @staticmethod
    def getFloatTokenArgCheckerInstance():
        return defaultInstanceArgChecker._getCheckerInstance(FLOATCHECKER_TYPENAME, floatTokenArgChecker)

    @staticmethod
    def getCompleteEnvironmentChecker():
        return defaultInstanceArgChecker._getCheckerInstance(ENVIRONMENTCHECKER_TYPENAME, completeEnvironmentChecker)

    @staticmethod
    def getKeyChecker():
        return defaultInstanceArgChecker._getCheckerInstance(KEYCHECKER_TYPENAME, KeyArgChecker)

    @staticmethod
    def getEngineChecker():
        return defaultInstanceArgChecker._getCheckerInstance(ENGINECHECKER_TYPENAME, engineChecker)

    @staticmethod
    def getFileChecker():
        return defaultInstanceArgChecker._getCheckerInstance(FILEPATHCHECKER_TYPENAME, filePathArgChecker)

###############################################################################################
##### ArgChecker ##############################################################################
###############################################################################################

class ArgChecker(object):
    def __init__(self,minimumSize = 1,maximumSize = 1,showInUsage=True, typeName = ARGCHECKER_TYPENAME):
        self.typeName    = typeName
        self.setSize(minimumSize, maximumSize)
        self.defaultValueEnabled = True
        self.hasDefault          = False
        self.default             = None
        self.showInUsage         = showInUsage
        self.engine              = None

    def setSize(self, minimumSize=None, maximumSize=None):
        self.checkSize(minimumSize, maximumSize)
        self.minimumSize         = minimumSize
        self.maximumSize         = maximumSize

    def checkSize(self,minimumSize, maximumSize):
        if minimumSize is not None:
            if type(minimumSize) != int:
                raise argInitializationException("("+self.typeName+") Minimum size must be an integer, got type '"+str(type(minimumSize))+"' with the following value <"+str(minimumSize)+">")

            if minimumSize < 0:
                raise argInitializationException("("+self.typeName+") Minimum size must be a positive value, got <"+str(minimumSize)+">")

        if maximumSize is not None:
            if type(maximumSize) != int:
                raise argInitializationException("("+self.typeName+") Maximum size must be an integer, got type '"+str(type(maximumSize))+"' with the following value <"+str(maximumSize)+">")

            if maximumSize < 0:
                raise argInitializationException("("+self.typeName+") Maximum size must be a positive value, got <"+str(maximumSize)+">")

        if minimumSize is not None and maximumSize is not None and maximumSize < minimumSize:
            raise argInitializationException("("+self.typeName+") Maximum size <"+str(maximumSize)+"> can not be smaller than Minimum size <"+str(minimumSize)+">")

    def isVariableSize(self):
        return (self.minimumSize == self.maximumSize is None) or self.minimumSize != self.maximumSize

    def needData(self):
        return self.minimumSize is not None and self.minimumSize > 0
        #return not (self.minimumSize == self.maximumSize == 0)

    def getValue(self,value,argNumber=None, argNameToBind=None):
        return value

    def getUsage(self):
        return "<any>"

    def getDefaultValue(self, argNameToBind=None):
        if not self.hasDefaultValue(argNameToBind):
            self._raiseArgException("there is no default value")

        return self.default

    def hasDefaultValue(self, argNameToBind=None):
        if not self.defaultValueEnabled:
            return False

        return self.hasDefault

    def setDefaultValue(self,value, argNameToBind=None):
        if not self.defaultValueEnabled:
            raise argInitializationException("("+self.typeName+") default value is not allowed with this kind of checker, probably because it is a default instance checker")

        self.hasDefault = True

        if value is None:
            self.default = None
            return

        self.default = self.getValue(value, None,argNameToBind) #will convert the value if needed

    def setDefaultValueEnable(self, state):
        self.defaultValueEnabled = state

    def erraseDefaultValue(self):
        self.hasDefault = False
        self.default = None

    def setEngine(self, engine):
        self.engine = engine

    def _raiseIfEnvIsNotAvailable(self, argNumber=None, argNameToBind=None):
        if self.engine is None:
            self._raiseArgException("can not get Environment, no engine linked to this argument instance", argNumber, argNameToBind)

        if not hasattr(self.engine,"getEnv"):
            self._raiseArgException("can not get Environment, linked engine does not have a method to get the environment", argNumber, argNameToBind)

        if self.engine.getEnv() is None:
            self._raiseArgException("can not get Environment, no environment linked to the engine", argNumber, argNameToBind)

    def _isEnvAvailable(self):
        return not (self.engine is None or not hasattr(self.engine,"getEnv") or self.engine.getEnv() is None)

    def _raiseArgException(self, message, argNumber=None, argNameToBind=None):
        prefix = ""

        if argNumber is not None:
            prefix += "Token <"+str(argNumber)+">"

        if argNameToBind is not None:
            if len(prefix) > 0:
                prefix += " "

            prefix += "at argument '"+str(argNameToBind)+"'"

        if len(prefix) > 0:
            prefix += ": "

        raise argException("("+self.typeName+") "+ prefix + message)

    def getTypeName(self):
        return self.typeName

class stringArgChecker(ArgChecker):
    def __init__(self, minimumStringSize=0, maximumStringSize = None, typeName = STRINGCHECKER_TYPENAME):
        ArgChecker.__init__(self,1,1,True, typeName)

        if type(minimumStringSize) != int:
            raise argInitializationException("("+self.typeName+") Minimum string size must be an integer, got type '"+str(type(minimumStringSize))+"' with the following value <"+str(minimumStringSize)+">")

        if minimumStringSize < 0:
            raise argInitializationException("("+self.typeName+") Minimum string size must be a positive value bigger or equal to 0, got <"+str(minimumStringSize)+">")

        if maximumStringSize is not None:
            if type(maximumStringSize) != int:
                raise argInitializationException("("+self.typeName+") Maximum string size must be an integer, got type '"+str(type(maximumStringSize))+"' with the following value <"+str(maximumStringSize)+">")

            if maximumStringSize < 1:
                raise argInitializationException("("+self.typeName+") Maximum string size must be a positive value bigger than 0, got <"+str(maximumStringSize)+">")

        if minimumStringSize is not None and maximumStringSize is not None and maximumStringSize < minimumStringSize:
            raise argInitializationException("("+self.typeName+") Maximum string size <"+str(maximumSize)+"> can not be smaller than Minimum string size <"+str(minimumStringSize)+">")

        self.minimumStringSize = minimumStringSize
        self.maximumStringSize = maximumStringSize

    def getValue(self, value,argNumber=None, argNameToBind=None):
        value = ArgChecker.getValue(self, value,argNumber, argNameToBind)

        if value is None:
            self._raiseArgException("the string arg can't be None", argNumber, argNameToBind)

        if type(value) != str and type(value) != unicode:
            if not hasattr(value, "__str__"):
                self._raiseArgException("this value '"+str(value)+"' is not a valid string, got type '"+str(type(value))+"'", argNumber, argNameToBind)

            value = str(value)

        if len(value) < self.minimumStringSize:
            self._raiseArgException("this value '"+str(value)+"' is a too small string, got size '"+str(len(value))+"' with value '"+str(value)+"', minimal allowed size is '"+str(self.minimumStringSize)+"'", argNumber, argNameToBind)

        if self.maximumStringSize is not None and len(value) > self.maximumStringSize:
            self._raiseArgException("this value '"+str(value)+"' is a too big string, got size '"+str(len(value))+"' with value '"+str(value)+"', maximal allowed size is '"+str(self.maximumStringSize)+"'", argNumber, argNameToBind)

        return value

    def getUsage(self):
        return "<string>"

class IntegerArgChecker(ArgChecker):
    def __init__(self, minimum=None, maximum=None,showInUsage=True, typeName=INTEGERCHECKER_TYPENAME):
        ArgChecker.__init__(self,1,1,True,typeName)

        if not hasattr(self, "shortType"):
            self.shortType     = "int"

        if not hasattr(self, "bases"):
            self.bases = [10, 16, 2]

        if minimum is not None and type(minimum) != int and type(minimum) != float:
            raise argInitializationException("("+self.typeName+") Minimum must be an integer or None, got <"+str(type(minimum))+">")

        if maximum is not None and type(maximum) != int and type(maximum) != float:
            raise argInitializationException("("+self.typeName+") Maximum must be an integer or None, got <"+str(type(maximum))+">")

        if minimum is not None and maximum is not None and maximum < minimum:
            raise argInitializationException("("+self.typeName+") Maximum size <"+str(maximum)+"> can not be smaller than Minimum size <"+str(minimum)+">")

        self.minimum = minimum
        self.maximum = maximum

    def getValue(self, value,argNumber=None, argNameToBind=None):
        value = ArgChecker.getValue(self, value,argNumber, argNameToBind)

        if value is None:
            self._raiseArgException("the "+self.typeName.lower()+" arg can't be None", argNumber, argNameToBind)

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

        if castedValue is None:

            if len(self.bases) == 1:
                message = "Only a number in base <"+str(self.bases[0])+"> is allowed"
            else:
                message = "Only a number in bases <"+", ".join(str(x) for x in self.bases)+"> is allowed"

            self._raiseArgException("this arg is not a valid "+self.typeName.lower()+", got <"+str(value)+">. "+message, argNumber, argNameToBind)

        if self.minimum is not None:
            if castedValue < self.minimum:
                self._raiseArgException("the lowest value must be bigger or equal than <"+str(self.minimum) +">, got <"+str(value)+">", argNumber, argNameToBind)

        if self.maximum is not None:
            if castedValue > self.maximum:
                self._raiseArgException("the biggest value must be lower or equal than <"+str(self.maximum)+">, got <"+str(value)+">", argNumber, argNameToBind)

        return castedValue

    def getUsage(self):
        if self.minimum is not None:
            if self.maximum is not None:
                return "<"+self.shortType+" "+str(self.minimum)+"-"+str(self.maximum)+">"
            return "<"+self.shortType+" "+str(self.minimum)+"-*>"
        else:
            if self.maximum is not None:
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
        stringArgChecker.__init__(self,1,None, typename)
        if not isinstance(tokenDict, dict):
            raise argInitializationException("("+self.typeName+") tokenDict must be a dictionary, got '"+str(type(tokenDict))+"'")

        self.localtries = tries()
        for k,v in tokenDict.iteritems():
            #key must be non empty string, value can be anything
            if type(k) != str and type(k) != unicode:
                raise argInitializationException("("+self.typeName+") a key in the dictionary is not a string: '"+str(k)+"', type: '"+str(type(k))+"'")

            self.localtries.insert(k,v)

    def getValue(self, value,argNumber=None, argNameToBind=None):
        value = stringArgChecker.getValue(self, value,argNumber,argNameToBind)

        try:
            node = self.localtries.search(value)
            if node is None:
                self._raiseArgException("this arg '"+str(value)+"' is not an existing token, valid token are ("+ ("|".join(self.localtries.getKeyList())) + ")", argNumber, argNameToBind)
            return node.value

        except ambiguousPathException:
            self._raiseArgException("this arg '"+str(value)+"' is ambiguous, valid token are ("+ ("|".join(self.localtries.getKeyList())) + ")", argNumber, argNameToBind)

    def getUsage(self):
        return "("+ ("|".join(self.localtries.getKeyList())) + ")"

class booleanValueArgChecker(tokenValueArgChecker):
    def __init__(self,TrueName=None,FalseName=None):
        if TrueName is None:
            TrueName = "true"

        if FalseName is None:
            FalseName = "false"

        #the constructor of tokenValueArgChecker will check if every keys are
        tokenValueArgChecker.__init__(self,{TrueName:True,FalseName:False}, BOOLEANCHECKER_TYPENAME)
        self.TrueName = TrueName
        self.FalseName = FalseName

    def getValue(self,value,argNumber=None, argNameToBind=None):
        if type(value) == bool:
            if value:
                value = self.TrueName
            else:
                value = self.FalseName
        else:
            value = str(value).lower()

        return tokenValueArgChecker.getValue(self,value,argNumber,argNameToBind)

class floatTokenArgChecker(ArgChecker):
    def __init__(self, minimum=None, maximum=None):
        ArgChecker.__init__(self,1,1,True, FLOATCHECKER_TYPENAME)

        if minimum is not None and type(minimum) != float and type(minimum) != int:
            raise argInitializationException("("+self.typeName+") Minimum must be a float or None, got '"+str(type(minimum))+"'")

        if maximum is not None and type(maximum) != float and type(maximum) != int:
            raise argInitializationException("("+self.typeName+") Maximum must be a float or None, got '"+str(type(maximum))+"'")

        if minimum is not None and maximum is not None and maximum < minimum:
            raise argInitializationException("("+self.typeName+") Maximum <"+str(maximum)+"> can not be smaller than Minimum <"+str(minimum)+">")

        self.minimum = minimum
        self.maximum = maximum

    def getValue(self, value,argNumber=None, argNameToBind=None):
        value = ArgChecker.getValue(self, value,argNumber, argNameToBind)

        if value is None:
            self._raiseArgException("the float arg can't be None", argNumber, argNameToBind)

        try:
            castedValue = float(value)
        except ValueError:
            self._raiseArgException("this arg is not a valid float or hexadecimal, got <"+str(value)+">", argNumber, argNameToBind)

        if self.minimum is not None:
            if castedValue < self.minimum:
                self._raiseArgException("the lowest value must be bigger or equal than <"+str(self.minimum) + ">, got <"+str(value)+">", argNumber, argNameToBind)

        if self.maximum is not None:
            if castedValue > self.maximum:
                self._raiseArgException("the biggest value must be lower or equal than <"+str(self.maximum)+ ">, got <"+str(value)+">", argNumber, argNameToBind)

        return castedValue

    def getUsage(self):
        if self.minimum is not None:
            if self.maximum is not None:
                return "<float "+str(self.minimum)+"-"+str(self.maximum)+">"
            return "<float "+str(self.minimum)+"-*.*>"
        else:
            if self.maximum is not None:
                return "<float *.*-"+str(self.maximum)+">"
        return "<float>"

class engineChecker(ArgChecker):
    def __init__(self):
        ArgChecker.__init__(self,0,0,False, ENGINECHECKER_TYPENAME)

    def getValue(self,value,argNumber=None, argNameToBind=None):
        return self.engine

    def usage(self):
        return ""

    def getDefaultValue(self, argNameToBind=None):
        return self.engine

    def hasDefaultValue(self, argNameToBind=None):
        return True

    def setDefaultValue(self,value, argNameToBind=None):
        pass

    def erraseDefaultValue(self):
        pass

class completeEnvironmentChecker(ArgChecker):
    def __init__(self):
        ArgChecker.__init__(self,0,0,False, COMPLETEENVIRONMENTCHECKER_TYPENAME)

    def getValue(self,value,argNumber=None, argNameToBind=None):
        self._raiseIfEnvIsNotAvailable(argNumber, argNameToBind)
        return self.engine.getEnv()

    def usage(self):
        return ""

    def getDefaultValue(self, argNameToBind=None):
        self._raiseIfEnvIsNotAvailable(None, argNameToBind)
        return self.engine.getEnv()

    def hasDefaultValue(self, argNameToBind=None):
        return self._isEnvAvailable()#n not isinstance(self.engine.getEnv(), ParameterManager)

    def setDefaultValue(self,value, argNameToBind=None):
        pass

    def erraseDefaultValue(self):
        pass

#TODO this checker should not be use anywhere, use contextParameterChecker or environmentParameterChecker
class abstractParameterChecker(ArgChecker):
    def __init__(self,keyname, containerAttribute, typeName = PARAMETERCHECKER_TYPENAME):
        ArgChecker.__init__(self,0,0,False, typeName)

        if keyname is None or (type(keyname) != str and type(keyname) != unicode) or not isinstance(keyname, collections.Hashable):
            raise argInitializationException("("+self.typeName+") keyname must be hashable string, got '"+str(keyname)+"'")

        self.keyname = keyname

        if containerAttribute is None or (  (type(containerAttribute) != str and type(containerAttribute) != unicode) ):
            raise argInitializationException("("+self.typeName+") containerAttribute must be a valid string, got '"+str(type(containerAttribute))+"'")

        self.containerAttribute = containerAttribute

    def _getContainer(self,argNumber=None, argNameToBind=None):
        self._raiseIfEnvIsNotAvailable(argNumber, argNameToBind)
        env = self.engine.getEnv()

        if not hasattr(env, self.containerAttribute):
            self._raiseArgException("environment container does not have the attribute '"+str(self.containerAttribute)+"'", argNumber, argNameToBind)

        return getattr(env, self.containerAttribute)

    def getValue(self,value,argNumber=None, argNameToBind=None):
        container = self._getContainer(argNumber, argNameToBind)

        param = container.getParameter(self.keyname)
        if param is None:
            self._raiseArgException("the key '"+self.keyname+"' is not available but needed", argNumber, argNameToBind)

        return param

    def usage(self):
        return ""

    #TODO est ce qu'il existe vraiment un cas de figure ou les valeurs par defaut peuvent être appellée avec un argument de taille min=0, max=0 ?
    def getDefaultValue(self, argNameToBind=None):
        container = self._getContainer(None, argNameToBind)

        param = container.getParameter(self.keyname)
        if param is None:
            self._raiseArgException("the key '"+self.keyname+"' is not available but needed", None, argNameToBind)

        return param

    def hasDefaultValue(self, argNameToBind=None):
        container = self._getContainer(None, argNameToBind)
        return container.hasParameter(self.keyname)

    def setDefaultValue(self,value, argNameToBind=None):
        pass

    def erraseDefaultValue(self):
        pass

class abstractParameterDynamicChecker(ArgChecker):
    def __init__(self, containerAttribute, typeName = PARAMETERDYNAMICCHECKER_TYPENAME):
        ArgChecker.__init__(self,1,1,False, typeName)

        if containerAttribute is None or (  (type(containerAttribute) != str and type(containerAttribute) != unicode) ):
            raise argInitializationException("("+self.typeName+") containerAttribute must be a valid string, got '"+str(type(containerAttribute))+"'")

        self.containerAttribute = containerAttribute

    def getValue(self,value,argNumber=None, argNameToBind=None):
        self._raiseIfEnvIsNotAvailable(argNumber, argNameToBind)
        if not isinstance(value, collections.Hashable):
            self._raiseArgException("keyname must be hashable, got '"+str(value)+"'", argNumber, argNameToBind)

        env = self.engine.getEnv()

        if not hasattr(env, self.containerAttribute):
            self._raiseArgException("environment container does not have the attribute '"+str(self.containerAttribute)+"'", argNumber, argNameToBind)

        container = getattr(env, self.containerAttribute)

        param = container.getParameter(value)
        if param is None:
            self._raiseArgException("the key '"+str(value)+"' is not available but needed", argNumber, argNameToBind)

        return param

    def hasDefaultValue(self, argNameToBind=None):
        return False

    def setDefaultValue(self,value, argNameToBind=None):
        pass

    def erraseDefaultValue(self):
        pass

#TODO use constant name

class contextParameterChecker(abstractParameterChecker):
    def __init__(self, contextStringPath):
        abstractParameterChecker.__init__(self, contextStringPath, CONTEXT_ATTRIBUTE_NAME, CONTEXTCHECKER_TYPENAME)

class environmentParameterChecker(abstractParameterChecker):
    def __init__(self, environmentStringPath):
        abstractParameterChecker.__init__(self, environmentStringPath, ENVIRONMENT_ATTRIBUTE_NAME, ENVIRONMENTCHECKER_TYPENAME)

class variableParameterChecker(abstractParameterChecker):
    def __init__(self, environmentStringPath):
        abstractParameterChecker.__init__(self, environmentStringPath, VARIABLE_ATTRIBUTE_NAME, VARIABLECHECKER_TYPENAME)

class contextParameterDynamicChecker(abstractParameterDynamicChecker):
    def __init__(self):
        abstractParameterDynamicChecker.__init__(self, CONTEXT_ATTRIBUTE_NAME, CONTEXTDYNAMICCHECKER_TYPENAME)

class environmentParameterDynamicChecker(abstractParameterDynamicChecker):
    def __init__(self):
        abstractParameterDynamicChecker.__init__(self, ENVIRONMENT_ATTRIBUTE_NAME, ENVIRONMENTDYNAMICCHECKER_TYPENAME)

class variableParameterDynamicChecker(abstractParameterDynamicChecker):
    def __init__(self):
        abstractParameterDynamicChecker.__init__(self, VARIABLE_ATTRIBUTE_NAME, VARIABLEDYNAMICCHECKER_TYPENAME)

class defaultValueChecker(ArgChecker):
    def __init__(self,value):
        ArgChecker.__init__(self,0,0,False, DEFAULTVALUE_TYPENAME)
        self.setDefaultValue(value)

    def setDefaultValue(self,value, argNameToBind=None):
        self.hasDefault = True
        self.default = value #no check on the value...

    def getValue(self,value,argNumber=None, argNameToBind=None):
        return self.getDefaultValue(argNameToBind)

class listArgChecker(ArgChecker):
    def __init__(self,checker,minimumSize=None,maximumSize=None):
        if not isinstance(checker, ArgChecker) or isinstance(checker, listArgChecker):
            raise argInitializationException("("+LISTCHECKER_TYPENAME+") checker must be an instance of ArgChecker but can not be an instance of listArgChecker, got '"+str(type(checker))+"'")

        #checker must have a fixed size
        if checker.minimumSize != checker.maximumSize or checker.minimumSize is None or checker.minimumSize == 0:
            if checker.minimumSize is None:
                checkerSize = "]-Inf,"
            else:
                checkerSize = "["+str(checker.minimumSize)+","

            if checker.maximumSize is None:
                checkerSize += "+Inf["
            else:
                checkerSize += str(checker.maximumSize)+"]"

            raise argInitializationException("("+LISTCHECKER_TYPENAME+") checker must have a fixed size bigger than zero, got this sizer : "+checkerSize)

        self.checker = checker
        ArgChecker.__init__(self,minimumSize,maximumSize, True, LISTCHECKER_TYPENAME)

    def checkSize(self,minimumSize, maximumSize):
        ArgChecker.checkSize(self,minimumSize, maximumSize)

        if minimumSize is not None and (minimumSize % self.checker.minimumSize)  != 0:
            raise argInitializationException("("+LISTCHECKER_TYPENAME+") the minimum size of the list <"+str(minimumSize)+"> is not a multiple of the checker size <"+str(self.checker.minimumSize)+">")

        if maximumSize is not None and (maximumSize % self.checker.minimumSize)  != 0:
            raise argInitializationException("("+LISTCHECKER_TYPENAME+") the maximum size of the list <"+str(maximumSize)+"> is not a multiple of the checker size <"+str(self.checker.minimumSize)+">")

    def getValue(self,values,argNumber=None, argNameToBind=None):
        #check if it's a list
        if not hasattr(values, "__iter__"):#if not isinstance(values,list):
            values = (values,)
            #self._raiseArgException("this arg is not a valid list, not iterable",argNumber, argNameToBind)

        #len(values) must always be a multiple of self.checker.minimumSize
            #even if there is to much data, it is a sign of anomalies
        if (len(values) % self.checker.minimumSize)  != 0:
            self._raiseArgException("the size of the value list <"+str(len(values))+"> is not a multiple of the checker size <"+str(self.checker.minimumSize)+">",argNumber, argNameToBind)

        #check the minimal size
        addAtEnd = []
        if self.minimumSize is not None and len(values) < self.minimumSize:
            #checker has default value ?
            if self.checker.hasDefaultValue(argNameToBind):
                #build the missing part with the default value
                addAtEnd = ((self.minimumSize - len(values)) / self.checker.minimumSize) * [self.checker.getDefaultValue(argNameToBind)]
            else:
                self._raiseArgException("need at least "+str(self.minimumSize))+" items, got "+str(len(values),argNumber, argNameToBind)

        #build range limite and manage max size
        if self.maximumSize is not None:
            if len(values) < self.maximumSize:
                msize = len(values)
            else:
                msize = self.maximumSize
        else:
            msize = len(values)

        #check every args
        ret = []
        if argNumber is not None:
            for i in range(0,msize, self.checker.minimumSize):
                if self.checker.minimumSize == 1:
                    ret.append(self.checker.getValue(values[i],argNumber, argNameToBind))
                else:
                    ret.append(self.checker.getValue(values[i:i+self.checker.minimumSize],argNumber, argNameToBind))

                argNumber += 1
        else:
            for i in range(0,msize, self.checker.minimumSize):
                if self.checker.minimumSize == 1:
                    ret.append(self.checker.getValue(values[i], None, argNameToBind))
                else:
                    ret.append(self.checker.getValue(values[i:i+self.checker.minimumSize], None, argNameToBind))

        #add the missing part
        ret.extend(addAtEnd)
        return ret

    def getDefaultValue(self,argNameToBind=None):
        if self.hasDefault:
            return self.default

        if self.minimumSize is None:
            return []

        if self.checker.hasDefaultValue(argNameToBind):
            return [self.checker.getDefaultValue(argNameToBind)] * self.minimumSize

        self._raiseArgException("getDefaultValue, there is no default value", None, argNameToBind)

    def hasDefaultValue(self,argNameToBind=None):
        return self.hasDefault or self.minimumSize is None or self.checker.hasDefaultValue(argNameToBind)

    def getUsage(self):
        if self.minimumSize is None :
            if self.maximumSize is None :
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

            if self.maximumSize is None :
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

    def setEngine(self, engine):
        ArgChecker.setEngine(self, engine)
        self.checker.setEngine(engine)

class filePathArgChecker(stringArgChecker):
    #just check a path, no operation are executed here, it is the job of the addon to perform change

    def __init__(self, exist=None, readable=None, writtable=None, isFile=None):
        stringArgChecker.__init__(self, 1,None, FILEPATHCHECKER_TYPENAME)

        if exist is not None and type(exist) != bool:
            raise argInitializationException("("+self.typeName+") exist must be None or a boolean, got '"+str(type(exist))+"'")

        if readable is not None and type(readable) != bool:
            raise argInitializationException("("+self.typeName+") readable must be None or a boolean, got '"+str(type(readable))+"'")

        if writtable is not None and type(writtable) != bool:
            raise argInitializationException("("+self.typeName+") writtable must be None or a boolean, got '"+str(type(writtable))+"'")

        if isFile is not None and type(isFile) != bool:
            raise argInitializationException("("+self.typeName+") isFile must be None or a boolean, got '"+str(type(isFile))+"'")

        self.exist     = exist
        self.readable  = readable
        self.writtable = writtable
        self.isFile    = isFile

    def getValue(self, value,argNumber=None, argNameToBind=None):
        path = stringArgChecker.getValue(self, value,argNumber, argNameToBind)

        #prepare path
        path = os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

        fileExist = None

        #exist
        if self.exist is not None:
            fileExist = os.access(path, os.F_OK)

            if self.exist and not fileExist:
                self._raiseArgException("Path '"+str(path)+"' does not exist and must exist",argNumber, argNameToBind)

            if not self.exist and fileExist:
                self._raiseArgException("Path '"+str(path)+"' exists and must not exist",argNumber, argNameToBind)

        #isFile
        if self.isFile is not None:
            if fileExist is None:
                fileExist = os.access(path, os.F_OK)

            if fileExist:
                isFile = os.path.isfile(path)

                if self.isFile and not isFile:
                    self._raiseArgException("Path '"+str(path)+"' is a directory and must be a file",argNumber, argNameToBind)

                if not self.isFile and isFile:
                    self._raiseArgException("Path '"+str(path)+"' is a file and must be a directory",argNumber, argNameToBind)
            #else: #if not exist, do not care, no way to know if it is a file or a directory

        #readable
        if self.readable is not None:
            if fileExist is None:
                fileExist = os.access(path, os.F_OK)

            if not fileExist:
                if self.exist is not None and self.exist:
                    self._raiseArgException("Path '"+str(path)+"' does not exist and so it is not readable",argNumber, argNameToBind)

            else:
                readable = os.access(path, os.R_OK)

                if self.readable and not readable:
                    self._raiseArgException("Path '"+str(path)+"' is not readable and must be readable",argNumber, argNameToBind)

                if not self.readable and readable:
                    self._raiseArgException("Path '"+str(path)+"' is readable and must not be readable",argNumber, argNameToBind)

        #writtable
        if self.writtable is not None:
            if fileExist is None:
                fileExist = os.access(path, os.F_OK)

            if not fileExist:
                #first existing parent must be writtable
                curentPath = path
                parentPath = os.path.abspath(os.path.join(curentPath, os.pardir))
                while not os.path.samefile(parentPath, curentPath): #until we reach the root
                    #this parent exists ?
                    if os.access(parentPath, os.F_OK):
                        #do we have write access on it ?
                        if not os.access(parentPath, os.W_OK):
                            #no writing access to the first existing directory, go to else clause of the loop
                            curentPath = parentPath
                            continue

                        #we have writing access, break the boucle
                        break

                    #go to a upper parent
                    curentPath = parentPath
                    parentPath = os.path.abspath(os.path.join(curentPath, os.pardir))
                else:
                    self._raiseArgException("Path '"+str(path)+"' does not exist and the first existing parent directory '"+str(parentPath)+"' is not writtable",argNumber, argNameToBind)

            else:
                writtable = os.access(path, os.W_OK)#return False if path does not exist...

                if self.writtable and not writtable:
                    self._raiseArgException("Path '"+str(path)+"' is not writtable and must be writtable",argNumber, argNameToBind)

                if not self.writtable and writtable:
                    self._raiseArgException("Path '"+str(path)+"' is writtable and must not be writtable",argNumber, argNameToBind)

        #don't open a file, because not sure the addon will close it...
        return value

    def getUsage(self):
        return "<file_path>"

class abstractKeyStoreTranslatorArgChecker(stringArgChecker):
    "retrieve a key from the keystore"

    def __init__(self, keySize = None, byteKey=True, allowdifferentKeySize = False):
        stringArgChecker.__init__(self, 1,None, KEYTRANSLATORCHECKER_TYPENAME)

        if keySize is not None:
            if type(keySize) != int:
                raise argInitializationException("("+self.typeName+") keySize must be an integer, got '"+str(type(keySize))+"'")

            if type(keySize) < 0:
                raise argInitializationException("("+self.typeName+") keySize must be bigger than 0, got <"+str(tkeySize)+">")

        if allowdifferentKeySize is None or type(allowdifferentKeySize) != bool:
            raise argInitializationException("("+self.typeName+") allowdifferentKeySize must be a boolean, got '"+str(type(allowdifferentKeySize))+"'")

        if byteKey is None or type(byteKey) != bool:
            raise argInitializationException("("+self.typeName+") byteKey must be a boolean, got '"+str(type(byteKey))+"'")

        self.allowdifferentKeySize = allowdifferentKeySize
        self.keySize               = keySize
        self.byteKey               = byteKey

    def getValue(self, value,argNumber=None, argNameToBind=None):
        keyInstance = value

        #check type
        if self.byteKey is not None:
            if self.byteKey and keyInstance.getKeyType() !=  Key.KEYTYPE_HEXA:
                self._raiseArgException("the key '"+str(value)+"' is a bit key and the process need a byte key", argNumber, argNameToBind)

            if not self.byteKey and keyInstance.getKeyType() !=  Key.KEYTYPE_BIT:
                self._raiseArgException("the key '"+str(value)+"' is a byte key and the process need a bit key", argNumber, argNameToBind)

        #check size
        if self.keySize is not None and not self.allowdifferentKeySize and keyInstance.getKeySize() < self.keySize:
            if Key.KEYTYPE_HEXA == keyInstance.getKeyType():
                keytype = "byte(s)"
            else:
                keytype = "bit(s)"

            self._raiseArgException("too short key '"+str(value)+"', need a key of at least <"+str(self.keySize)+" "+keytype+", got a <"+str(keyInstance.getKeySize())+"> "+keytype+" key", argNumber, argNameToBind)

        return keyInstance

    def getUsage(self):
        return "<key name>"

class KeyParameterChecker(abstractParameterChecker, abstractKeyStoreTranslatorArgChecker):
    def __init__(self, environmentStringPath, keySize = None, byteKey=True, allowdifferentKeySize = False):
        abstractParameterChecker.__init__(self, environmentStringPath, KEY_ATTRIBUTE_NAME, KEYTRASNLATORCHECKER_TYPENAME)
        abstractKeyStoreTranslatorArgChecker.__init__(self,keySize, byteKey, allowdifferentKeySize)

    def getValue(self, value,argNumber=None, argNameToBind=None):
        parameter = abstractParameterChecker.getValue(value, argNumber, argNameToBind)
        return abstractKeyStoreTranslatorArgChecker.getValue(parameter.getValue())

class KeyParameterDynamicChecker(abstractParameterDynamicChecker, abstractKeyStoreTranslatorArgChecker):
    def __init__(self, keySize = None, byteKey=True, allowdifferentKeySize = False):
        abstractParameterDynamicChecker.__init__(self, KEY_ATTRIBUTE_NAME, KEYTRANSLATORDYNAMICCHECKER_TYPENAME)
        abstractKeyStoreTranslatorArgChecker.__init__(self,keySize, byteKey, allowdifferentKeySize)

    def getValue(self, value,argNumber=None, argNameToBind=None):
        parameter = abstractParameterChecker.getValue(value, argNumber, argNameToBind)
        return abstractKeyStoreTranslatorArgChecker.getValue(parameter.getValue())

class KeyArgChecker(IntegerArgChecker):
    "create a key from the input"
    def __init__(self):
        self.bases = [2,16]
        self.shortType     = "key"
        IntegerArgChecker.__init__(self, 0,None, True, KEYCHECKER_TYPENAME)

    def getValue(self, value,argNumber=None, argNameToBind=None):
        intvalue = IntegerArgChecker.getValue(self, value,argNumber, argNameToBind)

        try:
            return CryptographicKey(value)
        except Exception as e:
            self._raiseArgException("Fail to resolve key: "+str(e), argNumber, argNameToBind)

    def getUsage(self):
        return "<key>"


