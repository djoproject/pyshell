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
        #FAILED
            #empty stack
            #not pre at top

        #SUCCESS
            #add random skip count and check

    #TODO skipNextSubCommandForTheEntireDataBunch(self, skipCount=1):
        #FAILED
            #empty stack
            #not pre at top
            #disable such as the current data bunch is totaly disabled
            #disable every sub cmd

        #SUCCESS
            #set where no map exists
            #skip one or more 
            #skip already skipped

    #TODO skipNextSubCommandForTheEntireExecution(self, skipCount=1):
        #FAILED
            #empty stack
            #disable such as the current data bunch is totaly disabled
            #disable everything in the cmd

        #SUCCESS
            #disable 0 or negativ
            #disable 1 or more
            #disable more than available
            #disable to recompute path on other bunch

    #TODO disableEnablingMapOnDataBunch(self,index=0):
        #FAILED
            #invalid index stack

        #SUCCESS
            #valid disabling
    
    #TODO _setStateSubCmdInCmd(self,cmdIndex, subCmdIndex, value):
        #FAILED
        #invalid cmdIndex
        #invalid subCmdIndex
        #disable such as the current data bunch is totaly disabled
        #disable everything in the cmd

        #SUCCESS
        #update false/true in a command
        #disable to recompute path on other bunch
    
    #TODO _setStateSubCmdInDataBunch(self, dataBunchIndex, subCmdIndex, value)
		#FAILED
		#invalid stack index
		#invalid sub cmd index
        #disable such as the current data bunch is totaly disabled
        #disable every sub cmd
		
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
