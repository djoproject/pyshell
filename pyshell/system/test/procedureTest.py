#!/usr/bin/python
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
from pyshell.system.procedure import getAbsoluteIndex, Procedure, ProcedureFromList, ProcedureFromFile

class ProcedureTest(unittest.TestCase):
    def setUp(self):
        pass

    ## Misc ##
     
    def test_getAbsoluteIndex1(self):#getAbsoluteIndex, positiv value in the range
        self.assertEqual(getAbsoluteIndex(4,5),4)
        
    def test_getAbsoluteIndex2(self):#getAbsoluteIndex, positiv value out of range
        self.assertEqual(getAbsoluteIndex(23,5),23)
        
    def test_getAbsoluteIndex3(self):#getAbsoluteIndex, zero value
        self.assertEqual(getAbsoluteIndex(0,5),0)
        
    def test_getAbsoluteIndex4(self):#getAbsoluteIndex, negativ value in the range
        self.assertEqual(getAbsoluteIndex(-3,5),2)
        
    def test_getAbsoluteIndex5(self):#getAbsoluteIndex, negativ value out of range
        self.assertEqual(getAbsoluteIndex(-23,5),0)
    
    ## TODO Procedure ##
    
    ## TODO ProcedureFromList ##
    
    ## TODO ProcedureFromFile ##
        
if __name__ == '__main__':
    unittest.main()
