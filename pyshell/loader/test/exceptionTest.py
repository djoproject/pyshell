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
from pyshell.loader.exception import LoadException, RegisterException

def raise_LoadException():
    raise LoadException("plop")
    
def raise_RegisterException():
    raise RegisterException("plip")

class ExceptionTest(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_RegisterException(self):
        self.assertRaises(RegisterException, raise_RegisterException)
        
    def test_LoadException(self):
        self.assertRaises(LoadException, raise_LoadException)
        
if __name__ == '__main__':
    unittest.main()
