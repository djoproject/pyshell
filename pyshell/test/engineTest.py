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
        self.mc = MultiCommand("Multiple test", "help me")
        self.mc.addProcess(noneFun,noneFun,noneFun)
        self.e = engineV3([self.mc])
        
    #TODO other cmd meth ...
    #TODO skipNextCommandOnTheCurrentData
    #TODO skipNextCommandForTheEntireDataBunch
    #TODO skipNextCommandForTheEntireExecution
    #TODO flushArgs
    #TODO addSubCommand
    #TODO addCommand
    
    #TODO setDataCmdRange
    #TODO setDataCmdRangeAndMerge
    
    #TODO mergeDataOnStack
    #TODO setCmdRange
    #TODO splitData
    
    #flushData
    
        
    #addData

        
    #removeData

    
    #getData and setData

    
    #hasNextData
    
    #getRemainingDataCount
    
    #getDataCount
    
    #isEmptyStack
    def test_isEmptyStack(self):
        e = engineV3([self.mc])
        self.assertFalse(e.isEmptyStack())
        
        e.stack = []
        self.assertTrue(e.isEmptyStack())
        
    #isLastStackItem
    def test_isLastStackItem(self):
        e = engineV3([self.mc])
        self.assertTrue(e.isLastStackItem())
        
        e.stack = []
        self.assertFalse(e.isLastStackItem())
    
    #getStackSize
    def test_getStackSize(self):
        e = engineV3([self.mc])
        self.assertEqual(e.getStackSize(),1)
        
        e.stack = []
        self.assertEqual(e.getStackSize(),0)
    
    #getCurrentItemMethodeType
    def test_getCurrentItemMethodeType(self):
        e = engineV3([self.mc])
        
        self.assertEqual(e.getCurrentItemMethodeType(),PREPROCESS_INSTRUCTION)
    
        #empty stack test
        e.stack = []
        self.assertRaises(executionException,e.getCurrentItemMethodeType)
    
    #getCurrentItemData
    def test_getCurrentItemData(self):
        e = engineV3([self.mc])
        
        data = e.getCurrentItemData()
        self.assertEqual(len(data),1)
        self.assertEqual(data[0],None)

        #empty stack test
        e.stack = []
        self.assertRaises(executionException,e.getCurrentItemData)
        
    #getCurrentItemCmdPath
    def test_getCurrentItemCmdPath(self):
        e = engineV3([self.mc])
        
        path = e.getCurrentItemCmdPath()
        self.assertEqual(len(path),1)
        self.assertEqual(path[0],0)

        #empty stack test
        e.stack = []
        self.assertRaises(executionException,e.getCurrentItemCmdPath)
        
    #getCurrentItemSubCmdLimit
    def test_getCurrentItemSubCmdLimit(self):
        e = engineV3([self.mc])
        
        #default limit
        (low,hight) = e.getEffectiveCurrentItemSubCmdLimit()
        self.assertEqual(low,0)
        self.assertEqual(hight,None)
    
        #test fixed limit
        self.mc.addProcess(noneFun,noneFun,noneFun)
        self.mc.addProcess(noneFun,noneFun,noneFun)
        self.mc.addProcess(noneFun,noneFun,noneFun)
        self.mc.addProcess(noneFun,noneFun,noneFun)
        self.mc.addProcess(noneFun,noneFun,noneFun)
        self.mc.addProcess(noneFun,noneFun,noneFun)
        self.mc.addProcess(noneFun,noneFun,noneFun)
        e = engineV3([self.mc])
        e.stack[-1][1][-1] = 2
        e.setCmdRange(2,3)
        
        (low,hight) = e.getEffectiveCurrentItemSubCmdLimit()
        self.assertEqual(low,2)
        self.assertEqual(hight,2)
    
        #empty stack test
        e.stack = []
        self.assertRaises(executionException,e.getEffectiveCurrentItemSubCmdLimit)
    
		#TODO make more test about the new raised exceptions
    
    #getEnv
    def test_GetEnv(self):
        mc = MultiCommand("Multiple test", "help me")
        mc.addProcess(noneFun,noneFun,noneFun)  
    
        e = engineV3([mc])
        
        self.assertIs(e.env, e.getEnv())
        
        a = {}
        a["ddd"] = 53
        a[88] = "plop"
        e = engineV3([mc],a)
        
        self.assertIs(e.env, e.getEnv())
        self.assertIs(a, e.getEnv())
    
if __name__ == '__main__':
    unittest.main()
