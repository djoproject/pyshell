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

#TODO
    #add new test for allowed transition testing and forbidde several addon loaded
    #remove old test irrelevant about transaction

import unittest
from pyshell.loader.utils import getAndInitCallerModule, AbstractLoader, GlobalLoader
from pyshell.loader.exception import RegisterException,LoadException
from pyshell.utils.exception  import ListOfException
from pyshell.utils.constants  import DEFAULT_PROFILE_NAME, STATE_LOADED, STATE_LOADED_E, STATE_UNLOADED, STATE_UNLOADED_E

class SubAbstractLoader(AbstractLoader):
    pass
    
class SubAbstractLoaderWithError(AbstractLoader):
    def load(self, parameterManager, profile=None):
        raise Exception("errroooorrr !")
        
class SubAbstractUnloaderWithError(AbstractLoader):
    def unload(self, parameterManager, profile=None):
        raise Exception("errroooorrr !")
        
    def reload(self, parameterManager, profile=None):
        raise Exception("errroooorrr !")

class UtilsTest(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        global _loaders
        if "_loaders" in globals():
            del _loaders
    
    ### getAndInitCallerModule ###
    
    def test_getAndInitCallerModule1(self):#getAndInitCallerModule, parent module does not have _loader THEN parent module has _loader
        global _loaders
        self.assertFalse("_loaders" in globals())
        loader1 = getAndInitCallerModule("getAndInitCallerModule1", SubAbstractLoader, profile = None, moduleLevel = 1)
        self.assertTrue("_loaders" in globals())
        self.assertIsInstance(_loaders, GlobalLoader)
        loader2 = getAndInitCallerModule("getAndInitCallerModule1", SubAbstractLoader, profile = None, moduleLevel = 1)
        self.assertIs(loader1, loader2)
        
    def test_getAndInitCallerModule2(self):#getAndInitCallerModule, parent module has _loader but with a wrong type
        global _loaders
        _loaders = "plop"
        self.assertTrue("_loaders" in globals())
        self.assertRaises(RegisterException, getAndInitCallerModule,"getAndInitCallerModule1", AbstractLoader, profile = None, moduleLevel = 2) #level is 2 because we have to go outside of the assert module
        
    ### AbstractLoader ###
    
    def test_AbstractLoader1(self):#AbstractLoader, init, exist without arg
        self.assertTrue(hasattr(AbstractLoader, "__init__"))
        self.assertTrue(hasattr(AbstractLoader.__init__, "__call__"))
        self.assertIsInstance(AbstractLoader(), AbstractLoader)
        self.assertRaises(TypeError, AbstractLoader, None)
        
    def test_AbstractLoader2(self):#AbstractLoader, load, exist, test args
        al = AbstractLoader()
        self.assertTrue(al, "load")
        self.assertTrue(al.load, "__call__")
        self.assertIs(al.load(None), None)
        self.assertIs(al.load(None, None), None)
        self.assertRaises(TypeError, al.load, None, None, None)
        
    def test_AbstractLoader3(self):#AbstractLoader, unload, exist, test args
        al = AbstractLoader()
        self.assertTrue(al, "unload")
        self.assertTrue(al.unload, "__call__")
        self.assertIs(al.unload(None), None)
        self.assertIs(al.unload(None, None), None)
        self.assertRaises(TypeError, al.unload, None, None, None)
        
    def test_AbstractLoader4(self):#AbstractLoader, reload, exist, test args
        al = AbstractLoader()
        self.assertTrue(al, "reload")
        self.assertTrue(al.reload, "__call__")
        self.assertIs(al.reload(None), None)
        self.assertIs(al.reload(None, None), None)
        self.assertRaises(TypeError, al.reload, None, None, None)
    
    ### GlobalLoader ###
    
    def test_GlobalLoaderInit(self):#GlobalLoader, test init, subAddons must be empty, no constructor arg
        self.assertTrue(hasattr(GlobalLoader, "__init__"))
        self.assertTrue(hasattr(GlobalLoader.__init__, "__call__"))
        self.assertIsInstance(GlobalLoader(), GlobalLoader)
        self.assertRaises(TypeError, GlobalLoader, None)
    
    ## getLoader ##
    
    def test_GlobalLoaderGetLoader1(self):#profile is not None, loaderName exist
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderGetLoader1", SubAbstractLoader, profile = "plop")
        l2 = gl.getOrCreateLoader("GlobalLoaderGetLoader1", SubAbstractLoader, profile = "plop")
        self.assertIs(l1,l2)
    
    def test_GlobalLoaderGetLoader2(self):#profile is not None, loaderName does not exist, classDefinition is anything
        gl = GlobalLoader()
        self.assertRaises(RegisterException, gl.getOrCreateLoader, "GlobalLoaderGetLoader2", 42, profile = "plop")
    
    def test_GlobalLoaderGetLoader3(self):#profile is not None, loaderName does not exist, classDefinition is AbstractLoader
        gl = GlobalLoader()
        self.assertRaises(RegisterException, gl.getOrCreateLoader, "GlobalLoaderGetLoader3", AbstractLoader, profile = "plop")
    
    def test_GlobalLoaderGetLoader4(self):#profile is not None, loaderName does not exist, classDefinition is a class definition that does not inherit from AbstractLoader
        gl = GlobalLoader()
        self.assertRaises(RegisterException, gl.getOrCreateLoader, "GlobalLoaderGetLoader4", object, profile = "plop")
    
    def test_GlobalLoaderGetLoader5(self):#profile is not None, loaderName does not exist, classDefinition is valid, profile already exist for another loaderName
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderGetLoader5a", SubAbstractLoader, profile = "plop")
        l2 = gl.getOrCreateLoader("GlobalLoaderGetLoader5b", SubAbstractLoader, profile = "plop")
        self.assertIsNot(l1,l2)
    
    def test_GlobalLoaderGetLoader6(self):#profile is not None, loaderName does not exist, classDefinition is valid, profile does not exist for another loaderName
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderGetLoader6", SubAbstractLoader, profile = "plop")
        self.assertIsNot(l1,None)
        
    def test_GlobalLoaderGetLoader7(self):#profile is None, loaderName exist
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderGetLoader7", SubAbstractLoader, profile = None)
        l2 = gl.getOrCreateLoader("GlobalLoaderGetLoader7", SubAbstractLoader, profile = None)
        self.assertIs(l1,l2)
    
    def test_GlobalLoaderGetLoader8(self):#profile is None, loaderName does not exist, classDefinition is anything
        gl = GlobalLoader()
        self.assertRaises(RegisterException, gl.getOrCreateLoader, "GlobalLoaderGetLoader8", 42, profile = None)
    
    def test_GlobalLoaderGetLoader9(self):#profile is None, loaderName does not exist, classDefinition is AbstractLoader
        gl = GlobalLoader()
        self.assertRaises(RegisterException, gl.getOrCreateLoader, "GlobalLoaderGetLoader9", AbstractLoader, profile = None)
    
    def test_GlobalLoaderGetLoader10(self):#profile is None, loaderName does not exist, classDefinition is a class definition that does not inherit from AbstractLoader
        gl = GlobalLoader()
        self.assertRaises(RegisterException, gl.getOrCreateLoader, "GlobalLoaderGetLoader10", object, profile = None)
    
    def test_GlobalLoaderGetLoader11(self):#profile is None, loaderName does not exist, classDefinition is valid, profile already exist for another loaderName
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderGetLoader11a", SubAbstractLoader, profile = None)
        l2 = gl.getOrCreateLoader("GlobalLoaderGetLoader11b", SubAbstractLoader, profile = None)
        self.assertIsNot(l1,l2)
    
    def test_GlobalLoaderGetLoader12(self):#profile is None, loaderName does not exist, classDefinition is valid, profile does not exist for another loaderName
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderGetLoader12", SubAbstractLoader, profile = None)
        self.assertIsNot(l1,None)
        
    ## _innerLoad ##
    def test_GlobalLoader_innerLoad1(self):#profile is not None, profile is not in profileList
        gl = GlobalLoader()
        self.assertIs(gl._innerLoad(methodName="kill", parameterManager=None, profile = "TOTO", nextState="nstate",nextStateIfError="estate"),None)
        
    #def test_GlobalLoader_innerLoad2(self):#profile is not None, profile is in profileList, profile in invalid state
    #    gl = GlobalLoader()
    #    l1 = gl.getOrCreateLoader("GlobalLoader_innerLoad2", SubAbstractLoader, profile = "TOTO")
    #    self.assertRaises(LoadException, gl._innerLoad, methodName="kill", parameterManager=None, profile = "TOTO", nextState="nstate",nextStateIfError="estate")
        
    def test_GlobalLoader_innerLoad3(self):#profile is not None, profile is in profileList,profile in valid state, unknown method name
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoader_innerLoad3", SubAbstractLoader, profile = "TOTO")
        self.assertRaises(AttributeError, gl._innerLoad, methodName="kill", parameterManager=None, profile = "TOTO", nextState="nstate",nextStateIfError="estate")
        
    def test_GlobalLoader_innerLoad4(self):#profile is not None, profile is in profileList,profile in valid state, known method name, with error production
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoader_innerLoad4", SubAbstractLoaderWithError, profile = "TOTO")
        self.assertRaises(ListOfException, gl._innerLoad, methodName="load", parameterManager=None, profile = "TOTO", nextState="nstate",nextStateIfError="estate")
        self.assertEqual(gl.lastUpdatedProfile[0], "TOTO")
        self.assertEqual(gl.lastUpdatedProfile[1], "estate")
        
    def test_GlobalLoader_innerLoad5(self):#profile is not None, profile is in profileList,profile in valid state, known method name, without error production
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoader_innerLoad5", SubAbstractLoader, profile = "TOTO")
        gl._innerLoad(methodName="load", parameterManager=None, profile = "TOTO", nextState="nstate",nextStateIfError="estate")
        self.assertEqual(gl.lastUpdatedProfile[0], "TOTO")
        self.assertEqual(gl.lastUpdatedProfile[1], "nstate")
        
    def test_GlobalLoader_innerLoad6(self):#profile is None, profile is not in profileList
        gl = GlobalLoader()
        self.assertIs(gl._innerLoad(methodName="kill", parameterManager=None, profile = None, nextState="nstate",nextStateIfError="estate"),None)
        
    #def test_GlobalLoader_innerLoad7(self):#profile is None, profile is in profileList, profile in invalid state
    #    gl = GlobalLoader()
    #    l1 = gl.getOrCreateLoader("GlobalLoader_innerLoad7", SubAbstractLoader, profile = None)
    #    self.assertRaises(LoadException, gl._innerLoad, methodName="kill", parameterManager=None, profile = DEFAULT_PROFILE_NAME, nextState="nstate",nextStateIfError="estate")
        
    def test_GlobalLoader_innerLoad8(self):#profile is None, profile is in profileList,profile in valid state, unknown method name
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoader_innerLoad8", SubAbstractLoader, profile = None)
        self.assertRaises(AttributeError, gl._innerLoad, methodName="kill", parameterManager=None, profile = DEFAULT_PROFILE_NAME, nextState="nstate",nextStateIfError="estate")
        
    def test_GlobalLoader_innerLoad9(self):#profile is None, profile is in profileList,profile in valid state, known method name, with error production
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoader_innerLoad9", SubAbstractLoaderWithError, profile = None)
        self.assertRaises(ListOfException, gl._innerLoad, methodName="load", parameterManager=None, profile = DEFAULT_PROFILE_NAME, nextState="nstate",nextStateIfError="estate")
        self.assertEqual(gl.lastUpdatedProfile[0], DEFAULT_PROFILE_NAME)
        self.assertEqual(gl.lastUpdatedProfile[1], "estate")
        
    def test_GlobalLoader_innerLoad10(self):#profile is None, profile is in profileList,profile in valid state, known method name, without error production   
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoader_innerLoad10", SubAbstractLoader, profile = None)
        gl._innerLoad(methodName="load", parameterManager=None, profile = DEFAULT_PROFILE_NAME, nextState="nstate",nextStateIfError="estate")
        self.assertEqual(gl.lastUpdatedProfile[0], DEFAULT_PROFILE_NAME)
        self.assertEqual(gl.lastUpdatedProfile[1], "nstate")
                       
                    
    ## load ##
    def test_GlobalLoaderLoad1(self):#valid load
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderLoad1", SubAbstractLoader)
        gl.load(None)
        self.assertEqual(gl.lastUpdatedProfile[0], DEFAULT_PROFILE_NAME)
        self.assertEqual(gl.lastUpdatedProfile[1], STATE_LOADED)
    
    def test_GlobalLoaderLoad2(self):#valid load with error
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderLoad2", SubAbstractLoaderWithError)
        self.assertRaises(ListOfException, gl.load,None)
        self.assertEqual(gl.lastUpdatedProfile[0], DEFAULT_PROFILE_NAME)
        self.assertEqual(gl.lastUpdatedProfile[1], STATE_LOADED_E)
    
    def test_GlobalLoaderLoad3(self):#invalid load
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderLoad3", SubAbstractLoader)
        gl.load(None)
        self.assertEqual(gl.lastUpdatedProfile[0], DEFAULT_PROFILE_NAME)
        self.assertEqual(gl.lastUpdatedProfile[1], STATE_LOADED)
        self.assertRaises(LoadException,gl.load,None)
        
    ## unload ##
    def test_GlobalLoaderUnload4(self):#valid unload
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderLoad1", SubAbstractLoader)
        gl.load(None)
        gl.unload(None)
        self.assertEqual(gl.lastUpdatedProfile[0], DEFAULT_PROFILE_NAME)
        self.assertEqual(gl.lastUpdatedProfile[1], STATE_UNLOADED)
    
    def test_GlobalLoaderUnload5(self):#valid unload with error
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderLoad1", SubAbstractUnloaderWithError)
        gl.load(None)
        self.assertRaises(ListOfException, gl.unload,None)
        self.assertEqual(gl.lastUpdatedProfile[0], DEFAULT_PROFILE_NAME)
        self.assertEqual(gl.lastUpdatedProfile[1], STATE_UNLOADED_E)
    
    def test_GlobalLoaderUnload6(self):#invalid unload
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderLoad1", SubAbstractLoader)
        gl.load(None)
        gl.unload(None)
        self.assertEqual(gl.lastUpdatedProfile[0], DEFAULT_PROFILE_NAME)
        self.assertEqual(gl.lastUpdatedProfile[1], STATE_UNLOADED)
        self.assertRaises(LoadException,gl.unload,None)
        
    ## reload ##
    def test_GlobalLoaderReload7(self):#valid reload
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderLoad1", SubAbstractLoader)
        gl.load(None)
        gl.reload(None)
        self.assertEqual(gl.lastUpdatedProfile[0], DEFAULT_PROFILE_NAME)
        self.assertEqual(gl.lastUpdatedProfile[1], STATE_LOADED)
    
    def test_GlobalLoaderReload8(self):#valid reload with error
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderLoad1", SubAbstractUnloaderWithError)
        gl.load(None)
        self.assertRaises(ListOfException, gl.reload,None)
        self.assertEqual(gl.lastUpdatedProfile[0], DEFAULT_PROFILE_NAME)
        self.assertEqual(gl.lastUpdatedProfile[1], STATE_LOADED_E)

    
    def test_GlobalLoaderReload9(self):#invalid reload
        gl = GlobalLoader()
        l1 = gl.getOrCreateLoader("GlobalLoaderLoad1", SubAbstractLoader)
        gl.load(None)
        gl.unload(None)
        self.assertEqual(gl.lastUpdatedProfile[0], DEFAULT_PROFILE_NAME)
        self.assertEqual(gl.lastUpdatedProfile[1], STATE_UNLOADED)
        self.assertRaises(LoadException,gl.reload,None)
    
        
if __name__ == '__main__':
    unittest.main()
