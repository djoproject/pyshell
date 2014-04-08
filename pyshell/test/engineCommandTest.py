#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.command.exception import *
from pyshell.arg.decorator import shellMethod
from pyshell.arg.argchecker import ArgChecker
from pyshell.command.command import *
from pyshell.command.engine import *

@shellMethod(arg=ArgChecker()) 
def plop(arg):
    return arg

class splitAndMergeTest(unittest.TestCase): 
    #TODO skipNextSubCommandOnTheCurrentData
    #TODO skipNextSubCommandForTheEntireDataBunch
    #TODO skipNextSubCommandForTheEntireExecution
    #TODO disableEnablingMapOnDataBunch
    #TODO enableSubCommandInCurrentDataBunchMap
    #TODO enableSubCommandInCommandMap
    #TODO disableSubCommandInCurrentDataBunchMap
    #TODO disableSubCommandInCommandMap
    #TODO _setStateSubCmdInCmd
    #TODO _setStateSubCmdInDataBunch
    #TODO flushArgs
    #TODO addSubCommand
    #TODO addCommand

    def test_isCurrentRootCommand(self):
        mc = MultiCommand("Multiple test")
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)
        mc.addProcess(plop,plop,plop)

        engine = engineV3([mc,mc,mc])

        self.assertTrue(engine.isCurrentRootCommand())

        engine.stack[-1][1].append(2)
        self.assertFalse(engine.isCurrentRootCommand())

        del engine.stack[:]
        self.assertRaises(executionException, engine.isCurrentRootCommand)
    
    
if __name__ == '__main__':
    unittest.main()
