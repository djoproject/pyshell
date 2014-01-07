#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyshell.utils.ordereddict import OrderedDict
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
        #mais cela implique que la definition du dico ordonnée soit utilisée en dehors
        #perte en genericite
            #mais ici, c'est un peu degeu, on a une liste qui contient des paires key/value
                #en soi argfeeder est initialisé dans un decorateur, ça ne passe pas dans le code utilisateur

    #si len(self.argTypeList) == 0, on ne renvoit rien
        #si pas de parametre a binder, pas de parametre a retourner, meme en cas de data, pas notre prblm
            #semble coherent

class ArgFeeder(ArgsChecker):

    #
    # @param argTypeList, une liste de tuple (Argname,ArgChecker) 
    #
    def __init__(self,argTypeList):
        if argTypeList == None or not isinstance(argTypeList,list): 
            raise argInitializationException("(ArgFeeder) argTypeList must be a valid list")
        
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
