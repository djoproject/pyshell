#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.command.command import *
from pyshell.command.exception import *

class commandTest(unittest.TestCase):
    def setUp(self):
        pass
        
#test multicommand
    #init an empty one and check the args
    def testEmptyCommand(self):
        mc = MultiCommand("plop", False)
        self.assertTrue(mc.name == "plop" and mc.helpMessage is None and not mc.showInHelp)
        
    #addProcess
    def testAddProcess(self):
        mc = MultiCommand("plop", False)
        #add preProcess with/withou checker
        self.assertRaises(commandException, mc.addProcess) #pre/pro/post process are None
        
        #test meth insertion and usagebuilder set
        def toto():
            "tata"
            pass
        
        toto.checker = 52
        self.assertTrue(mc.addProcess(toto) is None)
        self.assertTrue(mc.usageBuilder == 52) 
        self.assertEqual(mc.helpMessage,"tata")
        
        toto.checker = 53
        self.assertTrue(mc.addProcess(None,toto) is None)
        self.assertTrue(mc.usageBuilder == 52) #the usage builder is still the builder of the first command inserted
        
        toto.checker = 54
        self.assertTrue(mc.addProcess(None,None,toto) is None)
        self.assertTrue(mc.usageBuilder == 52) #the usage builder is still the builder of the first command inserted
        
        mc = MultiCommand("plop", False)
        mc.addProcess(None,None,toto)
        self.assertTrue(mc.usageBuilder == 54)
        
        toto.checker = 52
        mc.addProcess(toto)
        self.assertTrue(mc.usageBuilder == 54)
        
        toto.checker = 53
        mc.addProcess(None,toto)
        self.assertTrue(mc.usageBuilder == 54)
        
        mc = MultiCommand("plop", False)
        toto.checker = 53
        mc.addProcess(None,toto)
        self.assertTrue(mc.usageBuilder == 53)
        
        mc.addProcess(None,None,toto)
        self.assertTrue(mc.usageBuilder == 53)
        
        toto.checker = 52
        mc.addProcess(toto)
        self.assertTrue(mc.usageBuilder == 53)
        
        #try to insert not callable object
        self.assertRaises(commandException, mc.addProcess,1)
        self.assertRaises(commandException, mc.addProcess,None,1)
        self.assertRaises(commandException, mc.addProcess,None,None,1)

        #check the process length
        self.assertTrue(len(mc) == 3)
        
        #check if the useArgs is set in the list
        for (c,u,e,) in mc:
            self.assertTrue(u)
        
    #addStaticCommand
    def testStaticCommand(self):
        mc = MultiCommand("plop", False)
        c = Command()
        
        #try to insert anything but cmd instance
        self.assertRaises(commandException,mc.addStaticCommand,23)
        
        #try to insert a valid cmd
        self.assertTrue(mc.addStaticCommand(c) is None)
        
        #try to insert where there is a dynamic command in in
        mc.dymamicCount = 1
        self.assertRaises(commandException,mc.addStaticCommand,c)
        
        #check self.usageBuilder, and useArgs in the list
        self.assertTrue(mc.usageBuilder == c.preProcess.checker)
        
    #usage
    def testUsage(self):
        mc = MultiCommand("plop", False)
        c = Command()
        
        #test with and without self.usageBuilder
        self.assertTrue(mc.usage() == "plop: no args needed")
        
        mc.addStaticCommand(c)
        self.assertTrue(mc.usage() == "plop [args:(<any> ... <any>)]")
        
    #reset
    def testReset(self):
        mc = MultiCommand("plop", False)
        c = Command()
        
        #populate
        mc.addStaticCommand(c)
        mc.addDynamicCommand(c,True)
        mc.addDynamicCommand(c,True)
        mc.args = "toto"
        mc.preCount = 1
        mc.proCount = 2
        mc.postCount = 3
        
        #reset and test
        finalCount = len(mc) - mc.dymamicCount
        mc.reset()
        #self.assertTrue(mc.args is None)
        self.assertTrue(mc.dymamicCount == 0)
        self.assertTrue(len(mc.onlyOnceDict) == 0)
        self.assertTrue(mc.preCount == mc.proCount == mc.postCount == 0)
        self.assertTrue(finalCount == len(mc))
        
    #setArgs
    """def testArgs(self):
        mc = MultiCommand("plop", False)
        #try to add anything
        mc.setArgs(42)
        self.assertTrue(isinstance(mc.args, MultiOutput))
        self.assertTrue(mc.args[0] == 42)
        
        #try to add multioutput
        mo = MultiOutput([1,2,3])
        mc.setArgs(mo)
        self.assertTrue(isinstance(mc.args, MultiOutput))
        self.assertTrue(mc.args[0] == 1 and mc.args[1] == 2 and mc.args[2] == 3)
    
    #flushArgs
    def testFlus(self):
        mc = MultiCommand("plop", False)
        #set (anything/multioutput) then flush
        mc.setArgs(42)
        mc.flushArgs()
        
        #it must always be None
        self.assertTrue(mc.args is None)"""
    
    #addDynamicCommand
    def testAddDynamicCommand(self):
        mc = MultiCommand("plop", False)
        c = Command()
    
        #try to insert anything but command
        self.assertRaises(commandException, mc.addDynamicCommand, 42)
        
        #try to insert the same command twice with onlyAddOnce=True
        mc.addDynamicCommand(c)
        self.assertTrue(len(mc) == 1)
        mc.addDynamicCommand(c)
        self.assertTrue(len(mc) == 1)
        mc.addDynamicCommand(c, False)#do the same with onlyAddOnce=False
        self.assertTrue(len(mc) == 2)
        
        #check useArgs in the list
        for (c,u,e,) in mc:
            self.assertTrue(u)
    
    #test unicommand class
    def testUniCommand(self):
        #test to create a basic empty one
        self.assertRaises(commandException, UniCommand, "plop")
        
        def toto():
            pass
        
        #then with different kind of args
        self.assertTrue(UniCommand("plop", toto) is not None )
        self.assertTrue(UniCommand("plop", None, toto) is not None )
        self.assertTrue(UniCommand("plop", None,None,toto) is not None )

        #try to add another command
        uc = UniCommand("plop", toto)
        self.assertTrue(len(uc) == 1)
        
        uc.addProcess()
        self.assertTrue(len(uc) == 1)
        
        uc.addStaticCommand(42)
        self.assertTrue(len(uc) == 1)
    
    def test_EnableDisableCmd(self):
        def plop():
            pass

        mc = MultiCommand("plop", False)
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop)
        mc.addProcess(plop)
        mc.addProcess(plop,plop)

        index = 0
        for c,a,e in mc:
            self.assertTrue(e)
            self.assertTrue(a)

            if (index % 2) == 0:
                mc.disableCmd(index)
            else:
                mc.disableArgUsage(index)

            index += 1

        index = 0
        for c,a,e in mc:
            if (index % 2) == 0:
                self.assertTrue(a)
                self.assertFalse(e)
                mc.disableArgUsage(index)
                mc.enableCmd(index)
            else:
                self.assertTrue(e)
                self.assertFalse(a)
                mc.disableCmd(index)
                mc.enableArgUsage(index)
            index += 1

        index = 0
        for c,a,e in mc:
            if (index % 2) == 0:
                self.assertTrue(e)
                self.assertFalse(a)
            else:
                self.assertTrue(a)
                self.assertFalse(e)
            index += 1

if __name__ == '__main__':
    unittest.main()
