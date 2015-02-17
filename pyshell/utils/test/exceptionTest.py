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
from pyshell.utils.exception import ListOfException


class ExceptionTest(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_emptyListOfException(self):
        l = ListOfException()
        self.assertFalse(l.isThrowable())
        self.assertEqual(str(l),"no error, this exception shouldn't be throwed")
        
    def test_invalidException(self):
        l = ListOfException()
        self.assertRaises(Exception,l.addException, ("plop",))
        
    def test_addOneException(self):
        l = ListOfException()
        l.addException(Exception("plop"))
        self.assertEqual(len(l.exceptions),1)
        
    def test_addSeveralExceptions(self):
        l = ListOfException()
        l.addException(Exception("plop"))
        l.addException(Exception("plip"))
        
        self.assertEqual(len(l.exceptions),2)
        
        l2 = ListOfException()
        l2.addException(l)
        
        self.assertEqual(len(l2.exceptions),2)
        

if __name__ == '__main__':
    unittest.main()
