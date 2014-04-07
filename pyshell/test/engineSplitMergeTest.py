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
    pass
    
    #TODO mergeDataAndSetEnablingMap
    #TODO mergeData
    #TODO splitDataAndSetEnablingMap
    
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

            engine = engineV3([mc,mc,mc])
            engin.stack.append( ([None],[0],0,None,)  )
            engin.stack.append( ([None],[0],0,None,)  )
            engin.stack.append( ([None],[0],0,None,)  )
            engin.stack.append( ([None],[0],0,None,)  )

            for i in range(0,len(engine.stack)):
                for j in range(1,6):
                    engine.stack[i][0].append(str(i+1)+str(j))

            
        
            
        #TODO test to do
            #pile avec plus de 1 element
            #split avec un index au debut, a la fin, et un au millieu de pile
            #tester le recalcul d'index avecun bitmap


                
    
if __name__ == '__main__':
    unittest.main()
