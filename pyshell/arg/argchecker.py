#!/usr/bin/python
# -*- coding: utf-8 -*-

from exception import *
from pyshell.utils.ordereddict import OrderedDict
from tries import tries
from tries.exception import ambiguousPathException
import collections # for collections.Hashable
from math import log

###############################################################################################
##### ArgsChecker #############################################################################
###############################################################################################
class ArgsChecker():
    "abstract arg checker"

    #
    # @argsList, une liste de string
    # @return, un dico trie des arguments et de leur valeur : <name,value>
    # 
    def checkArgs(self,argsList):
        pass #XXX to override
        
    def usage(self):
        pass #XXX to override

class ArgFeeder2(ArgsChecker):

    #
    # @param argTypeList, une liste de tuple (Argname,ArgChecker) 
    #
    def __init__(self,argTypeList=None):
        if argTypeList == None:
            self.argTypeList = []
        else:
            self.argTypeList = argTypeList
        
    #
    # @argsList, une liste de string
    # @return, un dico trie des arguments et de leur valeur : <name,value>
    # 
    def checkArgs(self,argsList):
        #print argsList
        ret = OrderedDict()

        argCheckerIndex = 0
        dataIndex = 0
        for (name,checker) in self.argTypeList:
            
            #is there a minimum limit
            if checker.minimumSize != None:
                #is there at least minimumSize item in the data stream?
                if len(argsList[dataIndex:]) < checker.minimumSize:
                    #end of stream ?
                    if len(argsList[dataIndex:]) == 0:
                        #we will check if there is some default value
                        break 
                    else:
                        #there are data but not enough
                        raise argException("(ArgFeeder) not enough data for the argument <"+name+">")
            
            #is there a maximum limit?
            if checker.maximumSize == None:
                #No max limit, it consume all remaining data
                ret[name] = checker.getValue(argsList[dataIndex:],dataIndex)
                dataIndex = len(argsList)
            else:
                #checker only need one item?
                if checker.minimumSize != None and checker.minimumSize == checker.maximumSize == 1:
                    value = argsList[dataIndex:(dataIndex+checker.maximumSize)][0]
                else:
                    value = argsList[dataIndex:(dataIndex+checker.maximumSize)]
                    
                ret[name] = checker.getValue(value,dataIndex)
                dataIndex += checker.maximumSize
                    
            argCheckerIndex += 1
        
        
        # MORE THAN THE LAST ARG CHECKER HAVEN'T BEEN CONSUMED YET
        for i in range(argCheckerIndex,len(self.argTypeList)):
            (name,checker) = self.argTypeList[i]
                
            if checker.hasDefaultValue():
                ret[name] = checker.getDefaultValue()
            else:
                raise argException("(ArgFeeder) some arguments aren't bounded, missing data : <"+name+">")

        return ret
        
    def usage(self):
        if len(self.argTypeList) == 0:
            return "no args needed"
    
        ret = ""
        firstMandatory = False
        for (name,checker) in self.argTypeList:
            if not checker.showInUsage:
                continue
        
            if checker.hasDefaultValue() and not firstMandatory:
                ret += "["
                firstMandatory = True
            
            ret += name+":"+checker.getUsage()+" "
            
        if firstMandatory:
            ret += "]"
        
        return ret
        
###############################################################################################
##### ArgChecker ##############################################################################
###############################################################################################

#TODO
    #-en cas de conversion de la valeur, celle-ci a lieu deux fois
        #une fois dans le check et une fois dans le get
        #c'est deux fois la meme operation :/
        #pas moyen d'eviter ça ?

