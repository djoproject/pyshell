#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.command.command import *
from pyshell.command.exception import *

class ArgCheckerTest(unittest.TestCase):
    def setUp(self):
        pass
        
#test multicommand
    #init an empty one and check the args
    def testEmptyCommand(self):
        mc = MultiCommand("plop", "rtfm", False)
        self.assertTrue(mc.name == "plop" and mc.helpMessage == "rtfm" and not mc.showInHelp)
        
    #addProcess
    def testAddProcess(self):
        mc = MultiCommand("plop", "rtfm", False)
        #add preProcess with/withou checker
        self.assertRaises(commandException, mc.addProcess) #pre/pro/post process are None
        
        #test meth insertion and usagebuilder set
        def toto():
            pass
        
        toto.checker = 52
        self.assertTrue(mc.addProcess(toto) == None)
        self.assertTrue(mc.usageBuilder == 52) 
        
        toto.checker = 53
        self.assertTrue(mc.addProcess(None,toto) == None)
        self.assertTrue(mc.usageBuilder == 52) #the usage builder is still the builder of the first command inserted
        
        toto.checker = 54
        self.assertTrue(mc.addProcess(None,None,toto) == None)
        self.assertTrue(mc.usageBuilder == 52) #the usage builder is still the builder of the first command inserted
        
        mc = MultiCommand("plop", "rtfm", False)
        mc.addProcess(None,None,toto)
        self.assertTrue(mc.usageBuilder == 54)
        
        toto.checker = 52
        mc.addProcess(toto)
        self.assertTrue(mc.usageBuilder == 54)
        
        toto.checker = 53
        mc.addProcess(None,toto)
        self.assertTrue(mc.usageBuilder == 54)
        
        mc = MultiCommand("plop", "rtfm", False)
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
        for (u,c,) in mc:
            self.assertTrue(u)
        
    #addStaticCommand
    def testStaticCommand(self):
        mc = MultiCommand("plop", "rtfm", False)
        c = Command()
        
        #try to insert anything but cmd instance
        self.assertRaises(commandException,mc.addStaticCommand,23)
        
        #try to insert a valid cmd
        self.assertTrue(mc.addStaticCommand(c) == None)
        
        #try to insert where there is a dynamic command in in
        mc.dymamicCount = 1
        self.assertRaises(commandException,mc.addStaticCommand,c)
        
        #check self.usageBuilder, and useArgs in the list
        self.assertTrue(mc.usageBuilder == c.preProcess.checker)
        
    #usage
    def testUsage(self):
        mc = MultiCommand("plop", "rtfm", False)
        c = Command()
        
        #test with and without self.usageBuilder
        self.assertTrue(mc.usage() == "plop: no args needed")
        
        mc.addStaticCommand(c)
        self.assertTrue(mc.usage() == "plop [args:(<any> ... <any>)]")
        
    #reset
    def testReset(self):
        mc = MultiCommand("plop", "rtfm", False)
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
        self.assertTrue(mc.args == None)
        self.assertTrue(mc.dymamicCount == 0)
        self.assertTrue(len(mc.onlyOnceDict) == 0)
        self.assertTrue(mc.preCount == mc.proCount == mc.postCount == 0)
        self.assertTrue(finalCount == len(mc))
        
    #setArgs
    def testArgs(self):
        mc = MultiCommand("plop", "rtfm", False)
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
        mc = MultiCommand("plop", "rtfm", False)
        #set (anything/multioutput) then flush
        mc.setArgs(42)
        mc.flushArgs()
        
        #it must always be None
        self.assertTrue(mc.args == None)
    
    #TODO addDynamicCommand
    def testAddDynamicCommand(self):
        #try to insert anything but command
        #try to insert the same command twice with onlyAddOnce=True
            #do the same with onlyAddOnce=False
            #try to redeclare the same command prototype
        #check dynamic count
        #check useArgs in the list
        pass
    
    #TODO test unicommand class
        #test to create a basic empty one
        #then with different kind of args
        #try to add another command

if __name__ == '__main__':
    unittest.main()
