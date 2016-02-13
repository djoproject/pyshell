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
from pyshell.command.utils import *

class EngineUtilsTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_equalPath(self):

        #different length
        path1 = [0,1]
        path2 = [0]

        equals, sameLength, equalsCount, path1IsHigher = equalPath(path1,path2)
        self.assertTrue(not equals and not sameLength and equalsCount == 1 and path1IsHigher is None)

        path2 = [0,1]
        path1 = [0]

        equals, sameLength, equalsCount, path1IsHigher = equalPath(path1,path2)
        self.assertTrue(not equals and not sameLength and equalsCount == 1 and path1IsHigher is None)


        #same path
        path1 = []
        path2 = []
        for i in range(1,5):
            path1.append(i)
            path2.append(i)

            equals, sameLength, equalsCount, path1IsHigher = equalPath(path1,path2)
            self.assertTrue(equals and sameLength and equalsCount == i and path1IsHigher is None)

        #same length but 2 is always higher
        path1 = []
        path2 = []
        for i in range(1,5):
            path1.append(i)
            path2.append(i+1)
            if len(path2) > 1:
                path2[-2] -= 1

            equals, sameLength, equalsCount, path1IsHigher = equalPath(path1,path2)
            self.assertTrue((not equals) and sameLength and equalsCount == (i-1) and (not path1IsHigher))

        #same length but 1 is always higher
        path1 = []
        path2 = []
        for i in range(1,5):
            path2.append(i)
            path1.append(i+1)
            if len(path1) > 1:
                path1[-2] -= 1

            equals, sameLength, equalsCount, path1IsHigher = equalPath(path1,path2)
            self.assertTrue((not equals) and sameLength and equalsCount == (i-1) and (path1IsHigher))

    def test_isAValidIndex(self):
        self.assertRaises(ExecutionException,isAValidIndex,[],43)
        self.assertRaises(ExecutionException,isAValidIndex,[],-25)
        self.assertRaises(ExecutionException,isAValidIndex,[],0)

        self.assertRaises(ExecutionException,isAValidIndex,[1,2,3,4,5],43)
        self.assertRaises(ExecutionException,isAValidIndex,[1,2,3,4,5],-25)
        self.assertRaises(ExecutionException,isAValidIndex,[1,2,3,4,5],5)
        self.assertRaises(ExecutionException,isAValidIndex,[1,2,3,4,5],-6)
        isAValidIndex([1,2,3,4,5], 4)
        isAValidIndex([1,2,3,4,5], -5)
        isAValidIndex([1,2,3,4,5], 0)

    def test_equalMap(self):
        self.assertTrue(equalMap(None,None))
        self.assertFalse(equalMap(None,[]))
        self.assertFalse(equalMap([],None))
        self.assertTrue(equalMap([],[]))

        self.assertFalse(equalMap([True,False,True],[False,True]))
        self.assertFalse(equalMap([True,False,True],[True,True,True]))

        self.assertTrue(equalMap([True,False,True],[True,False,True]))

    def test_isValidMap(self):
        self.assertTrue(isValidMap(None,123))
        self.assertFalse(isValidMap("",123))
        self.assertFalse(isValidMap(23,123))
        self.assertFalse(isValidMap(56.5,123))
        self.assertFalse(isValidMap(object(),123))

        self.assertFalse(isValidMap([1,2,3],123))
        self.assertTrue(isValidMap([True,True,True],3))
        self.assertFalse(isValidMap([1,2,3],3))
        self.assertFalse(isValidMap([True,True,True,42],4))

if __name__ == '__main__':
    unittest.main()
