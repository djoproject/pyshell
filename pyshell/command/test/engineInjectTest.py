#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

#Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
        self.mc = MultiCommand()
        self.mc.addProcess(noneFun,noneFun,noneFun)
        self.mc.addProcess(noneFun,noneFun,noneFun)
        self.mc.addProcess(noneFun,noneFun,noneFun)
        self.mc.addProcess(noneFun,noneFun,noneFun)

        self.mc2 = MultiCommand()
        self.mc2.addProcess(noneFun,noneFun,noneFun)
        self.mc2.addProcess(noneFun,noneFun,noneFun)
        self.mc2.addProcess(noneFun,noneFun,noneFun)
        self.mc2.addProcess(noneFun,noneFun,noneFun)

        self.e = EngineV3([self.mc,self.mc2,self.mc2,self.mc2], [[],[],[],[]], [[{},{},{}],[{},{},{}],[{},{},{}],[{},{},{}] ])

    def resetStack(self):
        del self.e.stack[:]
        self.e.stack.append( (["a"], [0,2], PREPROCESS_INSTRUCTION, None, ) )

        self.e.stack.append( (["b"], [0,2,0], PREPROCESS_INSTRUCTION, [True, True, True, True], ) )
        self.e.stack.append( (["b"], [0,2,0], PREPROCESS_INSTRUCTION, [True, False, True, True], ) )
        self.e.stack.append( (["b"], [0,2,0], PREPROCESS_INSTRUCTION, [True, True, False, True], ) )

        self.e.stack.append( (["c"], [0,3,0,0], PROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["d"], [0,2,0,0], PROCESS_INSTRUCTION, None, ) )

        self.e.stack.append( (["e"], [0,3], POSTPROCESS_INSTRUCTION, None, ) )
        self.e.stack.append( (["f"], [0,2,0], POSTPROCESS_INSTRUCTION, None, ) )

    #_getTheIndexWhereToStartTheSearch(self,processType)
    def test_getTheIndexWhereToStartTheSearch(self):
        #FAIL
        self.assertRaises(ExecutionException, self.e._getTheIndexWhereToStartTheSearch, 42)
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

    #_findIndexToInject(self, cmd_path, processType)
    def test_findIndexToInject(self):
        #FAIL
            #try to find too big cmd_path, to generate invalid index
        self.assertRaises(ExecutionException, self.e._findIndexToInject, [1,2,3,4], PREPROCESS_INSTRUCTION)
            #try to find path with invalid sub index
        self.assertRaises(ExecutionException, self.e._findIndexToInject, [0,25], PREPROCESS_INSTRUCTION)

            #try to inject pro process with non root path
        self.assertRaises(ExecutionException, self.e._findIndexToInject, [0,0], PROCESS_INSTRUCTION)

        #SUCCESS

        #perfect match
        self.resetStack()
        r = self.e._findIndexToInject([0,2,0], POSTPROCESS_INSTRUCTION)
        self.assertIs(r[1], 7)
        self.assertEqual(r[0], self.e.stack[7])

        r = self.e._findIndexToInject([0,3], POSTPROCESS_INSTRUCTION)
        self.assertIs(r[1], 6)
        self.assertEqual(r[0], self.e.stack[6])

        r = self.e._findIndexToInject([0,2,0,0], PROCESS_INSTRUCTION)
        self.assertIs(r[1], 5)
        self.assertEqual(r[0], self.e.stack[5])

        r = self.e._findIndexToInject([0,3,0,0], PROCESS_INSTRUCTION)
        self.assertIs(r[1], 4)
        self.assertEqual(r[0], self.e.stack[4])

        r = self.e._findIndexToInject([0,2,0], PREPROCESS_INSTRUCTION)
        self.assertIs(len(r), 3)
        for i in range(0, 3):
            self.assertIs(r[i][1],3-i)
            self.assertEqual(r[i][0], self.e.stack[3-i])

        r = self.e._findIndexToInject([0,3], PREPROCESS_INSTRUCTION)
        self.assertIs(len(r), 1)
        self.assertIs(r[0][1], 0)
        self.assertIs(r[0][0], self.e.stack[0])

        #partial match
        r = self.e._findIndexToInject([0,2,1], PREPROCESS_INSTRUCTION)
        self.assertIs(len(r), 3)
        for i in range(0, 3):
            self.assertIs(r[i][1],3-i)
            self.assertEqual(r[i][0], self.e.stack[3-i])

        r = self.e._findIndexToInject([0,3], PREPROCESS_INSTRUCTION)
        self.assertIs(len(r), 1)
        self.assertIs(r[0][1], 0)
        self.assertIs(r[0][0], self.e.stack[0])

        #no match
        r = self.e._findIndexToInject([0,2,0,0], POSTPROCESS_INSTRUCTION) #too long path stop
        self.assertIs(r[1], 8)
        self.assertIs(r[0], None)
        r = self.e._findIndexToInject([0,1,0], POSTPROCESS_INSTRUCTION) #too hight path on stack stop
        self.assertIs(r[1], 8)
        self.assertIs(r[0], None)

        r = self.e._findIndexToInject([0,1,0,0], PROCESS_INSTRUCTION) #too long path stop
        self.assertIs(r[1], 6)
        self.assertIs(r[0], None)

        r = self.e._findIndexToInject([0,2,0,0], PREPROCESS_INSTRUCTION) #too long path stop
        self.assertIs(len(r), 1)
        self.assertIs(r[0][1], 4)
        self.assertIs(r[0][0], None)

        r = self.e._findIndexToInject([0,1,0], PREPROCESS_INSTRUCTION) #too hight path on stack stop
        self.assertIs(len(r), 1)
        self.assertIs(r[0][1], 4)
        self.assertIs(r[0][0], None)

    #_injectDataProOrPos(self, data, cmd_path, processType, onlyAppend = False)
    def test_injectDataProOrPos(self):
        #FAIL
        self.resetStack()
            #try to insert unexistant path with onlyAppend=True
        self.assertRaises(ExecutionException, self.e._injectDataProOrPos("toto", [0,3],POSTPROCESS_INSTRUCTION, True))

        #SUCCESS
            #existant
        self.assertRaises(ExecutionException, self.e._injectDataProOrPos("titi", [0,3,0,0],PROCESS_INSTRUCTION, True))
        self.assertIn("titi", self.e.stack[4][0])
        self.assertRaises(ExecutionException, self.e._injectDataProOrPos("toto", [0,3],POSTPROCESS_INSTRUCTION, True))
        self.assertIn("toto", self.e.stack[6][0])

            #not existant
        self.assertRaises(ExecutionException, self.e._injectDataProOrPos("plop", [0,1,0,0],PROCESS_INSTRUCTION))
        self.assertIn("plop", self.e.stack[6][0])

        self.assertRaises(ExecutionException, self.e._injectDataProOrPos("plap", [1],POSTPROCESS_INSTRUCTION))
        self.assertIn("plap", self.e.stack[7][0])

    #injectDataPre(self, data, cmd_path, enablingMap = None, onlyAppend = False, ifNoMatchExecuteSoonerAsPossible = True)
    def test_injectDataPre(self):
        #FAIL
            #map of invalid length
        self.assertRaises(ExecutionException, self.e.injectDataPre, "plop", [0,1,2], "toto")
        self.assertRaises(ExecutionException, self.e.injectDataPre, "plop", [0,1,2], [1,2,3,4])
        self.assertRaises(ExecutionException, self.e.injectDataPre, "plop", [0,1,2], [True, False])

            #no match and onlyAppend = True
        self.assertRaises(ExecutionException, self.e.injectDataPre, "plop", [0,1,2], [True, False,True,False], True)

            #onlyAppend=True and existant path and different map
        self.resetStack()
        self.assertRaises(ExecutionException, self.e.injectDataPre, "plop", [0,2,0], [True, False,True,False], True)

        #SUCCESS
            #insert unexisting
        self.e.injectDataPre("plop", [0,1,2], [True, False,True,False])
        self.assertEqual(self.e.stack[4][0], ["plop"])
        self.assertEqual(self.e.stack[4][1], [0,1,0])
        self.assertEqual(self.e.stack[4][2], PREPROCESS_INSTRUCTION)
        self.assertEqual(self.e.stack[4][3], [True, False,True,False])

            #insert existing with path matching
        self.e.injectDataPre("plip", [0,2,0], [True, False, True, True])
        self.assertEqual(self.e.stack[2][0], ["b","plip"])

            #insert existing whitout path matching with ifNoMatchExecuteSoonerAsPossible = True
        self.e.injectDataPre("plap", [0,2,0], [True, False,True,False], False, True)
        self.assertEqual(self.e.stack[4][0], ["plap"])
        self.assertEqual(self.e.stack[4][1], [0,2,0])
        self.assertEqual(self.e.stack[4][2], PREPROCESS_INSTRUCTION)
        self.assertEqual(self.e.stack[4][3], [True, False,True,False])

            #insert existing whitout path matching with ifNoMatchExecuteSoonerAsPossible = False
        self.e.injectDataPre("plyp", [0,2,0], [True, False,False,False], False, False)
        self.assertEqual(self.e.stack[1][0], ["plyp"])
        self.assertEqual(self.e.stack[1][1], [0,2,0])
        self.assertEqual(self.e.stack[1][2], PREPROCESS_INSTRUCTION)
        self.assertEqual(self.e.stack[1][3], [True, False,False,False])

    #insertDataToPreProcess(self, data, onlyForTheLinkedSubCmd = True)
    def test_insertDataToPreProcess(self):
        #FAIL
            #empty stack
        del self.e.stack[:]
        self.assertRaises(ExecutionException, self.e.insertDataToPreProcess, "plop")

        #SUCCESS
            #insert with preprocess at top
        self.e.stack.append( (["a"], [0,2], PREPROCESS_INSTRUCTION, None, ) )
        self.e.insertDataToPreProcess("plip")
        self.assertEqual(self.e.stack[0][0], ["a","plip"])
        self.assertEqual(self.e.stack[0][1], [0,2])
        self.assertEqual(self.e.stack[0][2], PREPROCESS_INSTRUCTION)
        self.assertEqual(self.e.stack[0][3], None)

            #insert with anything else at top except preprocess
                #onlyForTheLinkedSubCmd = True
        self.e.stack.append( (["a"], [0,2], POSTPROCESS_INSTRUCTION, None, ) )
        self.e.insertDataToPreProcess("plop", True)

        self.assertEqual(self.e.stack[1][0], ["plop"])
        self.assertEqual(self.e.stack[1][1], [0,0])
        self.assertEqual(self.e.stack[1][2], PREPROCESS_INSTRUCTION)
        self.assertEqual(self.e.stack[1][3], [False, False, True, False])

                #onlyForTheLinkedSubCmd = False
        self.e.insertDataToPreProcess("plap", False)
        self.assertEqual(self.e.stack[0][0], ["a","plip","plap"])
        self.assertEqual(self.e.stack[0][1], [0,2])
        self.assertEqual(self.e.stack[0][2], PREPROCESS_INSTRUCTION)
        self.assertEqual(self.e.stack[0][3], None)

    #insertDataToProcess(self, data)
    def test_insertDataToProcess(self):
        #FAIL
            #empty stack
        del self.e.stack[:]
        self.assertRaises(ExecutionException, self.e.insertDataToProcess, "toto")

            #not postprocess on top
        self.e.stack.append( (["a"], [0,2,0,0], PROCESS_INSTRUCTION, None, ) )
        self.assertRaises(ExecutionException, self.e.insertDataToProcess, "toto")

            #not root path on top
        self.e.stack.append( (["a"], [0,1], PREPROCESS_INSTRUCTION, None, ) )
        self.assertRaises(ExecutionException, self.e.insertDataToProcess, "toto")

        #SUCCESS
            #success insert
        self.e.stack.append( (["a"], [0,0,0,0], POSTPROCESS_INSTRUCTION, None, ) )
        self.e.insertDataToProcess("toto")

        self.assertEqual(self.e.stack[2][0], ["toto"])
        self.assertEqual(self.e.stack[2][1], [0,0,0,0])
        self.assertEqual(self.e.stack[2][2], PROCESS_INSTRUCTION)
        self.assertEqual(self.e.stack[2][3], None)


    #insertDataToNextSubCommandPreProcess(self,data)
    def test_insertDataToNextSubCommandPreProcess(self):
        #FAIL
            #empty stack
        del self.e.stack[:]
        self.assertRaises(ExecutionException, self.e.insertDataToNextSubCommandPreProcess, "toto")

            #last sub cmd of a cmd on top
        self.e.stack.append( (["a"], [0,0,0,3], POSTPROCESS_INSTRUCTION, None, ) )
        self.assertRaises(ExecutionException, self.e.insertDataToNextSubCommandPreProcess, "toto")

        #SUCCESS
            #success insert
        self.e.stack.append( (["a"], [0,0,0,2], POSTPROCESS_INSTRUCTION, None, ) )
        self.e.insertDataToNextSubCommandPreProcess("toto")

        self.assertEqual(self.e.stack[0][0], ["toto"])
        self.assertEqual(self.e.stack[0][1], [0,0,0,0])
        self.assertEqual(self.e.stack[0][2], PREPROCESS_INSTRUCTION)
        self.assertEqual(self.e.stack[0][3], [False, False, False, True])


if __name__ == '__main__':
    unittest.main()
