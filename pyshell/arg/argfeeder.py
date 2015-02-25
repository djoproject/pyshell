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

import sys
if sys.version_info[0] < 2 or (sys.version_info[0] < 3 and sys.version_info[0] < 7):
    from pyshell.utils.ordereddict import OrderedDict #TODO get from pipy, so the path will change
else:
    from collections import OrderedDict 
    
from pyshell.arg.exception import *

###############################################################################################
##### ArgsChecker #############################################################################
###############################################################################################
class ArgsChecker():
    "abstract arg checker"

    #
    # @argsList, une liste de string
    # @return, un dico trie des arguments et de leur valeur : <name,value>
    # 
    def checkArgs(self,argsList, engine=None):
        pass #XXX to override
        
    def usage(self):
        pass #XXX to override
    
class ArgFeeder(ArgsChecker):

    #
    # @param argTypeList, une liste de tuple (Argname,ArgChecker) 
    #
    def __init__(self,argTypeList):
        #take an ordered dict as argTypeList parameter  
        if not isinstance(argTypeList,OrderedDict) and  ( not isinstance(argTypeList, dict) or len(argTypeList) != 0): 
            raise argInitializationException("(ArgFeeder) argTypeList must be a valid instance of an ordered dictionnary")
        
        self.argTypeList = argTypeList
    
    def manageMappedArg(self, name, checker, args):
        if checker.maximumSize is not None and len(args) > checker.maximumSize:
            args = args[:checker.maximumSize]

        if checker.minimumSize is not None and len(args) < checker.minimumSize:
            raise argException("(ArgFeeder) not enough data for the dash mapped argument '"+name+"', expected at least '"+str(checker.minimumSize)+"', got '"+str(len(args))+"'")

        if checker.minimumSize == checker.maximumSize == 1:
            args = args[0]
                
        return checker.getValue(args,None, name)

    #
    # @argsList, une liste de n'importe quoi
    # @return, un dico trie des arguments et de leur valeur : <name,value>
    # 
    def checkArgs(self,argsList, mappedArgs, engine=None):
        if not hasattr(argsList,"__iter__"):#if not isinstance(argsList,list):
            # argsList must be a string
            #if type(argsList) != str and type(argsList) != unicode:
            #    raise argException("(ArgFeeder) string list was expected, got "+str(type(argsList)))
        
            #argsList = [argsList]
            argsList = (argsList,)
            #no need to check the other args, they will be checked into the argcheckers
    
        ret             = {}
        argCheckerIndex = 0
        dataIndex       = 0

        for (name,checker) in self.argTypeList.iteritems():
            #set the engine
            checker.setEngine(engine)

            #is it a mapped args ?
            if name in mappedArgs:
                ret[name] = self.manageMappedArg(name, checker, mappedArgs[name])
                argCheckerIndex += 1
                continue
        
            #is there a minimum limit
            if checker.minimumSize is not None:
                #is there at least minimumSize item in the data stream?
                if len(argsList[dataIndex:]) < checker.minimumSize:
                    #no more string token, end of stream ?
                    if len(argsList[dataIndex:]) == 0:
                        #we will check if there is some default value
                        break 
                    else:
                        #there are data but not enough
                        raise argException("(ArgFeeder) not enough data for the argument '"+name+"'")
            
            #is there a maximum limit?
            if checker.maximumSize is None:
                #No max limit, it consumes all remaining data
                ret[name] = checker.getValue(argsList[dataIndex:],dataIndex, name)
                dataIndex = len(argsList) #will not stop the loop but will notify that every data has been consumed
            else:
                #special case: checker only need one item? (most common case)
                if checker.minimumSize is not None and checker.minimumSize == checker.maximumSize == 1:
                    value = argsList[dataIndex:(dataIndex+checker.maximumSize)][0]
                else:
                    value = argsList[dataIndex:(dataIndex+checker.maximumSize)]
                    
                ret[name] = checker.getValue(value,dataIndex, name)
                dataIndex += checker.maximumSize

            argCheckerIndex += 1
        
        # MORE THAN THE LAST ARG CHECKER HAVEN'T BEEN CONSUMED YET
        items_list = list(self.argTypeList.items())
        for i in range(argCheckerIndex,len(self.argTypeList)):
            (name,checker) = items_list[i]
            checker.setEngine(engine)

            #is it a mapped args ?
            if name in mappedArgs:
                ret[name] = self.manageMappedArg(name, checker, mappedArgs[name])
                continue

            #is there a default value ?
            if not checker.hasDefaultValue(name):
                raise argException("(ArgFeeder) some arguments aren't bounded, missing data : '"+name+"'")
            
            ret[name] = checker.getDefaultValue(name)
            
        #don't care about unused data in argsList, if every parameter are binded, we are happy :)

        return ret
        
    def usage(self):
        if len(self.argTypeList) == 0:
            return "no args needed"
    
        ret = ""
        firstMandatory = False
        for (name,checker) in self.argTypeList.iteritems():
            if not checker.showInUsage:
                continue
        
            if checker.hasDefaultValue(name) and not firstMandatory:
                ret += "["
                firstMandatory = True
            
            ret += name+":"+checker.getUsage()+" "
        
        ret = ret.strip()
        
        if firstMandatory:
            ret += "]"
        
        return ret
