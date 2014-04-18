#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.command.exception import *
from pyshell.arg.decorator import shellMethod
from pyshell.arg.argchecker import ArgChecker
from pyshell.command.command import *
from pyshell.command.engine import *

@shellMethod(arg=ArgChecker()) 
def plop(arg):
    return arg
    
def noneFun():
    pass


class splitAndMergeTest(unittest.TestCase): 
    def setUp(self):
        self.mc = MultiCommand("Multiple test", "help me")
        self.mc.addProcess(noneFun,noneFun,noneFun)
        
        self.mc2 = MultiCommand("Multiple test2", "help me2")
        self.mc2.addProcess(noneFun,noneFun,noneFun)
        
        self.e = engineV3([self.mc,self.mc2,self.mc2])

    #TODO _willThisCmdBeCompletlyDisabled(self, cmdID, startSkipRange, rangeLength=1)
        #must return False
            #empty before range, at least on item true in the after range
            #not empty before range but no value set to true, at least on item true in the after range
            #empty after range, at least on item true in the before range
            
            #range must have a size of 1 or more than 1
            #skip range must have a size of 0, 1 or more than 1
        
        #mist return True
            #empty before and empty after range
            #empty before range and after range only set to False
            #before range not empty but only with false value, after range empty
            #before range not empty but only with false value, after range not empty but only with false value
            
            #range must have a size of 1 or more than 1
            #skip range must have a size of 0, 1 or more than 1
        
    #TODO _willThisDataBunchBeCompletlyDisabled(self, dataIndex, startSkipRange, rangeLength=1)
        #same test as previous, must give the same results, enable map is set to None
        
        #same test as previous, but every cmd are enabled and enableMap keep the values, msut give the same results
    
    #TODO _willThisDataBunchBeCompletlyEnabled(self, dataIndex, startSkipRange, rangeLength=1)
        #must return False
            #empty before range, at least on item False in the after range
            #not empty before range but no value set to False, at least on item False in the after range
            #empty after range, at least on item False in the before range
            
            #range must have a size of 1 or more than 1
            #skip range must have a size of 0, 1 or more than 1
        
        #mist return True
            #None map
            #empty before and empty after range
            #empty before range and after range only set to True
            #before range not empty but only with True value, after range empty
            #before range not empty but only with True value, after range not empty but only with True value
            
            #range must have a size of 1 or more than 1
            #skip range must have a size of 0, 1 or more than 1
    
    #TODO _skipOnCmd(self,cmdID, subCmdID, skipCount = 1)
        #FAILED
            #skip count < 1
            #invalic cmd index
            #invalid sub cmd index
            #this will completly disable a entire cmd
            #this will disable compeltly a databunch at the current cmdID
            #this will disable compeltly a databunch at a different cmdID but with the same command

        #SUCCESS
            #disable range
                #at the biggining
                #at the end
                #in the middle
            #range of length 1 or more than 1
            #with empty stack or not
            #with pre/post/pro process on the stack
            #switch to False some already false, or not
    
    #TODO _enableOnCmd(self, cmdID, subCmdID, enableCount = 1)
        #FAILED
            #skip count < 1
            #invalic cmd index
            #invalid sub cmd index
            
        #SUCCESS
            #enable range
                #at the biggining
                #at the end
                #in the middle
            #range of length 1 or more than 1
            #switch to true some already true, or not
    
    #TODO _skipOnDataBunch(self, dataBunchIndex, subCmdID, skipCount = 1)
        #FAILED
            #skip count < 1
            #empty stack
            #invalic dataBunchIndex index
            #invalid sub cmd index
            #not a preprocess
            #will be completly disabled
        
        #SUCCESS
            #enable range
                #at the biggining
                #at the end
                #in the middle
            #range of length 1 or more than 1
            #enablingMap is none, or not
            #switch to False some already false, or not
    
    #TODO _enableOnDataBunch(self, dataBunchIndex, subCmdID, enableCount = 1)
        #FAILED
            #skip count < 1
            #empty stack
            #invalic dataBunchIndex index
            #invalid sub cmd index
            #not a preprocess
            
        #SUCCESS
            #totaly reenabled a databunch
                #original map was None, or not
            
            #enable range
                #at the biggining
                #at the end
                #in the middle
            #range of length 1 or more than 1
            #enablingMap is none, or not
            #switch to True some already True, or not
 
    #TODO skipNextSubCommandOnTheCurrentData(self, skipCount=1):
        #FAILED
            #invalid skip count
            #empty stack
            #not pre at top
            
        #SUCCESS
            #add random skip count and check

    #TODO skipNextSubCommandForTheEntireDataBunch(self, skipCount=1):
        #FAILED
            #empty stack

        #SUCCESS
            #no test to do

    #TODO skipNextSubCommandForTheEntireExecution(self, skipCount=1):
        #FAILED
            #empty stack
            #no preprocess at top

        #SUCCESS
            #no test to do

    #TODO disableEnablingMapOnDataBunch(self,index=0):
        #FAILED
            #invalid index stack
            #not pre at top
            #invalid stack index

        #SUCCESS
            #valid disabling
                #where already none
                #where not


    #flushArgs(self, index=None)
    def test_flushArgs(self):
        #FAILED
			#None index and empty stack
		del self.e.stack[:]
		self.assertRaises(executionException, self.e.flushArgs)
		
			#invalid index
		self.assertRaises(executionException, self.e.flushArgs, -8000)
		self.assertRaises(executionException, self.e.flushArgs, 123)
        
        #SUCCESS
			#valid index
		self.mc.setArgs("toto")
		self.mc2.setArgs("tata")
		self.assertEqual(self.mc.args,["toto"])
		self.assertEqual(self.mc2.args,["tata"])
		
		self.e.flushArgs(1)
		self.assertEqual(self.mc.args,["toto"])
		self.assertEqual(self.mc2.args,None)

    #addSubCommand(self, cmd, cmdID = None, onlyAddOnce = True, useArgs = True)
    def test_addSubCommand(self):
        #FAILED
            #invalid sub cmd instance
        self.assertRaises(executionException, self.e.addSubCommand, None)
        self.assertRaises(executionException, self.e.addSubCommand, "toto")
        self.assertRaises(executionException, self.e.addSubCommand, 52)
        
            #cmdID is None, and empty stack
        del self.e.stack[:]
        self.assertRaises(executionException, self.e.addSubCommand,Command())
        
            #invalid cmd index
        self.assertRaises(executionException, self.e.addSubCommand,Command(), -8000)
        self.assertRaises(executionException, self.e.addSubCommand,Command(), 123)
            
        #SUCCESS
            #with empty stack
        self.e.addSubCommand(Command(), 1)  
        self.assertEqual(len(self.e.cmdList[1]), 2)
        
            #with not empty stack
        self.e.stack.append( (["a","b","c"], [0], PREPROCESS_INSTRUCTION, None,) )
        self.e.stack.append( (["d","e","f"], [0,1], PREPROCESS_INSTRUCTION, None,) )
        
            #none cmd id must return the cmd index at the top
        self.e.addSubCommand(Command(), None)
        self.assertEqual(len(self.e.cmdList[0]), 1)
        self.assertEqual(len(self.e.cmdList[1]), 3)
        
        self.e.stack.append( (["d","e","f"], [0,1], PREPROCESS_INSTRUCTION, [True,False,True],) ) 
        self.e.stack.append( (["d","e","f"], [0,1,0], PREPROCESS_INSTRUCTION, [True,False,True],) ) 
        
            #with stack (with random data on stack, not only matching result, != path, != preprocess)
        self.e.addSubCommand(Command(), 1)
                #with path not using this cmd
                #with path using this cmd
                    #with None map
                    #with map enabled
                #with cmd used several times in the cmdList
        self.assertEqual(self.e.stack[1][3],None)
        self.assertEqual(len(self.e.stack[2][3]),4)
        self.assertEqual(len(self.e.stack[3][3]),4)

    #addCommand(self, cmd, convertProcessToPreProcess = False)
    def test_addCommand(self):
        #FAILED
            #try to insert a not MultiCommand instance
        self.assertRaises(executionException, self.e.addCommand, None)
        self.assertRaises(executionException, self.e.addCommand, "toto")
        self.assertRaises(executionException, self.e.addCommand, 52)
        
            #try to insert with process at top
                #with more than one data
        del self.e.stack[:]
        self.e.stack.append( (["a","b","c"], [0], PROCESS_INSTRUCTION, None,) )
        self.assertRaises(executionException, self.e.addCommand, self.mc)
        
            #try to insert with postprocess at top with process in the middle
        del self.e.stack[:]
        self.e.stack.append( (["a","b","c"], [0], PROCESS_INSTRUCTION, None,) )
        self.e.stack.append( (["a"], [0], POSTPROCESS_INSTRUCTION, None,) )
        self.assertRaises(executionException, self.e.addCommand, self.mc)
        
        #SUCCESS
            #try to insert with process at top
                #with only one data
        del self.e.stack[:]
        self.e.stack.append( (["a"], [0], PROCESS_INSTRUCTION, None,) )
        self.e.addCommand(self.mc)
                
            #try to insert with postprocess at top without process in the middle
        del self.e.stack[:]
        self.e.stack.append( (["a"], [0], POSTPROCESS_INSTRUCTION, None,) )
        self.e.addCommand(self.mc)
            
            #insert a valid one with process in the stack, and see if they are correctly converted
        del self.e.stack[:]
        self.e.stack.append( (["a","b","c"], [0], PROCESS_INSTRUCTION, None,) )
        self.e.stack.append( (["a"], [0], POSTPROCESS_INSTRUCTION, None,) )
        self.e.addCommand(self.mc, True)        
        self.assertEqual(self.e.stack[0][2], PREPROCESS_INSTRUCTION)
        
    def test_isCurrentRootCommand(self):
        mc = MultiCommand("Multiple test")
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)

        engine = engineV3([mc,mc,mc])

        self.assertTrue(engine.isCurrentRootCommand())

        engine.stack[-1][1].append(2)
        self.assertFalse(engine.isCurrentRootCommand())

        del engine.stack[:]
        self.assertRaises(executionException, engine.isCurrentRootCommand)
    
    
if __name__ == '__main__':
    unittest.main()
