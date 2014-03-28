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
        self.push(1,2,3,4)
        self.assertTrue(self.stack[0][0] == 1)
        self.assertTrue(self.stack[0][1] == 2)
        self.assertTrue(self.stack[0][2] == 3)
        self.assertTrue(self.stack[0][3] == 4)
        self.stack.raiseIfEmpty()
        self.stack.raiseIfEmpty("plop")
        self.assertTrue(self.stack.size() == 1)
        self.assertFalse(self.stack.isEmpty())
        self.assertTrue(self.stack.isLastStackItem())
        
        self.push(5,6,7)
        self.assertTrue(self.stack[-1][0] == 5)
        self.assertTrue(self.stack[-1][1] == 6)
        self.assertTrue(self.stack[-1][2] == 7)
        self.assertTrue(self.stack[-1][3] == None)
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
        
        self.stack.getCmd(0)
        self.stack.subCmdLength(0)
        self.stack.subCmdIndex(0)
        
    def test_methMapper(self):
        pass

if __name__ == '__main__':
    unittest.main()
