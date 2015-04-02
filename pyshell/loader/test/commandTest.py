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
from pyshell.loader.command import _local_getAndInitCallerModule, registerSetGlobalPrefix, registerSetTempPrefix, registerResetTempPrefix, registerAnInstanciatedCommand, registerCommand, registerAndCreateEmptyMultiCommand, registerStopHelpTraversalAt, CommandLoader
from pyshell.loader.utils import GlobalLoader

def loader(profile=None):
    return _local_getAndInitCallerModule(profile)

class CommandTest(unittest.TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        global _loaders
        if "_loaders" in globals():
            del _loaders
        
    ## _local_getAndInitCallerModule ##
    
    def test_local_getAndInitCallerModule1(self):#_local_getAndInitCallerModule with None profile
        global _loaders
        self.assertFalse("_loaders" in globals())
        a = loader()
        self.assertTrue("_loaders" in globals())
        self.assertIsInstance(_loaders, GlobalLoader)
        b = loader()
        self.assertIs(a,b)
        self.assertIsInstance(a,CommandLoader)
        
    def test_local_getAndInitCallerModule2(self):#_local_getAndInitCallerModule withouth None profile
        global _loaders
        self.assertFalse("_loaders" in globals())
        a = loader("plop")
        self.assertTrue("_loaders" in globals())
        self.assertIsInstance(_loaders, GlobalLoader)
        b = loader("plop")
        c = loader()
        self.assertIs(a,b)
        self.assertIsNot(a,c)
        self.assertIsInstance(a,CommandLoader)
        self.assertIsInstance(c,CommandLoader)
        
    ## registering ## TODO test every method with profile set to None and profile not set to None
    
        #registerSetGlobalPrefix with invalid keyList
        #registerSetGlobalPrefix with valid keyList
        
        #registerSetTempPrefix with invalid keyList
        #registerSetTempPrefix with valid keyList
        
        #registerResetTempPrefix with temp prefix set
        #registerResetTempPrefix without temp prefix set
        
        #registerAnInstanciatedCommand with invalid command type
        #registerAnInstanciatedCommand with invalid keyList
        #registerAnInstanciatedCommand with valid args
        #registerAnInstanciatedCommand with valid args and registerSetTempPrefix
        #registerAnInstanciatedCommand with valid args and registerSetGlobalPrefix
        
        #registerCommand with invalid keyList
        #registerCommand test showInHelp
        #registerCommand test pre/pro/post
        #registerCommand test name generation
        #registerCommand with valid args and registerSetTempPrefix
        #registerCommand with valid args and registerSetGlobalPrefix
        
        #registerCreateMultiCommand with invalid keyList
        #registerCreateMultiCommand test showInHelp
        #registerCreateMultiCommand test name generation
        #registerCommand with valid args and registerSetTempPrefix
        #registerCommand with valid args and registerSetGlobalPrefix
        
        #registerStopHelpTraversalAt with invalid keyList
        #registerStopHelpTraversalAt with valid args and NO predefined prefix
        #registerStopHelpTraversalAt with valid args and registerSetTempPrefix
        #registerStopHelpTraversalAt with valid args and registerSetGlobalPrefix
        
    ## CommandLoader ##
    
        #TODO
        
if __name__ == '__main__':
    unittest.main()
