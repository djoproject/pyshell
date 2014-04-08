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
 
    #TODO mergeDataAndSetEnablingMap
    #TODO mergeData
    
    #splitDataAndSetEnablingMap(self,itemToSplit = -1, splitAtDataIndex=0, map1 = None, map2=None)
    def test_splitWithSet(self):
        mc = MultiCommand("Multiple test")
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)
        
        engine = engineV3([mc,mc,mc])
        engine.appendData("11")
        engine.appendData("22")
        engine.appendData("33")
        engine.appendData("44")
        engine.appendData("55")
        
        #map1 != None with wrong size
        self.assertRaises(executionException, engine.splitDataAndSetEnablingMap, -1, 1, [True, False], None)
        
        #map1 != None with current index disabled
        self.assertRaises(executionException, engine.splitDataAndSetEnablingMap, -1, 1, [False, True, True], None)
        
        #map1 != None with wrong size
        self.assertRaises(executionException, engine.splitDataAndSetEnablingMap, -1, 1, None, [True, False])
        
        #map1 != None and fully disabled
        self.assertRaises(executionException, engine.splitDataAndSetEnablingMap, -1, 1, None, [False, False, False])
        
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
        
        engine = engineV3([mc,mc,mc])
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
        self.assertEqual(engine.stack[0][1],[2])
        
    
    #splitData(self, itemToSplit = -1,splitAtDataIndex=0, resetEnablingMap = False):
    def test_split(self):
        mc = MultiCommand("Multiple test")
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)
        
        engine = engineV3([mc,mc,mc])
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
        self.assertRaises(executionException, engine.splitData,-1, 1, False)
        engine.stack[0] = (engine.stack[0][0],engine.stack[0][1],0,engine.stack[0][3],)
        
        #invalid index
        self.assertRaises(executionException, engine.splitData,4000, 1, False)
        self.assertRaises(executionException, engine.splitData,-1, -4000, False)
        
        #normal split
        self.assertTrue(engine.splitData(-1, 1, False))
        self.assertEqual(engine.stack.size(),2)
        self.assertEqual(len(engine.stack[1][0]), 1)
        self.assertEqual(engine.stack[1][0][0], None)
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
        self.assertRaises(executionException, engine.splitData,-1, 1, False)
        
    def test_multiLevel(self):
        mc = MultiCommand("Multiple test")
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)

        for k in range(0, 5):
            engine = engineV3([mc,mc,mc])
            engine.stack.append( ([None],[0],0,None,)  )
            engine.stack.append( ([None],[0],0,None,)  )
            engine.stack.append( ([None],[0],0,None,)  )
            engine.stack.append( ([None],[0],0,None,)  )

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

            if k == 4:
                self.assertRaises(executionException, engine.splitData, k, 2, False)
                continue

            self.assertTrue(engine.splitData(k, 2, False))
            self.assertEqual(engine.stack.size(),6)

            for i in range(0,len(engine.stack)):
                if i < k:
                    self.assertEqual(len(engine.stack[i][0]), 6)
                    self.assertEqual(engine.stack[i][3], None)
                    for j in range(0,6):
                        if j == 0:
                            self.assertEqual(engine.stack[i][0][j], None )
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
                            self.assertEqual(engine.stack[i][0][j], None )
                            continue

                        self.assertEqual(engine.stack[i][0][j], (str(i)+str(j)) )

                else:
                    self.assertEqual(engine.stack[i][3], None)
                    self.assertEqual(len(engine.stack[i][0]), 6)
                    for j in range(0,6):
                        if j == 0:
                            self.assertEqual(engine.stack[i][0][j], None )
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
                        self.assertEqual(engine.stack[i][1], [1])
                        self.assertEqual(engine.stack[i+1][3],[False,True,True])
                        self.assertEqual(engine.stack[i+1][1], [0]) #initial value, not recomputed on split even if bitmap set to false
                    elif k == 2:
                        self.assertEqual(engine.stack[i][3],[True,False,True])
                        self.assertEqual(engine.stack[i][1], [0])
                        self.assertEqual(engine.stack[i+1][3],[True,False,True])
                        self.assertEqual(engine.stack[i+1][1], [0])
                    elif k == 3:
                        self.assertEqual(engine.stack[i][3],[False,False,True])
                        self.assertEqual(engine.stack[i][1], [2])
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
