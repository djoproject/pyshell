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
    #TODO skipNextSubCommandOnTheCurrentData(self, skipCount=1):
    
    #TODO skipNextSubCommandForTheEntireDataBunch(self, skipCount=1):
    
    #TODO skipNextSubCommandForTheEntireExecution(self, skipCount=1):
    
    #TODO disableEnablingMapOnDataBunch(self,dept=0):
    
    #TODO _setStateSubCmdInCmd(self,cmdIndex, subCmdIndex, value):
    
    #TODO _setStateSubCmdInDataBunch(self, dataBunchIndex, subCmdIndex, value)
		#FAILED
		#invalid stack index
		#invalid sub cmd index
		
		#SUCCESS
		#test on data without map
		#test on data with map
		#test with False and True
    
    #TODO flushArgs(self, index=None)
		#FAILED
		#None index and empty stack
		#invalid index
		
		#SUCCESS
		#valid index
    
    #TODO addSubCommand(self, cmdID = None, onlyAddOnce = True, useArgs = True)
		#FAILED
		#invalid cmd index
		
		#SUCCESS
		#none cmd id must return the cmd index at the top
		#with empty stack
		#with stack
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
		#try to insert with postprocess at top without process in the middle
		
		#SUCCESS
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