class ArgChecker(object):
    def __init__(self,minimumSize = 1,maximumSize = 1,showInUsage=True):
        if type(minimumSize) != int:
            raise argInitializationException("(ArgChecker) Minimum size must be an integer")
            
        if type(maximumSize) != int:
            raise argInitializationException("(ArgChecker) Maximum size must be an integer") 
        
        if minimumSize < 0:
            raise argInitializationException("(ArgChecker) Minimum size must be a positive value")
        
        if maximumSize < 0:
            raise argInitializationException("(ArgChecker) Maximum size must be a positive value") 
    
        if maximumSize < minimumSize:
            raise argInitializationException("(ArgChecker) Maximum size can not be smaller than Minimum size") 
    
        self.minimumSize = minimumSize
        self.maximumSize = maximumSize
        self.hasDefault = False
        self.default = None
        self.showInUsage = showInUsage
    
    def isVariableSize(self):
        return (self.minimumSize == self.maximumSize == None) or self.minimumSize != self.maximumSize
    
    def needData(self):
        return not (self.minimumSize == self.maximumSize == 0)
    
    #
    # @exception raise an argException if there is an error
    #   
    def checkValue(self,argNumber=None):
        pass #XXX to override
        
    def getValue(self,value,argNumber=None):
        self.checkValue(value)
        return value
        
    def getUsage(self):
        return "<any>"
        
    def getDefaultValue(self):
        if not self.hasDefaultValue():
            raise argException("(ArgChecker) there is no default value")
    
        return self.default
        
    def hasDefaultValue(self):
        return self.hasDefault
        
    def setDefaultValue(self,value):
        self.hasDefault = True
        self.default = value
        
    def erraseDefaultValue(self):
        self.hasDefault = False
        self.default = None
        
class stringArgChecker(ArgChecker):
    def checkValue(self, value,argNumber=None):
        if value == None:
            raise argException("(String) Argument %s: the string arg can't be None"%("" if argNumber == None else str(argNumber)+" "))

        if type(value) != str and type(value) != unicode:
            raise argException("(String) Argument %s: this value <"%("" if argNumber == None else str(argNumber)+" ")+str(value)+"> is not a valid string")
    
    """def getValue(self,value,argNumber=None):
        self.checkValue(value,argNumber)
        v = super(stringArgChecker,self).getValue(value,argNumber)

        if v != None:
            return v
        return None """
    
    def getUsage(self):
        return "<string>"

class IntegerArgChecker(ArgChecker):
    def __init__(self, minimum=None, maximum=None):
        ArgChecker.__init__(self)
        
        if not hasattr(self, "completeType"):
            self.completeType  = "Integer"
        
        if not hasattr(self, "shortType"):
            self.shortType     = "int"
        
        if not hasattr(self, "bases"):
            self.bases = [10, 16, 2]
        
        if minimum != None and type(minimum) != int and type(minimum) != float:
            raise argInitializationException("("+self.completeType+") Minimum must be an integer or None")
            
        if maximum != None and type(maximum) != int and type(maximum) != float:
            raise argInitializationException("("+self.completeType+") Maximum must be an integer or None")
            
        if minimum != None and maximum != None and maximum < minimum:
            raise argInitializationException("("+self.completeType+") Maximum can not be smaller than Minimum")
        
        self.minimum = minimum
        self.maximum = maximum

    def checkValue(self, value,argNumber=None):
        if value == None:
            raise argException("("+self.completeType+") Argument %s: the "%("" if argNumber == None else str(argNumber)+" ")+self.completeType.lower()+" arg can't be None")
        
        castedValue = None
        if type(value) == int or type(value) == float or type(value) == bool:
            castedValue = int(value)
        elif type(value) == str or type(value) == unicode:
            for b in self.bases:
                try:
                    castedValue = int(value, b)
                    break
                except ValueError:
                    continue
                    
        if castedValue == None:
            raise argException("("+self.completeType+") Argument %s: this arg is not a valid "%("" if argNumber == None else str(argNumber))+self.completeType.lower()+" or hexadecimal")

        if self.minimum != None:
            if castedValue < self.minimum:
                raise argException("("+self.completeType+") Argument %s: the lowest value must be bigger or equal than "%("" if argNumber == None else str(argNumber)+str(self.minimum)))
                
        if self.maximum != None:
            if castedValue > self.maximum:
                raise argException("("+self.completeType+") Argument %s: the biggest value must be lower or equal than "%("" if argNumber == None else str(argNumber)+str(self.maximum)))


    def getValue(self,value,argNumber=None):
        self.checkValue(value,argNumber)
        v = super(IntegerArgChecker,self).getValue(value,argNumber)
        
        if type(value) == int or type(value) == float or type(value) == bool:
            return int(value)
        elif type(value) == str or type(value) == unicode:
            for b in self.bases:
                try:
                    return int(value, b)
                except ValueError:
                    continue       
        
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
            raise argInitializationException("(Limited integer) the amount of bit must at least be 8, got <"+str(amountOfBit)+">")
    
        if log(amountOfBit, 2)%1 != 0:
            raise argInitializationException("(Limited integer) only powers of 2 are allowed, 8, 16, 32, 64, ..., got <"+str(amountOfBit)+">")

        if signed:
            IntegerArgChecker.__init__(self, -(2**(amountOfBit-1)), (2**(amountOfBit-1))-1)
        else:
            IntegerArgChecker.__init__(self, 0x0, (2**amountOfBit) -1)

