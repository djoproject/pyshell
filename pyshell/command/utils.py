#!/usr/bin/python
# -*- coding: utf-8 -*-

from exception import executionException

def equalPath(path1,path2):
    sameLength    = True
    equals        = True

    if len(path1) != len(path2):
        sameLength = False
        equals     = False
    
    equalsCount = 0
    path1IsHigher = None
    for i in range(0, min(len(path1), len(path2))):
        if path1[i] != path2[i]:
            equals = False
            path1IsHigher = path1[i] > path2[i]
            break
            
        equalsCount += 1 
    
    return equals, sameLength, equalsCount, path1IsHigher

def isAValidIndex(li, index, cmdName = None, listName = None, context="engine", ex = executionException):
    try:
        noop = li[index]
    except IndexError:
        if cmdName != None:
            cmdName += ", "
        else:
            cmdName = ""
        
        if listName != None:
            listName = " on list <"+listName+">"
        else:
            listName = ""
        
        raise ex("("+context+") "+cmdName+"list index out of range"+listName)

def equalMap(map1,map2):
    if map1 == None and map2 == None:
        return True

    if map1 != None and map2 != None:
        if len(map1) != len(map2):
            return False

        for i in range(0,len(map2)):
            if map1[i] != map2[i]:
                return False

        return True
    
    return False

def isValidMap(emap, expectedLength):
    if emap == None:
        return True

    if not isinstance(emap,list):
        return False

    if len(emap) != expectedLength:
        return False

    falseCount = 0
    for b in emap:
        if type(b) != bool:
            return False

        if not b:
            falseCount += 1

    if falseCount == len(emap):
        return False

    return True

def raisIfInvalidMap(emap, expectedLength, cmdName = None, context="engine", ex = executionException):
    if not isValidMap(emap, expectedLength):
        if cmdName != None:
            cmdName += ", "
        else:
            cmdName = ""
        
        raise ex("("+context+") "+cmdName+"list index out of range on enabling map")

def raiseIfInvalidPath(cmdPath, cmdList, methName):
    #check command path
    isAValidIndex(cmdList, len(cmdPath)-1,methName, "command list")

    #check subindex
    for i in xrange(0,len(cmdPath)):
        isAValidIndex(cmdList[i], cmdPath[i],methName, "sub command list")

def getFirstEnabledIndexInEnablingMap(enablingMap, starting=0, cmdName = None, context="engine", ex = executionException):
    i = 0
    if enablingMap != None:
        #there is at least one True item in list, otherwise raisIfInvalidMap had raise an exception
        for i in xrange(starting,len(enablingMap)):
            if enablingMap[i]:
                return i

        if cmdName != None:
            cmdName += ", "
        else:
            cmdName = ""

        raise ex("("+context+") "+cmdName+" no enabled index on this enabling map from "+str(starting)+" to the end")

    return i


