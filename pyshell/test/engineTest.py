#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.command.engine import *
from pyshell.command.command import *
from pyshell.arg.decorator import shellMethod
from pyshell.arg.argchecker import ArgChecker, IntegerArgChecker

def noneFun():
    pass

class EngineTest(unittest.TestCase):
    def setUp(self):
        pass

    #TODO __init__
    def testInit(self):
        #check list
        self.assertRaise(executionInitException,engineV3,None)
        self.assertRaise(executionInitException,engineV3,[])
        self.assertRaise(executionInitException,engineV3,42)
        
        #check command
        mc = MultiCommand("Multiple test", "help me")
        self.assertRaise(executionInitException,engineV3,[mc])
        
        mc.addProcess(noneFun,noneFun,noneFun)
        self.assertRaise(executionInitException,engineV3,[mc, 42])
        
        e = engineV3([mc])
        self.assertIs(e.cmdList,mc)
        
            #TODO check the call on reset
        
        #TODO check dico
        
    #TODO skipNextCommandOnTheCurrentData
    #TODO skipNextCommandForTheEntireDataBunch
    #TODO skipNextCommandForTheEntireExecution
    #TODO flushArgs
    #TODO addSubCommand
    #TODO addCommand
    #TODO flushData
    #TODO addData
    #TODO removeData
    #TODO setData
    #TODO mergeDataOnStack
    #TODO setCmdRange
    #TODO splitData
    #TODO setDataCmdRange
    #TODO getData
    #TODO hasNextData
    #TODO getRemainingDataCount
    #TODO isEmptyStack
    #TODO isLastStackItem
    #TODO getStackSize
    #TODO getCurrentItemMethodeType
    #TODO getCurrentItemData
    #TODO getCurrentItemCmdPath
    #TODO getCurrentItemCmdLimit
    #TODO getEnv