class hexaArgChecker(IntegerArgChecker):
    def __init__(self, minimum=None, maximum=None):
        self.bases = [16]
        self.completeType  = "Hexadecimal"
        self.shortType     = "hex"
        IntegerArgChecker.__init__(self, minimum,maximum)
        
class binaryArgChecker(IntegerArgChecker):
    def __init__(self, minimum=None, maximum=None):
        self.bases = [2]
        self.completeType  = "Binary"
        self.shortType     = "bin"
        IntegerArgChecker.__init__(self, minimum,maximum)

class tokenValueArgChecker(stringArgChecker):
    def __init__(self, tokenDict):
        super(tokenValueArgChecker,self).__init__()
        if not isinstance(tokenDict, dict):
            raise argInitializationException("(Token) tokenDict must be a dictionary")
        
        self.localtries = tries()
        for k,v in tokenDict.iteritems():
            #key must be non empty string, value can be anything
            if type(k) != str and type(k) != unicode:
                raise argInitializationException("(Token) a key in the dictionary is not a string: <"+str(k)+">")

            self.localtries.insert(k,v)
    
    def checkValue(self, value,argNumber=None):
        super(tokenValueArgChecker,self).checkValue(value,argNumber)
        
        #must be a string
        if type(value) != str and type(value) != unicode:
            raise argException("(Token) Argument %s: this value <"%("" if argNumber == None else str(argNumber)+" ")+str(value)+"> is not a valid string")
        
        try:
            if self.localtries.search(value) == None:
                raise argException("(Token) Argument %s: this arg is not an existing token"%("" if argNumber == None else str(argNumber)+" ")+", valid token are ("+ ("|".join(self.localtries.getKeyList())) + ")")
        except ambiguousPathException:
            raise argException("(Token) Argument %s: this arg is ambiguous"%("" if argNumber == None else str(argNumber)+" ")+", valid token are ("+ ("|".join(self.localtries.getKeyList())) + ")")
           
    def getValue(self,value,argNumber=None):
        self.checkValue(value,argNumber)
        
        return self.localtries.search(value).value
        
    def getUsage(self):
        return "("+ ("|".join(self.localtries.getKeyList())) + ")"

class booleanValueArgChecker(tokenValueArgChecker):
    def __init__(self,TrueName=None,FalseName=None):
        if TrueName == None:
            TrueName = "true"
            
        if FalseName == None:
            FalseName = "false"
    
        #the constructor of tokenValueArgChecker will check if every keys are 
        tokenValueArgChecker.__init__(self,{TrueName:True,FalseName:False})
        self.TrueName = TrueName
        self.FalseName = FalseName
    
    def checkValue(self, value,argNumber=None):
        if type(value) == bool:
            return
            
        tokenValueArgChecker.checkValue(self, value,argNumber)
        
    def getValue(self,value,argNumber=None):
        if type(value) == bool:
            if value:
                value = self.TrueName
            else:
                value = self.FalseName
        
        return tokenValueArgChecker.getValue(self,value,argNumber)
    
    
