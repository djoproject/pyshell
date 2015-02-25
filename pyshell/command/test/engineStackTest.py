#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.command.stackEngine import *
from pyshell.command.exception import *

class EngineStackTest(unittest.TestCase):
    def setUp(self):
        self.stack = engineStack()

    def test_insert(self):
        self.assertTrue(self.stack.size() == 0)
        self.assertTrue(self.stack.isEmpty())
        self.assertFalse(self.stack.isLastStackItem())
        self.assertRaises(executionException, self.stack.raiseIfEmpty)
        self.assertRaises(executionException, self.stack.raiseIfEmpty,"plop")
        self.stack.push(1,2,3,4)
        self.assertEqual(self.stack[0][0],1)
        self.assertEqual(self.stack[0][1],2)
        self.assertEqual(self.stack[0][2],3)
        self.assertEqual(self.stack[0][3],4)
        self.stack.raiseIfEmpty()
        self.stack.raiseIfEmpty("plop")
        self.assertTrue(self.stack.size() == 1)
        self.assertFalse(self.stack.isEmpty())
        self.assertTrue(self.stack.isLastStackItem())
        
        self.stack.push(5,6,7)
        self.assertTrue(self.stack[-1][0] == 5)
        self.assertTrue(self.stack[-1][1] == 6)
        self.assertTrue(self.stack[-1][2] == 7)
        self.assertTrue(self.stack[-1][3] is None)
        self.stack.raiseIfEmpty()
        self.stack.raiseIfEmpty("plop")
        self.assertTrue(self.stack.size() == 2)
        self.assertFalse(self.stack.isEmpty())
        self.assertFalse(self.stack.isLastStackItem())
        
    def test_basicMeth(self):
        self.stack.push(["a"], [1,2], 2, [True,False])
        self.assertTrue(len(self.stack.data(0)) == 1 and self.stack.data(0)[0] == "a")
        self.assertTrue(len(self.stack.path(0)) == 2 and self.stack.path(0)[0] == 1 and self.stack.path(0)[1] == 2)
        self.assertTrue(self.stack.type(0) == 2)
        self.assertTrue(len(self.stack.enablingMap(0)) == 2 and self.stack.enablingMap(0)[0] and not self.stack.enablingMap(0)[1])
        self.assertTrue(self.stack.cmdIndex(0) == 1)
        self.assertTrue(self.stack.cmdLength(0) == 2)
        self.assertTrue(self.stack.item(0) == self.stack[0])
        cmdList = [[1,2,3,4],[5,6,7],[8,9]]
        self.assertEqual(self.stack.getCmd(0, cmdList), cmdList[1])
        self.assertEqual(self.stack.subCmdLength(0,cmdList), 3)
        self.assertEqual(self.stack.subCmdIndex(0), 2)
    
    def test_basicMethWithSuffix(self):
        self.stack.push(["a", "b"], [0,1], 0, [True,False])
        self.stack.push(["b","c", "d"], [1,2], 1, [True,False,True])
        self.stack.push(["c", "d", "e", "f"], [2,3], 2, [True,False, True, False])
        self.stack.push(["d", "e", "f", "g", "h"], [3,4,5], 3, [True,False, True, False, True])
        self.stack.push(["e", "f", "g", "h", "i", "j"], [4,5,6], 4, [True,False, True, False, True, False])

        cmdList = [[1,2,3,4,5],[5,6,7],[8,9]]
        letter  = ["a","b","c", "d","e", "f", "g", "h", "i", "j"]

        for i in range(0,5):
            dept = len(self.stack) - 1 - i

            #DATA
            dataI = self.stack.dataOnIndex(i)
            dataD = self.stack.dataOnDepth(dept)
            dataT = self.stack.dataOnTop()
            self.assertEqual(len(dataI), i+2)
            self.assertEqual(len(dataD), i+2)
            self.assertTrue(len(dataT), 6)
            for j in range(0,len(dataI)):
                self.assertEqual(dataI[j], letter[j+i])
                self.assertEqual(dataD[j], letter[j+i])
                self.assertEqual(dataT[j], letter[j+4])
            
            #PATH
            pathI = self.stack.pathOnIndex(i)
            pathD = self.stack.pathOnDepth(dept)
            pathT = self.stack.pathOnTop()

            if i < 3:
                self.assertEqual(len(pathI), 2)
                self.assertEqual(len(pathD), 2)
                self.assertEqual(self.stack.cmdIndexOnIndex(i),1)
                self.assertEqual(self.stack.cmdIndexOnDepth(dept),1)

                self.assertEqual(self.stack.subCmdLengthOnIndex(i,cmdList), 3)
                self.assertEqual(self.stack.subCmdLengthOnDepth(dept,cmdList), 3)

                self.assertEqual(self.stack.subCmdIndexOnIndex(i), i+1)
                self.assertEqual(self.stack.subCmdIndexOnDepth(dept), i+1)

                self.assertTrue(self.stack.cmdLengthOnIndex(i) == 2)
                self.assertTrue(self.stack.cmdLengthOnDepth(dept) == 2)

                self.assertEqual(self.stack.getCmdOnIndex(i, cmdList), cmdList[1])
                self.assertEqual(self.stack.getCmdOnDepth(dept, cmdList), cmdList[1])
            else:
                self.assertEqual(len(pathI), 3)
                self.assertEqual(len(pathD), 3)
                self.assertEqual(self.stack.cmdIndexOnIndex(i),2)
                self.assertEqual(self.stack.cmdIndexOnDepth(dept),2)

                self.assertEqual(self.stack.subCmdLengthOnIndex(i,cmdList), 2)
                self.assertEqual(self.stack.subCmdLengthOnDepth(dept,cmdList), 2)

                self.assertEqual(self.stack.subCmdIndexOnIndex(i), i+2)
                self.assertEqual(self.stack.subCmdIndexOnDepth(dept), i+2)

                self.assertTrue(self.stack.cmdLengthOnIndex(i) == 3)
                self.assertTrue(self.stack.cmdLengthOnDepth(dept) == 3)

                self.assertEqual(self.stack.getCmdOnIndex(i, cmdList), cmdList[2])
                self.assertEqual(self.stack.getCmdOnDepth(dept, cmdList), cmdList[2])

            self.assertEqual(self.stack.getCmdOnTop(cmdList), cmdList[2])
            self.assertTrue(self.stack.cmdLengthOnTop() == 3)
            self.assertEqual(self.stack.subCmdIndexOnTop(), 6)
            self.assertEqual(self.stack.cmdIndexOnTop(),2)
            self.assertEqual(self.stack.subCmdLengthOnTop(cmdList), 2)
            self.assertEqual(len(pathT), 3)
            for j in range(0,len(pathI)):
                self.assertEqual(j+i, pathI[j])
                self.assertEqual(j+i, pathD[j])

            for j in range(0,3):
                self.assertEqual(j+4, pathT[j])

            #TYPE
            self.assertTrue(self.stack.typeOnIndex(i) == i)
            self.assertTrue(self.stack.typeOnDepth(dept) == i)
            self.assertTrue(self.stack.typeOnTop() == 4)

            #ITEM
            self.assertTrue(self.stack.itemOnIndex(i) == self.stack[i])
            self.assertTrue(self.stack.itemOnDepth(dept) == self.stack[i])
            self.assertTrue(self.stack.itemOnTop() == self.stack[-1])

            #MAP
            mapI = self.stack.enablingMapOnIndex(i)
            mapD = self.stack.enablingMapOnDepth(dept)
            mapT = self.stack.enablingMapOnTop()

            self.assertEqual(len(mapI), i+2)
            self.assertEqual(len(mapD), i+2)
            self.assertEqual(len(mapT), 6)

            for i in range(0,i+1):
                if i%2 == 1:
                    self.assertFalse(mapI[i])
                    self.assertFalse(mapD[i])
                else:
                    self.assertTrue(mapI[i])
                    self.assertTrue(mapD[i])

            for i in range(0,6):
                if i%2 == 1:
                    self.assertFalse(mapT[i])
                else:
                    self.assertTrue(mapT[i])

    def test_methMapper(self):
        self.assertRaises(executionException, self.stack.__getattr__,"totoOnIndex")

if __name__ == '__main__':
    unittest.main()
