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
from tries import multiLevelTries
from pyshell.utils.exception  import DefaultPyshellException
from pyshell.utils.solving    import Solver, _removeEveryIndexUnder, _addValueToIndex, _isValidBooleanValueForChecker
from pyshell.utils.parsing    import Parser
from pyshell.system.parameter import ParameterManagerV3, VarParameter
from pyshell.command.command  import UniCommand
from pyshell.arg.decorator    import shellMethod
from pyshell.arg.argchecker   import defaultInstanceArgChecker,listArgChecker

@shellMethod(param=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def plop_meth(param):
    pass

class SolvingTest(unittest.TestCase):
    def setUp(self):
        self.mltries = multiLevelTries()
        
        m = UniCommand("plop", plop_meth)
        self.mltries.insert( ("plop",) ,m)
        
        self.var     = ParameterManagerV3()
    
    ### INIT ###
    
    def test_initSolving1(self):
        s = Solver()
        self.assertRaises(DefaultPyshellException, s.solve, "plop", self.mltries, self.var)
        
    def test_initSolving2(self):
        p = Parser("plop")
        s = Solver()
        self.assertRaises(DefaultPyshellException, s.solve, p, self.mltries, self.var)
        
    def test_initSolving3(self):
        p = Parser("plop")
        p.parse()
        s = Solver()
        self.assertRaises(DefaultPyshellException, s.solve, p, "toto", self.var)
        
    def test_initSolving4(self):
        p = Parser("plop")
        p.parse()
        s = Solver()
        self.assertRaises(DefaultPyshellException, s.solve, p, self.mltries,"plap")
    
    ### VAR SOLVING ###
    
    def test_var1(self): #existing var (size 0)
        p = Parser("plop $plop")
        p.parse()
        s = Solver()
        
        self.var.setParameter("plop",VarParameter( () ))
        
        commandList, argList, mappedArgsList = s.solve(p, self.mltries, self.var)
        
        self.assertEqual(len(commandList), 1)
        self.assertEqual(commandList[0], self.mltries.search( ("plop",) ).getValue() )
        
        self.assertEqual(len(argList), 1)
        self.assertEqual(len(argList[0]), 0)
        
        self.assertEqual(len(mappedArgsList), 1)
        self.assertEqual(len(mappedArgsList[0][0]), 0)
        self.assertEqual(len(mappedArgsList[0][1]), 0)
        self.assertEqual(len(mappedArgsList[0][2]), 0) 
        
    def test_var2(self): #existing var (size 0) with parameter, and so update of the parameter spotted index
        p = Parser("plop $plop -param aa bb cc")
        p.parse()
        s = Solver()
        
        self.var.setParameter("plop",VarParameter( () ))
        
        commandList, argList, mappedArgsList = s.solve(p, self.mltries, self.var)
        
        self.assertEqual(len(commandList), 1)
        self.assertEqual(commandList[0], self.mltries.search( ("plop",) ).getValue() )
        
        self.assertEqual(len(argList), 1)
        self.assertEqual(len(argList[0]), 0)
        
        self.assertEqual(len(mappedArgsList), 1)
        self.assertEqual(len(mappedArgsList[0][0]), 1)
        self.assertEqual(mappedArgsList[0][0]["param"], ("aa","bb","cc",))
        
        self.assertEqual(len(mappedArgsList[0][1]), 0)
        self.assertEqual(len(mappedArgsList[0][2]), 0)

    def test_var3(self):#existing var (size 1)
        p = Parser("plop $plop")
        p.parse()
        s = Solver()
        
        self.var.setParameter("plop",VarParameter( ("uhuh",) ))
        
        commandList, argList, mappedArgsList = s.solve(p, self.mltries, self.var)
        
        self.assertEqual(len(commandList), 1)
        self.assertEqual(commandList[0], self.mltries.search( ("plop",) ).getValue() )
        
        self.assertEqual(len(argList), 1)
        self.assertEqual(len(argList[0]), 1)
        self.assertEqual(argList[0], ["uhuh"])
        
        self.assertEqual(len(mappedArgsList), 1)
        self.assertEqual(len(mappedArgsList[0][0]), 0)
        self.assertEqual(len(mappedArgsList[0][1]), 0)
        self.assertEqual(len(mappedArgsList[0][2]), 0) 
        
        
    def test_var4(self):#existing var (size bigger than 1)
        p = Parser("plop $plop")
        p.parse()
        s = Solver()
        
        self.var.setParameter("plop",VarParameter( ("uhuh","ihih","ohoho",) ))
        
        commandList, argList, mappedArgsList = s.solve(p, self.mltries, self.var)
        
        self.assertEqual(len(commandList), 1)
        self.assertEqual(commandList[0], self.mltries.search( ("plop",) ).getValue() )
        
        self.assertEqual(len(argList), 1)
        self.assertEqual(len(argList[0]), 3)
        self.assertEqual(argList[0], ["uhuh","ihih","ohoho"])
        
        self.assertEqual(len(mappedArgsList), 1)
        self.assertEqual(len(mappedArgsList[0][0]), 0)
        self.assertEqual(len(mappedArgsList[0][1]), 0)
        self.assertEqual(len(mappedArgsList[0][2]), 0) 
            
    def test_var5(self):#existing var (size bigger than 1) with parameter spotted or not (check the index)
        p = Parser("plop $plop -param aa bb cc")
        p.parse()
        s = Solver()
        
        self.var.setParameter("plop",VarParameter( ("uhuh","ihih","ohoho",) ))
        
        commandList, argList, mappedArgsList = s.solve(p, self.mltries, self.var)
        
        self.assertEqual(len(commandList), 1)
        self.assertEqual(commandList[0], self.mltries.search( ("plop",) ).getValue() )
        
        self.assertEqual(len(argList), 1)
        self.assertEqual(len(argList[0]), 3)
        self.assertEqual(argList[0], ["uhuh","ihih","ohoho"])
        
        self.assertEqual(len(mappedArgsList), 1)
        self.assertEqual(len(mappedArgsList[0][0]), 1)
        self.assertEqual(mappedArgsList[0][0]["param"], ("aa","bb","cc",))
        
        self.assertEqual(len(mappedArgsList[0][1]), 0)
        self.assertEqual(len(mappedArgsList[0][2]), 0) 
        
    def test_var6(self):#not existing var
        p = Parser("plop $plop")
        p.parse()
        s = Solver()
        
        commandList, argList, mappedArgsList = s.solve(p, self.mltries, self.var)
        
        self.assertEqual(len(commandList), 1)
        self.assertEqual(commandList[0], self.mltries.search( ("plop",) ).getValue() )
        
        self.assertEqual(len(argList), 1)
        self.assertEqual(len(argList[0]), 0)
        
        self.assertEqual(len(mappedArgsList), 1)
        self.assertEqual(len(mappedArgsList[0][0]), 0)
        self.assertEqual(len(mappedArgsList[0][1]), 0)
        self.assertEqual(len(mappedArgsList[0][2]), 0)

    ### SOLVING COMMAND ###
    
    def test_solving1(self):#ambiguous command
        m = UniCommand("plap", plop_meth)
        self.mltries.insert( ("plap",) ,m)
    
        p = Parser("pl")
        p.parse()
        s = Solver()
        
        self.assertRaises(DefaultPyshellException, s.solve, p, self.mltries, self.var)
        
    def test_solving2(self):#all token used and no command found
        m = UniCommand("plap plup plip", plop_meth)
        self.mltries.insert( ("plap","plup","plip",) ,m)
    
        p = Parser("plap plup")
        p.parse()
        s = Solver()
        
        self.assertRaises(DefaultPyshellException, s.solve, p, self.mltries, self.var)
        
    def test_solving3(self):#no token found at all
        p = Parser("titi")
        p.parse()
        s = Solver()
        
        self.assertRaises(DefaultPyshellException, s.solve, p, self.mltries, self.var)
        
    def test_solving4(self):#at least first token found
        m = UniCommand("plap plup plip", plop_meth)
        self.mltries.insert( ("plap","plup","plip",) ,m)
    
        p = Parser("plap toto")
        p.parse()
        s = Solver()
        
        self.assertRaises(DefaultPyshellException, s.solve, p, self.mltries, self.var)

    def test_solving5(self):#command found without arg
        s = Solver()
        p = Parser("plop")
        p.parse()
        
        commandList, argList, mappedArgsList = s.solve(p, self.mltries, self.var)
        
        self.assertEqual(len(commandList), 1)
        self.assertEqual(commandList[0], self.mltries.search( ("plop",) ).getValue() )
        
        self.assertEqual(len(argList), 1)
        self.assertEqual(len(argList[0]), 0)
        
        self.assertEqual(len(mappedArgsList), 1)
        self.assertEqual(len(mappedArgsList[0][0]), 0)
        self.assertEqual(len(mappedArgsList[0][1]), 0)
        self.assertEqual(len(mappedArgsList[0][2]), 0)
    
    def test_solving6(self):#command found with arg
        s = Solver()
        p = Parser("plop aaa bbb ccc ddd")
        p.parse()
        
        commandList, argList, mappedArgsList = s.solve(p, self.mltries, self.var)
        
        self.assertEqual(len(commandList), 1)
        self.assertEqual(commandList[0], self.mltries.search( ("plop",) ).getValue() )
        
        self.assertEqual(len(argList), 1)
        self.assertEqual(len(argList[0]), 4)
        self.assertEqual(argList[0], ["aaa","bbb","ccc","ddd"])
        
        self.assertEqual(len(mappedArgsList), 1)
        self.assertEqual(len(mappedArgsList[0][0]), 0)
        self.assertEqual(len(mappedArgsList[0][1]), 0)
        self.assertEqual(len(mappedArgsList[0][2]), 0)
        
    ### TODO SOLVING DASHED PARAM ###
    
        #no param
        #no command in command
        #checker on pre OR pro OR post
        #valid param but not in the existing param of the command
        
        #stop to collect token for a param because a second valid one has been identified
            #and we have more token available than the limit of the current param
            #and we have exactly enought token available than the limit of the current param
            #and we have less token available than the limit of the current param
        
        #stop to collect token for a param because we reach the end of the available tokens
            #and we have more token available than the limit of the current param
            #and we have exactly enought token available than the limit of the current param
            #and we have less token available than the limit of the current param
            
        #boolean without token after
            #because of the end of token
            #because another param start immediatelly after boolean param
            
        #boolean with invalid bool token after
            #and no other token after the invalid one
                #end of the token list
                #start of new parameter
                
            #and other token after the invalid one
                #end of the token list
                #start of new parameter
            
        #boolean with valid bool token after
            #and no other token after the valid one
                #end of the token list
                #start of new parameter
                
            #and other token after the valid one
                #end of the token list
                #start of new parameter
        
    ### MISC CHECKS ###
            
    def test_removeEveryIndexUnder1(self):#no index removing
        l = [4,5,6,7,8]
        l2 = l[:]
        _removeEveryIndexUnder(l,3)
        self.assertEqual(l, l2)
        
    def test_removeEveryIndexUnder1(self):#no index removing
        l = [4,5,6,7,8]
        l2 = l[:]
        _removeEveryIndexUnder(l,4)
        self.assertEqual(l, l2)
    
    def test_removeEveryIndexUnder2(self):#all index removing, exact match index
        l = [4,7,12,23,35]
        _removeEveryIndexUnder(l,36)
        self.assertEqual(l, [])
    
    def test_removeEveryIndexUnder3(self):#all index removing, bigger limit match
        l = [4,7,12,23,35]
        _removeEveryIndexUnder(l,8000)
        self.assertEqual(l, [])
    
    def test_removeEveryIndexUnder4(self):#part of index removing, exact match index
        l = [4,7,12,23,35]
        l2 = l[2:]
        _removeEveryIndexUnder(l,12)
        self.assertEqual(l, l2)
    
    def test_removeEveryIndexUnder5(self):#part of index removing, bigger limit match
        l = [4,7,12,23,35]
        l2 = l[2:]
        _removeEveryIndexUnder(l,9)
        self.assertEqual(l, l2)
                
    def test_addValueToIndex1(self):#no index updating #exact match index
        l = [4,7,12,23,35]
        l2 = [4,7,12,23,35]
        _addValueToIndex(l,36)
        self.assertEqual(l, l2)
        
    def test_addValueToIndex2(self):#no index updating #bigger limit match
        l = [4,7,12,23,35]
        l2 = [4,7,12,23,35]
        _addValueToIndex(l,8000)
        self.assertEqual(l, l2)
        
    def test_addValueToIndex3(self):#all index updating #exact match index
        l = [4,7,12,23,35]
        l2 = [5,8,13,24,36]
        _addValueToIndex(l,4)
        self.assertEqual(l, l2)
        
    def test_addValueToIndex4(self):#all index updating #bigger limit match
        l = [4,7,12,23,35]
        l2 = [5,8,13,24,36]
        _addValueToIndex(l,2)
        self.assertEqual(l, l2)
    
    def test_addValueToIndex5(self):#part of index updating #exact match index
        l = [4,7,12,23,35]
        l2 = [4,7,12,24,36]
        _addValueToIndex(l,23)
        self.assertEqual(l, l2)
        
    def test_addValueToIndex6(self):#part of index updating #bigger limit match
        l = [4,7,12,23,35]
        l2 = [4,7,12,24,36]
        _addValueToIndex(l,15)
        self.assertEqual(l, l2)
    
    def test_isValidBooleanValueForChecker(self):
        self.assertTrue(_isValidBooleanValueForChecker("t"))
        self.assertTrue(_isValidBooleanValueForChecker("tr"))
        self.assertTrue(_isValidBooleanValueForChecker("tRu"))
        self.assertTrue(_isValidBooleanValueForChecker("true"))
        self.assertTrue(_isValidBooleanValueForChecker("FALSE"))
        self.assertTrue(_isValidBooleanValueForChecker("faLSe"))
        self.assertTrue(_isValidBooleanValueForChecker("f"))
        self.assertTrue(_isValidBooleanValueForChecker("false"))
        self.assertTrue(_isValidBooleanValueForChecker("FA"))
        
        self.assertFalse(_isValidBooleanValueForChecker("plop"))
        self.assertFalse(_isValidBooleanValueForChecker("falo"))
        self.assertFalse(_isValidBooleanValueForChecker("trut"))
    
if __name__ == '__main__':
    unittest.main()