class floatTokenArgChecker(ArgChecker):
    def __init__(self, minimum=None, maximum=None):
        if minimum != None and type(minimum) != float and type(minimum) != int:
            raise argInitializationException("(Float) Minimum must be a float or None")
            
        if maximum != None and type(maximum) != float and type(maximum) != int:
            raise argInitializationException("(Float) Maximum must be a float or None")
            
        if minimum != None and maximum != None and maximum < minimum:
            raise argInitializationException("(Float) Maximum can not be smaller than Minimum")
    
        ArgChecker.__init__(self)
        self.minimum = minimum
        self.maximum = maximum
    
    def checkValue(self, value,argNumber=None):
        if value == None:
            raise argException("(Float) Argument %s: the float arg can't be None"%("" if argNumber == None else str(argNumber)+" "))
        
        try:
            castedValue = float(value)
        except ValueError:
            raise argException("(Float) Argument %s: this arg is not a valid float or hexadecimal"%("" if argNumber == None else str(argNumber)+" "))
                
        if self.minimum != None:
            if castedValue < self.minimum:
                raise argException("(Float) Argument %s: the lowest value must be bigger or equal than "%("" if argNumber == None else str(argNumber)+" ")+str(self.minimum))
                
        if self.maximum != None:
            if castedValue > self.maximum:
                raise argException("(Float) Argument %s: the biggest value must be lower or equal than "%("" if argNumber == None else str(argNumber)+" ")+str(self.maximum))

    def getValue(self,value,argNumber=None):
        self.checkValue(value,argNumber)
        return float(super(floatTokenArgChecker,self).getValue(value,argNumber))     
        
    def getUsage(self):
        if self.minimum != None:
            if self.maximum != None:
                return "<float "+str(self.minimum)+"-"+str(self.maximum)+">"
            return "<float "+str(self.minimum)+"-*.*>"
        else:
            if self.maximum != None:
                return "<float *.*-"+str(self.maximum)+">"
        return "<float>"

class environmentChecker(ArgChecker):
    def __init__(self,keyname,environment):
        if not isinstance(environment, dict):
            raise argInitializationException("(Environment) environment must be a dictionary")
    
        if not isinstance(keyname, collections.Hashable):
            raise argInitializationException("(Environment) keyname must be hashable")
    
        #the key is not checked at the instanciation because maybe it does not yet exist
    
        ArgChecker.__init__(self,0,0,False)
        self.environment = environment
        self.keyname = keyname
    
    def getValue(self,value,argNumber=None):
        if self.keyname not in self.environment:
            raise argException("(Environment) environment %s: the key <"%("" if argNumber == None else str(argNumber)+" ")+self.keyname+"> is not available but needed")
    
        return self.environment[self.keyname]
        
    def usage(self):
        return ""
        
    def getDefaultValue(self):
        return self.environment[self.keyname]
        
    def hasDefaultValue(self):
        return self.keyname not in self.environment
        
    def setDefaultValue(self,value):
        pass
        
    def erraseDefaultValue(self):
        pass

class environmentDynamicChecker(ArgChecker):
    def __init__(self,environment):
        if not isinstance(environment, dict):
            raise argInitializationException("(EnvironmentDynamic) environment must be a dictionary")
    
        self.environment = environment
        ArgChecker.__init__(self,1,1,False)
    
    def getValue(self,value,argNumber=None):
        if not isinstance(value, collections.Hashable):
            raise argException("(EnvironmentDynamic) keyname must be hashable")
    
        if value not in self.environment:
            raise argException("(EnvironmentDynamic) environment %s: the key <"%("" if argNumber == None else str(argNumber)+" ")+self.keyname+"> is not available but needed")
    
        return self.environment[value]
    
    def hasDefaultValue(self):
        return False
        
    def setDefaultValue(self,value):
        pass
        
    def erraseDefaultValue(self):
        pass

