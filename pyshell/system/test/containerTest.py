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
from pyshell.system.container import ParameterContainer

class ExceptionTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_(self):
        pass #TODO
        
    def test_ParameterContainer1(self):#pushVariableLevelForThisThread with empty stack + getCurrentProcedure
        pass #TODO
        
    def test_ParameterContainer2(self):#pushVariableLevelForThisThread with not empty stack + getCurrentProcedure
        pass #TODO
        
    def test_ParameterContainer3(self):#popVariableLevelForThisThread with empty stack
        pass #TODO
        
    def test_ParameterContainer4(self):#popVariableLevelForThisThread with one level on stack
        pass #TODO
        
    def test_ParameterContainer5(self):#popVariableLevelForThisThread with several level on stack
        pass #TODO
        
    def test_ParameterContainer6(self):#getCurrentId with empty stack
        pass #TODO
        
    def test_ParameterContainer7(self):#getCurrentId with one level on stack
        pass #TODO
        
    def test_ParameterContainer8(self):#getCurrentId with several level on stack
        pass #TODO
        
    def test_ParameterContainer9(self):#isMainThread with the current thread
        pass #TODO
        
    def test_ParameterContainer10(self):#isMainThread with another thread
        pass #TODO
        
    def test_ParameterContainer11(self):#getCurrentProcedure with empty stack
        pass #TODO
        
    def test_ParameterContainer12(self):#getCurrentProcedure with not empty stack
        pass #TODO
        
        
if __name__ == '__main__':
    unittest.main()
