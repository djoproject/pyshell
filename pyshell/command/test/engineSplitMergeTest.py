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

@shellMethod(arg=ArgChecker())
def plop(arg):
    return arg

class splitAndMergeTest(unittest.TestCase):

    #mergeDataAndSetEnablingMap(self,toppestItemToMerge = -1, new_map = None, count = 2):
    def test_mergeWithCustomeMap(self):
        mc = MultiCommand()
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)

        engine = EngineV3([mc,mc,mc], [[],[],[]], [[{},{},{}], [{},{},{}],[{},{},{}]])

        #FAIL
        #empty stack
        del engine.stack[:]
        self.assertRaises(ExecutionException,engine.mergeDataAndSetEnablingMap,-1,None,2)

        for i in range(0,5):
            engine.stack.append( ([None],[0],0,None,)  )
        for i in range(0,len(engine.stack)):
            for j in range(1,6):
                engine.stack[i][0].append(str(i+1)+str(j))

        #set a map of invalid length
        self.assertRaises(ExecutionException,engine.mergeDataAndSetEnablingMap,-1,[True, True, True, True],2)

        #set a map of valid length but with the current subcmd disabled
        self.assertRaises(ExecutionException,engine.mergeDataAndSetEnablingMap,-1,[False, True, True],2)

        #SUCCESS
        #set a None map on a not None map merged
        del engine.stack[:]

        for i in range(0,5):
            engine.stack.append( ([None],[0],0,[True, False, True],)  )
        for i in range(0,len(engine.stack)):
            for j in range(1,6):
                engine.stack[i][0].append(str(i+1)+str(j))

        engine.mergeDataAndSetEnablingMap(-1,None,2)
        self.assertEqual(engine.stack[-1][3], None)

        #set a instanciated map
        del engine.stack[:]
        for i in range(0,5):
            engine.stack.append( ([None],[0],0,None,)  )
        for i in range(0,len(engine.stack)):
            for j in range(1,6):
                engine.stack[i][0].append(str(i+1)+str(j))

        engine.mergeDataAndSetEnablingMap(-1,[True, False, True],2)
        self.assertEqual(engine.stack[-1][3], [True, False, True])

    #def mergeData(self,toppestItemToMerge = -1, count = 2, depthOfTheMapToKeep = None)
    def test_basicMerge(self):
        mc = MultiCommand()
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)

        engine = EngineV3([mc,mc,mc], [[],[],[]], [[{},{},{}], [{},{},{}],[{},{},{}]])
        for i in range(0,4):
            engine.stack.append( ([None],[0],0,None,)  )

        for i in range(0,len(engine.stack)):
            for j in range(1,6):
                engine.stack[i][0].append(str(i+1)+str(j))

        #FAIL
        #count < 2
        self.assertFalse(engine.mergeData(-1,1,None))
        self.assertFalse(engine.mergeData(0,0,None))

        #toppestItemToMerge invalid
        self.assertRaises(ExecutionException, engine.mergeData,-100,4,None)

        #count with more to merge than available
        self.assertRaises(ExecutionException, engine.mergeData,-1,400,None)

        #merge pro/post process
            #at the top or in the middle
        del engine.stack[:]
        for i in range(0,5):
            engine.stack.append( ([None],[0],i%3,None,)  )
        self.assertRaises(ExecutionException, engine.mergeData,-1,3,None)
        del engine.stack[:]
        for i in range(0,5):
            engine.stack.append( ([None],[0],0,None,)  )

        #select a map outside of the scope
        self.assertRaises(ExecutionException, engine.mergeData,-1,2,[True,False,True,False])

        #select a map without the current process included
        self.assertRaises(ExecutionException, engine.mergeData,-1,2,[False,False,True])

        #try to merge some preprocess with different path
        del engine.stack[:]
        for i in range(0,5):
            engine.stack.append( ([None],[0]*(i+1),i%3,None,)  )
            #path of same length but different
        self.assertRaises(ExecutionException, engine.mergeData,-1,2,None)

        del engine.stack[:]
        for i in range(0,5):
            engine.stack.append( ([None],[i%2, i%3, i*2],i%3,None,)  )
            #path with a different length
        self.assertRaises(ExecutionException, engine.mergeData,-1,2,None)

        #empty stack
        del engine.stack[:]
        self.assertRaises(ExecutionException, engine.mergeData,-1,2,None)



        #SUCCESS
        #try normal merge
            #with or without selected map
        for k in range(1,5):
            #reinit
            del engine.stack[:]
            for i in range(0,5):
                engine.stack.append( ([None],[0],0,None,)  )
            for i in range(0,len(engine.stack)):
                for j in range(1,6):
                    engine.stack[i][0].append(str(i+1)+str(j))

            engine.mergeData(k,2,None)
            for i in range(0,k-1):
                self.assertEqual(len(engine.stack[i][0]),6)

            self.assertEqual(len(engine.stack[k-1][0]),12)

            for i in range(k,4):
                self.assertEqual(len(engine.stack[i][0]),6)


        for k in range(2,5):
            #reinit
            del engine.stack[:]
            for i in range(0,5):
                engine.stack.append( ([None],[0],0,None,)  )
            for i in range(0,len(engine.stack)):
                for j in range(1,6):
                    engine.stack[i][0].append(str(i+1)+str(j))

            engine.mergeData(k,3,None)
            for i in range(0,k-2):
                self.assertEqual(len(engine.stack[i][0]),6)

            self.assertEqual(len(engine.stack[k-2][0]),18)

            for i in range(k-1,3):
                self.assertEqual(len(engine.stack[i][0]),6)

    #splitDataAndSetEnablingMap(self,itemToSplit = -1, splitAtDataIndex=0, map1 = None, map2=None)
    def test_splitWithSet(self):
        mc = MultiCommand()
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)

        engine = EngineV3([mc,mc,mc], [[],[],[]], [[{},{},{}], [{},{},{}],[{},{},{}]])
        engine.appendData("11")
        engine.appendData("22")
        engine.appendData("33")
        engine.appendData("44")
        engine.appendData("55")

        #map1 is not None with wrong size
        self.assertRaises(ExecutionException, engine.splitDataAndSetEnablingMap, -1, 1, [True, False], None)

        #map1 is not None with current index disabled
        self.assertRaises(ExecutionException, engine.splitDataAndSetEnablingMap, -1, 1, [False, True, True], None)

        #map1 is not None with wrong size
        self.assertRaises(ExecutionException, engine.splitDataAndSetEnablingMap, -1, 1, None, [True, False])

        #map1 is not None and fully disabled
        self.assertRaises(ExecutionException, engine.splitDataAndSetEnablingMap, -1, 1, None, [False, False, False])

        #split at 0 index
        self.assertEqual(engine.stack.size(),1)
        engine.splitDataAndSetEnablingMap( 0, 0, None, None)
        self.assertEqual(engine.stack.size(),1)
        self.assertEqual(engine.stack[0][3], None)
        self.assertEqual(engine.stack[0][1],[0])


        #split at >0 index
        self.assertEqual(engine.stack.size(),1)
        engine.splitDataAndSetEnablingMap( 0, 2, None, None)
        self.assertEqual(engine.stack.size(),2)

        self.assertEqual(engine.stack[0][3], None)
        self.assertEqual(engine.stack[1][3], None)

        self.assertEqual(engine.stack[1][1],[0])
        self.assertEqual(engine.stack[0][1],[0])

        engine = EngineV3([mc,mc,mc], [[],[],[]], [[{},{},{}], [{},{},{}],[{},{},{}]])
        engine.appendData("11")
        engine.appendData("22")
        engine.appendData("33")
        engine.appendData("44")
        engine.appendData("55")

        #split at 0 index with new map
        self.assertEqual(engine.stack.size(),1)
        engine.splitDataAndSetEnablingMap( 0, 0, [True, False, False], [False, False,True])
        self.assertEqual(engine.stack.size(),1)
        self.assertEqual(engine.stack[0][3], [True, False, False])
        self.assertEqual(engine.stack[0][1],[0])

        #split at >0 index with new map
        self.assertEqual(engine.stack.size(),1)
        engine.splitDataAndSetEnablingMap( 0, 2, [True, False, True], [False, False,True])
        self.assertEqual(engine.stack.size(),2)
        self.assertEqual(engine.stack[1][3], [True, False, True])
        self.assertEqual(engine.stack[0][3], [False, False, True])
        self.assertEqual(engine.stack[1][1],[0])
        self.assertEqual(engine.stack[0][1],[0])

    #splitData(self, itemToSplit = -1,splitAtDataIndex=0, resetEnablingMap = False):
    def test_split(self):
        mc = MultiCommand()
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)

        engine = EngineV3([mc,mc,mc], [[],[],[]], [[{},{},{}], [{},{},{}],[{},{},{}]])
        engine.appendData("11")
        engine.appendData("22")
        engine.appendData("33")
        engine.appendData("44")
        engine.appendData("55")

        #split at 0 index
        self.assertFalse(engine.splitData(-1, 0, False))
        self.assertEqual(engine.stack.size(),1)

        #split on pro/post
        engine.stack[0] = (engine.stack[0][0],engine.stack[0][1],2,engine.stack[0][3],)
        self.assertRaises(ExecutionException, engine.splitData,-1, 1, False)
        engine.stack[0] = (engine.stack[0][0],engine.stack[0][1],0,engine.stack[0][3],)

        #invalid index
        self.assertRaises(ExecutionException, engine.splitData,4000, 1, False)
        self.assertRaises(ExecutionException, engine.splitData,-1, -4000, False)

        #normal split
        self.assertTrue(engine.splitData(-1, 1, False))
        self.assertEqual(engine.stack.size(),2)
        self.assertEqual(len(engine.stack[1][0]), 1)
        self.assertEqual(engine.stack[1][0][0], EMPTY_DATA_TOKEN)
        self.assertEqual(len(engine.stack[0][0]), 5)
        #print engine.printStack()
        for i in range(1,6):
            self.assertEqual(engine.stack[0][0][i-1], str(i)+str(i))
        self.assertEqual(engine.stack[1][1], [0])
        self.assertEqual(engine.stack[0][1], [0])
        self.assertEqual(engine.stack[1][2], 0)
        self.assertEqual(engine.stack[0][2], 0)
        self.assertEqual(engine.stack[1][3], None)
        self.assertEqual(engine.stack[0][3], None)

        #empty stack
        del engine.stack[:]
        self.assertRaises(ExecutionException, engine.splitData,-1, 1, False)

    def test_multiLevel(self):
        mc = MultiCommand()
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)

        for k in range(0, 5):
            engine = EngineV3([mc,mc,mc], [[],[],[]], [[{},{},{}], [{},{},{}],[{},{},{}]])
            engine.stack.append( ([EMPTY_DATA_TOKEN],[0],0,None,)  )
            engine.stack.append( ([EMPTY_DATA_TOKEN],[0],0,None,)  )
            engine.stack.append( ([EMPTY_DATA_TOKEN],[0],0,None,)  )
            engine.stack.append( ([EMPTY_DATA_TOKEN],[0],0,None,)  )

            if k==0:
                tab = [True,True,True]
            elif k == 1:
                tab = [False,True,True]
            elif k == 2:
                tab = [True,False,True]
            elif k == 3:
                tab = [False,False,True]
            else:#if k == 4:
                tab = [False,False,False]

            engine.stack.setEnableMapOnIndex(k,tab)

            for i in range(0,len(engine.stack)):
                for j in range(1,6):
                    engine.stack[i][0].append(str(i+1)+str(j))

            self.assertEqual(engine.stack.size(),5)

            #if k == 4:
            #    self.assertRaises(ExecutionException, engine.splitData, k, 2, False)
            #    continue

            self.assertTrue(engine.splitData(k, 2, False))
            self.assertEqual(engine.stack.size(),6)

            for i in range(0,len(engine.stack)):
                if i < k:
                    self.assertEqual(len(engine.stack[i][0]), 6)
                    self.assertEqual(engine.stack[i][3], None)
                    for j in range(0,6):
                        if j == 0:
                            self.assertEqual(engine.stack[i][0][j], EMPTY_DATA_TOKEN )
                            continue

                            self.assertEqual(engine.stack[i][0][j], (str(i+1)+str(j)) )

                elif k == i:
                    self.assertEqual(len(engine.stack[i][0]), 4)
                    for j in range(2,6):
                        self.assertEqual(engine.stack[i][0][j-2], (str(i+1)+str(j)) )

                elif k+1 == i:
                    self.assertEqual(len(engine.stack[i][0]), 2)
                    for j in range(0,2):
                        if j == 0:
                            self.assertEqual(engine.stack[i][0][j], EMPTY_DATA_TOKEN )
                            continue

                        self.assertEqual(engine.stack[i][0][j], (str(i)+str(j)) )

                else:
                    self.assertEqual(engine.stack[i][3], None)
                    self.assertEqual(len(engine.stack[i][0]), 6)
                    for j in range(0,6):
                        if j == 0:
                            self.assertEqual(engine.stack[i][0][j], EMPTY_DATA_TOKEN )
                            continue

                        self.assertEqual(engine.stack[i][0][j], (str(i)+str(j)) )

                if k == i:
                    if k==0:
                        self.assertEqual(engine.stack[i][3],[True,True,True])
                        self.assertEqual(engine.stack[i][1], [0])
                        self.assertEqual(engine.stack[i+1][3],[True,True,True])
                        self.assertEqual(engine.stack[i+1][1], [0])
                    elif k == 1:
                        self.assertEqual(engine.stack[i][3],[False,True,True])
                        self.assertEqual(engine.stack[i][1], [0])
                        self.assertEqual(engine.stack[i+1][3],[False,True,True])
                        self.assertEqual(engine.stack[i+1][1], [0]) #initial value, not recomputed on split even if bitmap set to false
                    elif k == 2:
                        self.assertEqual(engine.stack[i][3],[True,False,True])
                        self.assertEqual(engine.stack[i][1], [0])
                        self.assertEqual(engine.stack[i+1][3],[True,False,True])
                        self.assertEqual(engine.stack[i+1][1], [0])
                    elif k == 3:
                        self.assertEqual(engine.stack[i][3],[False,False,True])
                        self.assertEqual(engine.stack[i][1], [0])
                        self.assertEqual(engine.stack[i+1][3],[False,False,True])
                        self.assertEqual(engine.stack[i+1][1], [0]) #initial value, not recomputed on split even if bitmap set to false
                    else:#if k == 4:
                        self.assertEqual(engine.stack[i][3],[False,False,False])
                        self.assertEqual(engine.stack[i][1], [0])
                        self.assertEqual(engine.stack[i+1][3],[False,False,False])
                        self.assertEqual(engine.stack[i+1][1], [0])

                self.assertEqual(engine.stack[i][2], 0)


if __name__ == '__main__':
    unittest.main()
