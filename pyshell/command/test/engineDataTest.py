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
from pyshell.command.engine import *
from pyshell.command.command import *

def noneFun():
    pass

class dataTest(unittest.TestCase):
    def setUp(self):
        self.mc = MultiCommand()
        self.mc.addProcess(noneFun,noneFun,noneFun)

    #flushData
    def test_flushData(self):
        e = EngineV3([self.mc],[[]], [[{},{},{}]])
        e.flushData()
        self.assertIs(len(e.stack[0][0]),0)

        e.addData(11)
        e.addData(12)
        e.addData(13)
        self.assertIs(len(e.stack[0][0]),3)
        e.flushData()
        self.assertIs(len(e.stack[0][0]),0)

        del e.stack[:]
        self.assertRaises(ExecutionException,e.flushData)

    #appendData
    def test_append(self):
        e = EngineV3([self.mc],[[]], [[{},{},{}]])

        e.appendData(11)
        e.appendData(12)
        e.appendData(13)

        self.assertIs(len(e.stack[0][0]),4)
        self.assertIs(e.stack[0][0][0],EMPTY_DATA_TOKEN)
        self.assertIs(e.stack[0][0][1],11)
        self.assertIs(e.stack[0][0][2],12)
        self.assertIs(e.stack[0][0][3],13)

        del e.stack[:]
        self.assertRaises(ExecutionException,e.appendData,42)

    #addData
    def test_addData(self):
        e = EngineV3([self.mc],[[]], [[{},{},{}]])
        self.assertRaises(ExecutionException,e.addData, 33, 0)

        #regular addData
        e.addData(33,0,False)
        self.assertIs(len(e.stack[0][0]),2)
        self.assertIs(e.stack[0][0][0],33)
        self.assertIs(e.stack[0][0][1],EMPTY_DATA_TOKEN)

        e.addData(44)
        self.assertIs(len(e.stack[0][0]),3)
        self.assertIs(e.stack[0][0][0],33)
        self.assertIs(e.stack[0][0][1],44)
        self.assertIs(e.stack[0][0][2],EMPTY_DATA_TOKEN)

        del e.stack[:]
        self.assertRaises(ExecutionException,e.addData, 33)

    #removeData
    def test_removeData(self):
        e = EngineV3([self.mc],[[]], [[{},{},{}]])
        self.assertRaises(ExecutionException,e.removeData, -2)
        self.assertRaises(ExecutionException,e.removeData, 1)

        e.removeData()
        self.assertIs(len(e.stack[0][0]),0)
        self.assertIs(e.stack[0][1][-1],0)

        e.addData(None)
        e.addData(44)
        e.addData(55)

        e.removeData(1)
        self.assertIs(len(e.stack[0][0]),2)
        self.assertIs(e.stack[0][1][-1],0)
        self.assertIs(e.stack[0][0][1],None)
        self.assertIs(e.stack[0][0][0],44)

        e.flushData()
        e.addData(None)
        e.addData(44)
        e.addData(55)

        e.removeData(-2)
        self.assertIs(len(e.stack[0][0]),2)
        self.assertIs(e.stack[0][1][-1],0)
        self.assertIs(e.stack[0][0][1],None)
        self.assertIs(e.stack[0][0][0],44)

        del e.stack[:]
        self.assertRaises(ExecutionException,e.removeData)

    #setData
    #getData
    def test_getData(self):
        e = EngineV3([self.mc],[[]], [[{},{},{}]])

        self.assertEqual(e.getData(), EMPTY_DATA_TOKEN)
        e.setData(32)
        self.assertEqual(e.getData(), 32)
        e.setData(None)
        self.assertEqual(e.getData(), None)

        del e.stack[:]
        self.assertRaises(ExecutionException,e.getData)
        self.assertRaises(ExecutionException,e.setData, 33)

    #hasNextData
    def test_hasNextData(self):
        e = EngineV3([self.mc],[[]], [[{},{},{}]])

        self.assertFalse(e.hasNextData())
        e.addData(11)
        self.assertTrue(e.hasNextData())

        del e.stack[:]
        self.assertRaises(ExecutionException,e.hasNextData)

    #getRemainingDataCount
    def test_getRemainingDataCount(self):
        e = EngineV3([self.mc],[[]], [[{},{},{}]])

        self.assertEqual(e.getRemainingDataCount(), 0)
        e.addData(11)
        self.assertEqual(e.getRemainingDataCount(), 1)
        e.addData(12)
        e.addData(13)
        e.addData(14)
        e.addData(15)
        self.assertEqual(e.getRemainingDataCount(), 5)

        del e.stack[:]
        self.assertRaises(ExecutionException,e.getRemainingDataCount)

    #getDataCount
    def test_getDataCount(self):
        e = EngineV3([self.mc],[[]], [[{},{},{}]])

        self.assertEqual(e.getDataCount(), 1)
        e.addData(11)
        self.assertEqual(e.getDataCount(), 2)
        e.addData(12)
        e.addData(13)
        e.addData(14)
        e.addData(15)
        self.assertEqual(e.getDataCount(), 6)

        del e.stack[:]
        self.assertRaises(ExecutionException,e.getDataCount)

if __name__ == '__main__':
    unittest.main()
