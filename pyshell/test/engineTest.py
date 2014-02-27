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
        
    #__init__
    def testInit(self):
        #check list
        self.assertRaises(executionInitException,engineV3,None)
        self.assertRaises(executionInitException,engineV3,[])
        self.assertRaises(executionInitException,engineV3,42)
        
        #check command
        mc = MultiCommand("Multiple test", "help me")
        self.assertRaises(executionInitException,engineV3,[mc])
        
        mc.addProcess(noneFun,noneFun,noneFun)
        self.assertRaises(executionInitException,engineV3,[mc, 42])
        
        mc.dymamicCount = 42
        e = engineV3([mc])
        self.assertIs(e.cmdList[0],mc)
        self.assertEqual(mc.dymamicCount, 0) #check the call on reset
        
        mc.addProcess(noneFun,noneFun,noneFun) #because the reset with the dynamic at 42 will remove every command...
        
        #empty dict
        self.assertIsInstance(e.env,dict)
        self.assertEqual(len(e.env), 0)
        
        #nawak dico
        self.assertRaises(executionInitException,engineV3,[mc], 42)
        
        #non empty dico
        a = {}
        a["ddd"] = 53
        a[88] = "plop"
        e = engineV3([mc],a)
        self.assertIsInstance(e.env,dict)
        self.assertEqual(len(e.env), 2)
        
        
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
    def test_flushData(self):
        e = engineV3([self.mc])
        e.flushData()
        self.assertIs(len(e.stack[0][0]),0)
        
        e.addData(11)
        e.addData(12)
        e.addData(13)
        self.assertIs(len(e.stack[0][0]),3)
        e.flushData()
        self.assertIs(len(e.stack[0][0]),0)
        
        e.stack = []
        self.assertRaises(executionException,e.flushData)
        
    #addData
    def test_addData(self):
        self.assertRaises(executionException,self.e.addData, 33, 0)
        
        #regular addData
        self.e.addData(33,0,False)
        self.assertIs(len(self.e.stack[0][0]),2)
        self.assertIs(self.e.stack[0][0][0],33)
        self.assertIs(self.e.stack[0][0][1],None)
        
        self.e.addData(44)
        self.assertIs(len(self.e.stack[0][0]),3)
        self.assertIs(self.e.stack[0][0][0],33)
        self.assertIs(self.e.stack[0][0][1],44)
        self.assertIs(self.e.stack[0][0][2],None)
        
        self.e.stack = []
        self.assertRaises(executionException,self.e.addData, 33)
        
    #removeData
    def test_removeData(self):
        self.assertRaises(executionException,self.e.removeData, -2)
        self.assertRaises(executionException,self.e.removeData, 1)
        
        self.e.removeData()
        self.assertIs(len(self.e.stack[0][0]),0)
        self.assertIs(self.e.stack[0][1][-1],-1)
        
        self.e.addData(None)
        self.e.addData(44)
        self.e.addData(55)
        
        self.e.removeData(1)
        self.assertIs(len(self.e.stack[0][0]),2)
        self.assertIs(self.e.stack[0][1][-1],-1)
        self.assertIs(self.e.stack[0][0][0],None)
        self.assertIs(self.e.stack[0][0][1],44)
        
        self.e.flushData()
        self.e.addData(None)
        self.e.addData(44)
        self.e.addData(55)
        
        self.e.removeData(-2)
        self.assertIs(len(self.e.stack[0][0]),2)
        self.assertIs(self.e.stack[0][1][-1],-1)
        self.assertIs(self.e.stack[0][0][0],None)
        self.assertIs(self.e.stack[0][0][1],44)
        
        self.e.stack = []
        self.assertRaises(executionException,self.e.removeData)
    
    #getData and setData
    def test_getData(self):
        e = engineV3([self.mc])
        
        self.assertEqual(e.getData(), None) 
        e.setData(32)
        self.assertEqual(e.getData(), 32) 
        e.setData(None)
        self.assertEqual(e.getData(), None) 
        
        e.stack = []
        self.assertRaises(executionException,e.getData)
        self.assertRaises(executionException,e.setData, 33)
    
    #hasNextData
    def test_hasNextData(self):
        e = engineV3([self.mc])
        
        self.assertFalse(e.hasNextData())
        e.addData(11)
        self.assertTrue(e.hasNextData())
        
        e.stack = []
        self.assertRaises(executionException,e.hasNextData)
    
    #getRemainingDataCount
    def test_getRemainingDataCount(self):
        e = engineV3([self.mc])
        
        self.assertEqual(e.getRemainingDataCount(), 0)
        e.addData(11)
        self.assertEqual(e.getRemainingDataCount(), 1)
        e.addData(12)
        e.addData(13)
        e.addData(14)
        e.addData(15)
        self.assertEqual(e.getRemainingDataCount(), 5)
        
        e.stack = []
        self.assertRaises(executionException,e.getRemainingDataCount)
    
    #getDataCount
    def test_getDataCount(self):
        e = engineV3([self.mc])
        
        self.assertEqual(e.getDataCount(), 1)
        e.addData(11)
        self.assertEqual(e.getDataCount(), 2)
        e.addData(12)
        e.addData(13)
        e.addData(14)
        e.addData(15)
        self.assertEqual(e.getDataCount(), 6)
        
        e.stack = []
        self.assertRaises(executionException,e.getDataCount)
    
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
        (low,hight) = e.getCurrentItemSubCmdLimit()
        self.assertEqual(low,0)
        self.assertEqual(hight,0)
    
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
        
        (low,hight) = e.getCurrentItemSubCmdLimit()
        self.assertEqual(low,2)
        self.assertEqual(hight,4)
    
        #empty stack test
        e.stack = []
        self.assertRaises(executionException,e.getCurrentItemSubCmdLimit)
    
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
