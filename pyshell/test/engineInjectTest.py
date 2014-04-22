#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.command.exception import *
from pyshell.arg.decorator import shellMethod
from pyshell.arg.argchecker import ArgChecker
from pyshell.command.command import *
from pyshell.command.engine import *

def noneFun():
    pass

class injectTest(unittest.TestCase):
    def setUp(self):
        self.mc = MultiCommand("Multiple test", "help me")
        self.mc.addProcess(noneFun,noneFun,noneFun)
        
        self.mc2 = MultiCommand("Multiple test2", "help me2")
        self.mc2.addProcess(noneFun,noneFun,noneFun)
        
        self.e = engineV3([self.mc,self.mc2,self.mc2])

    #_getTheIndexWhereToStartTheSearch(self,processType)
    def test_getTheIndexWhereToStartTheSearch(self):
        #FAIL
        self.assertRaises(executionException, self.e._getTheIndexWhereToStartTheSearch, 42)
            #try a value different of pre/pro/post process

        #SUCCESS
            #if stack empty return zero
        del self.e.stack[:]
        self.assertIs(self.e._getTheIndexWhereToStartTheSearch(POSTPROCESS_INSTRUCTION),0)
        self.assertIs(self.e._getTheIndexWhereToStartTheSearch(PROCESS_INSTRUCTION),0)
        self.assertIs(self.e._getTheIndexWhereToStartTheSearch(PREPROCESS_INSTRUCTION),0)

            #three different type on stack, search each of them
        self.e.stack.append( (["a"], [0], PREPROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["b"], [0], PREPROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["c"], [0], PROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["d"], [0], PROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["e"], [0], POSTPROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["f"], [0], POSTPROCESS_INSTRUCTION, None, ) )

        self.assertIs(self.e._getTheIndexWhereToStartTheSearch(POSTPROCESS_INSTRUCTION),5)
        self.assertIs(self.e._getTheIndexWhereToStartTheSearch(PROCESS_INSTRUCTION),3)
        self.assertIs(self.e._getTheIndexWhereToStartTheSearch(PREPROCESS_INSTRUCTION),1)

            #search for each type when they are missing on stack
        del self.e.stack[:]
        self.e.stack.append( (["a"], [0], PREPROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["b"], [0], PREPROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["c"], [0], PROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["d"], [0], PROCESS_INSTRUCTION, None, ) )
        self.assertIs(self.e._getTheIndexWhereToStartTheSearch(POSTPROCESS_INSTRUCTION),3)

        del self.e.stack[:]
        self.e.stack.append( (["a"], [0], PREPROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["b"], [0], PREPROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["e"], [0], POSTPROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["f"], [0], POSTPROCESS_INSTRUCTION, None, ) )
        self.assertIs(self.e._getTheIndexWhereToStartTheSearch(PROCESS_INSTRUCTION),1)

        del self.e.stack[:]
        self.e.stack.append( (["c"], [0], PROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["d"], [0], PROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["e"], [0], POSTPROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["f"], [0], POSTPROCESS_INSTRUCTION, None, ) )
        self.assertIs(self.e._getTheIndexWhereToStartTheSearch(PREPROCESS_INSTRUCTION),-1)

    #TODO _findIndexToInject(self, cmdPath, processType)
    def test_findIndexToInject(self):
        #FAIL
            #try to find too big cmdPath, to generate invalid index
            #try to find path with invalid sub index
            #try to inject pro process with non root path

        #SUCCESS
            #make a perfect match
            #make a perfect match except for the last sub index
            #no match

            #only one match on stack
            #several match on stack (only for pre)

            #at the botom of the stack
            #or with different path under the current path (higher path ?)

            #with 0, 1 or more item of each type
            #with existing path, or inexsting path
        pass            
        
    #TODO injectDataProOrPos(self, data, cmdPath, processType, onlyAppend = False)
        #FAIL
            #try to insert unexistant path with onlyAppend=True

        #SUCCESS
            #insert existant or not
            #post or pro
        
    #TODO _injectDataPreToExecute(self, data, cmdPath, index, enablingMap = None, onlyAppend = False)
        #FAIL
            #map of invalid length (!= of path)
            #onlyAppend=True and inexistant path
            #onlyAppend=True and existant path and different map

        #SUCCESS
            #insert unexisting
            #insert existing with path matching
            #insert existing whitout path matching

            #test with index 0 or -1
        
    #TODO injectDataPre(self, data, cmdPath, enablingMap = None)
        #FAIL
            #insert existant path but with inexistant map

        #SUCCESS
            #insert existant path with existant map
                #in the beginning, in the middle or at the end of the existant
            #insert inexistant path
        
    #TODO insertDataToPreProcess(self, data, onlyForTheLinkedSubCmd = True)
        #FAIL
            #TODO

        #SUCCESS
            #TODO
        
    #TODO insertDataToProcess(self, data)
        #FAIL
            #TODO

        #SUCCESS
            #TODO
        
    #TODO insertDataToNextSubCommandPreProcess(self,data)
        #FAIL
            #TODO

        #SUCCESS
            #TODO

if __name__ == '__main__':
    unittest.main()