class defaultValueChecker(ArgChecker):
    def __init__(self,value):
        ArgChecker.__init__(self,0,0,False)
        self.setDefaultValue(value)
        
    def getValue(self,value,argNumber=None):
        return self.getDefaultValue()

class listArgChecker(ArgChecker):
    def __init__(self,checker,minimumSize=None,maximumSize=None):
        ArgChecker.__init__(self,minimumSize,maximumSize)
        
        if not isinstance(checker, ArgChecker) or isinstance(checker, listArgChecker):
            raise argInitializationException("(List) checker must be an instance of ArgChecker but can not be an instance of listArgChecker")

        self.checker = checker
        
    def checkValue(self, values,argNumber=None):
    
        #check if it's a list
        if not isinstance(values,list):
            if argNumber != None:
                raise argException("(List) Argument %s: this arg is not a valid list"%("" if argNumber == None else str(argNumber)+" "))
    
        #TODO manage the case with a list of 1 item
    
        if argNumber != None:
            for v in values:
                ret.append(self.checker.checkValue(v,argNumber))
                argNumber += 1
        else:
            for v in values:
                ret.append(self.checker.checkValue(v))
    
    def getValue(self,values,argNumber=None):
        ret = []
        
        #check if it's a list
        if not isinstance(values,list):
            raise argException("(List) Argument %s: this arg is not a valid list"%("" if argNumber == None else str(argNumber)+" "))

        #TODO manage the case with a list of 1 item
            #accept non list value
            #return an item and not a list

        if argNumber != None:
            for v in values:
                ret.append(self.checker.getValue(v,argNumber))
                argNumber += 1
        else:
            for v in values:
                ret.append(self.checker.getValue(v))

        return ret
    
    #TODO check the following methods
    def getDefaultValue(self):
        if ArgChecker.hasDefaultValue(self):
            return ArgChecker.getDefaultValue()
    
        if self.minimumSize == self.maximumSize == None:
            return []
    
        return self.default
        
    def hasDefaultValue(self):
        if ArgChecker.hasDefaultValue(self):
            return True
    
        if self.minimumSize == self.maximumSize == None:
            return True
            
        return False
        
    def getUsage(self):
        if self.minimumSize == None :
            if self.maximumSize == None :
                return "("+self.checker.getUsage()+" .. "+self.checker.getUsage()+")"
            return "("+self.checker.getUsage()+"0 .. "+self.checker.getUsage()+str(self.maximumSize-1)+")"
        else:
            if self.minimumSize == 1:
                part1 = self.checker.getUsage()+"0"
            elif self.minimumSize == 2:
                part1 = self.checker.getUsage() + "0 " + self.checker.getUsage()+"1"
            else:
                part1 = self.checker.getUsage() + "0 ..." + self.checker.getUsage()+str(self.minimumSize-1)
        
            if self.maximumSize == None :
                part1 += "(... "+self.checker.getUsage()+")"
            else:
                notMandatorySpace = self.maximumSize - self.minimumSize
                if notMandatorySpace == 1:
                    return part1 + "("+self.checker.getUsage()+str(self.maximumSize-1)+")"
                elif notMandatorySpace == 2:
                    return part1 + "("+self.checker.getUsage()+str(self.maximumSize-2)+""+self.checker.getUsage()+str(self.maximumSize-1)+")"
                else:
                    return part1 + "("+self.checker.getUsage()+str(self.minimumSize)+" ... "+self.checker.getUsage()+str(self.maximumSize-1)+")"
                    
    def __str__(self):
        return "listArgChecker : "+str(self.checker)
        
