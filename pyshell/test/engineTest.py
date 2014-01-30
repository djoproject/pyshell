#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.command.engine import *
from pyshell.command.command import *

class ArgCheckerTest(unittest.TestCase):
    def setUp(self):
        pass
        
    #TODO test multicommand
        #init an empty one and check the args
        #addProcess
            #add preProcess with/withou checker
            #check the value of self.usageBuilder
            #do the same with process and postProcess
            #check the process length
            #check if the useArgs is set in the list
        #addStaticCommand
            #try to insert anything but cmd instance
            #try to insert a valid cmd
            #try to insert where there is a dynamic command in in
            #check self.usageBuilder, and useArgs in the list
        #usage
            #test with and without self.usageBuilder
        #reset
            #args must be None, args was not none before the test
            #dynamic function must have been removed and the counter must be equal to zero
            #self.onlyOnceDict must be empty, check with a non empty dict
            #the three execution counter must be equal to zero, test with not empty value
        #setArgs
            #try to add anything
            #try to add multioutput
            #it can't store multioutput into multioutput
        
        #getArgs
            #set (anything/multioutput) then get
        
        #flushArgs
            #set (anything/multioutput) then flush
            #it must always be None
        
        #addDynamicCommand
            #try to insert anything but command
            #try to insert the same command twice with onlyAddOnce=True
                #do the same with onlyAddOnce=False
                #try to redeclare the same command prototype
            #check dynamic count
            #check useArgs in the list
    
    #TODO test unicommand
        #test to create a basic empty one
        #then with different kind of args
        #try to add another command
    
    def test_test(self):
        pass

    #TODO test engine module
    
if __name__ == '__main__':
    unittest.main()
