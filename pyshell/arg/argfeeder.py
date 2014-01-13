#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
if sys.version_info[0] < 2 or (sys.version_info[0] < 3 and sys.version_info[0] < 7):
    from pyshell.utils.ordereddict import OrderedDict #TODO get from pipy, so the path will change
else:
    from collections import OrderedDict 
    
from exception import *

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

#TODO
    #self.argTypeList devrait idealement etre un dictionnaire ordonnee
        #car les arg sont associe a une cle qui doit etre unique
        #et les arg arrivent dans un ordre precis pour le parsing
    
        #mais cela implique que la definition du dico ordonnée soit utilisée en dehors
            #juste dans le decorator en fait
            #disponible a partir de 2.7...
                #et on est bloqué en 2.6 avec pyscard sur macos
        #perte en genericite
            #mais ici, c'est un peu degeu, on a une liste qui contient des paires key/value
                #en soi argfeeder est initialisé dans un decorateur, ça ne passe pas dans le code utilisateur

        #XXX soit on laisse comme ça, soit on modifie dans le decorator
            #on peut garder le principe de liste mais alors on verifie qu'on a pas deux fois la meme cle
        
    #XXX OK, take an ordered dict, check the type
        #if will be the responsability of decorator to create the orderedDict    
    
class ArgFeeder(ArgsChecker):

    #
    # @param argTypeList, une liste de tuple (Argname,ArgChecker) 
    #
    def __init__(self,argTypeList):
        #TODO take an ordered dict as argTypeList parameter
    
        if argTypeList == None or not isinstance(argTypeList,list): 
            raise argInitializationException("(ArgFeeder) argTypeList must be a valid list")

        self.argTypeList = argTypeList
        
    #
    # @argsList, une liste de string
    # @return, un dico trie des arguments et de leur valeur : <name,value>
    # 
    def checkArgs(self,argsList):
        if not isinstance(argsList,list):
            #TODO argsList must be a string
        
            argsList = [argsList]
            
            #XXX no need to check the other args, they will be checked into the argcheckers
    
        #print argsList
        ret = {}

        argCheckerIndex = 0
        dataIndex = 0
        for (name,checker) in self.argTypeList:
            #is there a minimum limit
            if checker.minimumSize != None:
                #is there at least minimumSize item in the data stream?
                if len(argsList[dataIndex:]) < checker.minimumSize:
                    #no more string token, end of stream ?
                    if len(argsList[dataIndex:]) == 0:
                        #we will check if there is some default value
                        break 
                    else:
                        #there are data but not enough
                        raise argException("(ArgFeeder) not enough data for the argument <"+name+">")
            
            #is there a maximum limit?
            if checker.maximumSize == None:
                #No max limit, it consumes all remaining data
                ret[name] = checker.getValue(argsList[dataIndex:],dataIndex)
                dataIndex = len(argsList) #will not stop the loop but will notify that every data has been consumed
            else:
                #special case: checker only need one item? (most common case)
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

        #don't care about unused data in argsList, if every parameter are binded, we are happy :)

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
        
        ret = ret.strip()
        
        if firstMandatory:
            ret += "]"
        
        return ret
