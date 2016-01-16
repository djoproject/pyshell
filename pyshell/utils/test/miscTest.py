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

import unittest, os, shutil, tempfile
from pyshell.utils.misc import raiseIfInvalidKeyList, createParentDirectory
from pyshell.utils.exception import DefaultPyshellException

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

class MiscTest(unittest.TestCase):
    def setUp(self):
        pass 
        
    def test_raiseIfInvalidKeyList1(self):
        self.assertRaises(DefaultPyshellException, raiseIfInvalidKeyList, "toto", DefaultPyshellException, "package", "method" )
        
    def test_raiseIfInvalidKeyList2(self):
        self.assertRaises(DefaultPyshellException, raiseIfInvalidKeyList,  ("toto", "tata", u"titi", 42), DefaultPyshellException, "package", "method")
    
    def test_raiseIfInvalidKeyList3(self):
        self.assertRaises(DefaultPyshellException, raiseIfInvalidKeyList,  ("toto", "tata", u"titi", ""), DefaultPyshellException, "package", "method")
        
    def test_raiseIfInvalidKeyList4(self):
        self.assertEqual(raiseIfInvalidKeyList( ("toto", "tata", u"titi",), DefaultPyshellException, "package", "method" ), ("toto", "tata", u"titi",))
        
    def test_createParentDirectory1(self):
        filePath = tempfile.gettempdir() + os.sep + "plop.txt"
        self.assertTrue(os.path.exists(tempfile.gettempdir()))
        self.assertFalse(os.path.exists(filePath))
        createParentDirectory(filePath)
        self.assertTrue(os.path.exists(tempfile.gettempdir()))
        self.assertFalse(os.path.exists(filePath))
        
    def test_createParentDirectory2(self):
        shutil.rmtree( tempfile.gettempdir() + os.sep + "toto", True )
        
        path = os.sep.join( ("toto","tata","titi","test.txt") )
        path = tempfile.gettempdir() + os.sep + path
        
        self.assertFalse(os.path.exists(os.path.dirname(path)))
        self.assertFalse(os.path.exists(path))
        
        createParentDirectory(path)
        
        self.assertTrue(os.path.exists(os.path.dirname(path)))
        self.assertFalse(os.path.exists(path))
        
        shutil.rmtree( tempfile.gettempdir() + os.sep + "toto", True )
        
    def test_createParentDirectory3(self):
        shutil.rmtree( tempfile.gettempdir() + os.sep + "toto", True )
        os.makedirs(tempfile.gettempdir() + os.sep + "toto")
        touch(tempfile.gettempdir() + os.sep + "toto" + os.sep + "plop")
        self.assertRaises(DefaultPyshellException, createParentDirectory, tempfile.gettempdir() + os.sep + "toto" + os.sep + "plop" + os.sep + "test.txt")
        shutil.rmtree( tempfile.gettempdir() + os.sep + "toto", True )
    
if __name__ == '__main__':
    unittest.main()
