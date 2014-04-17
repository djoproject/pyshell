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

class splitAndMergeTest(unittest.TestCase): 
	#TODO _willThisCmdBeCompletlyDisabled(self, cmdID, startSkipRange, rangeLength=1)
		#TODO think about test
		
	#TODO _willThisDataBunchBeCompletlyDisabled(self, dataIndex, startSkipRange, rangeLength=1)
		#TODO think about test
	
	#TODO _willThisDataBunchBeCompletlyEnabled(self, dataIndex, startSkipRange, rangeLength=1)
		#TODO think about test
	
	#TODO _skipOnCmd(self,cmdID, subCmdID, skipCount = 1)
		#TODO think about test
	
	#TODO _enableOnCmd(self, cmdID, subCmdID, enableCount = 1)
		#TODO think about test
	
	#TODO _skipOnDataBunch(self, dataBunchIndex, subCmdID, skipCount = 1)
		#TODO think about test
	
	#TODO _enableOnDataBunch(self, dataBunchIndex, subCmdID, enableCount = 1)
		#TODO think about test
 
 
 
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

    #TODO flushArgs(self, index=None)
		#FAILED
		#None index and empty stack
		#invalid index
		
		#SUCCESS
		#valid index

    #TODO addSubCommand(self, cmdID = None, onlyAddOnce = True, useArgs = True)
		#FAILED
			#cmdID is None, and empty stack
			#invalid cmd index
		
		#SUCCESS
			#none cmd id must return the cmd index at the top
			#with empty stack
			#with stack (with random data on stack, not only matching result, != path, != preprocess)
				#with path not using this cmd
				#with path using this cmd
					#with None map
					#with map enabled
				#with cmd used several times in the cmdList

    #TODO addCommand(self, cmd, convertProcessToPreProcess = False)
		#FAILED
			#try to insert a not MultiCommand instance
			#try to insert with process at top
				#with one data
				#with more than one data
			#try to insert with postprocess at top with process in the middle
			
		#SUCCESS
			#try to insert with postprocess at top without process in the middle
			#insert a valid one with process in the stack, and see if they are correctly converted
		
		

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
