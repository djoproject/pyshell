#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.command.engine import *
from pyshell.command.command import *
from pyshell.arg.decorator import shellMethod
from pyshell.arg.argchecker import ArgChecker, IntegerArgChecker

#TODO pour l'instant dans les tests, on ne tiens pas compte de
    #-args
    #-useArgs
    #-execution limit

class ArgCheckerTest(unittest.TestCase):
    def setUp(self):
        pass

    def _testExecuteSimpleOne(self):
        #TODO choses qui ne vont pas dans ce test :
            #-s'il n'y a qu'un argument l'ensemble des args ne lui est pas lié automatiquement
                #ok le comportement correcte a avoir
                    #s'il n'y a qu'un args, on bind to sur lui
                    #s'il n'y a pas d'arg, pas grave
                    #s'il y a plusieurs args, on doit faire sauter une exception a l'ajout du process
            #-pas vraiment un probleme mais obligation d'avoir un retour dans le post pour ce cas ci, sinon l'encapsulation ne marche pas
                #-car arg3 n'a pas de valeur par défaut
    
        @shellMethod(arg1=IntegerArgChecker())
        def pre(arg1=0):
            self.preCount +=1
            return 5+arg1
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro(arg2):
            self.proCount += 1
            return arg2*arg2
        
        @shellMethod(arg3=ArgChecker()) 
        def post(arg3):
            self.assertTrue(arg3 == self.valueToTest)
            self.postCount += 1
            return arg3 #needed to the next post method in case of encapsulation
        
        #simple test
        self.valueToTest = 25
        self.preCount = self.proCount = self.postCount = 0
        uc = UniCommand("simple test", "help me", pre, pro, post)
        engine = engineV3([uc])
        engine.execute()
        self.assertTrue(self.preCount == 1)
        self.assertTrue(self.proCount == 1)
        self.assertTrue(self.postCount == 1)
        
        self.valueToTest = 100
        self.preCount = self.proCount = self.postCount = 0
        #uni command encapsulation test, the most used case
        engine = engineV3([uc, uc])
        engine.execute()
        self.assertTrue(self.preCount == 2)
        self.assertTrue(self.proCount == 1)
        self.assertTrue(self.postCount == 2)
        
        self.valueToTest = 225
        self.preCount = self.proCount = self.postCount = 0
        engine = engineV3([uc, uc, uc])
        engine.execute()
        self.assertTrue(self.preCount == 3)
        self.assertTrue(self.proCount == 1)
        self.assertTrue(self.postCount == 3)
        
        #...
    
    #test du mutliOutput
    def _testSimpleOneWithMultiOutput(self):
        @shellMethod(arg1=IntegerArgChecker())
        def pre(arg1=0):
            self.preCount +=1
            return MultiOutput([5+arg1, 10+arg1])
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro(arg2):
            self.proCount += 1
            return MultiOutput([arg2*arg2, arg2*arg2*arg2])
        
        @shellMethod(arg3=ArgChecker()) 
        def post(arg3):
            #print arg3
            self.assertTrue(arg3 in self.valueToTest)
            self.postCount += 1
            return MultiOutput([arg3,arg3])
        
        #simple test
        self.valueToTest = [25,125, 100, 1000]
        self.preCount = self.proCount = self.postCount = 0
        uc = UniCommand("simple test", "help me", pre, pro, post)
        engine = engineV3([uc])
        engine.execute()
        self.assertTrue(self.preCount == 1)
        self.assertTrue(self.proCount == 2)
        self.assertTrue(self.postCount == 4)

        self.valueToTest = [100, 1000, 225, 3375, 400, 8000]
        self.preCount = self.proCount = self.postCount = 0
        #uni command encapsulation test, the most used case
        engine = engineV3([uc, uc])
        engine.execute()
        self.assertTrue(self.preCount == 3)
        self.assertTrue(self.proCount == 4)
        self.assertTrue(self.postCount == 24)
        
        self.valueToTest = [225, 3375, 400, 8000, 625, 15625, 900, 27000]
        self.preCount = self.proCount = self.postCount = 0
        engine = engineV3([uc, uc, uc])
        engine.execute()
        self.assertTrue(self.preCount == 7)
        self.assertTrue(self.proCount == 8)
        self.assertTrue(self.postCount == 112)
        
        #...
    
    #test du mutlicommand
    def testMultiCommand(self):
        mc = MultiCommand("Multiple test", "help me")
        self.preCount = [0,0,0]
        self.proCount = [0,0,0]
        self.postCount = [0,0,0]
        self.valueToTest = [[25], [343], [1]]
    
        @shellMethod(arg1=IntegerArgChecker())
        def pre1(arg1=0):
            self.preCount[0] += 1
            return 5+arg1
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro1(arg2):
            self.proCount[0] += 1
            return arg2*arg2
        
        @shellMethod(arg3=ArgChecker()) 
        def post1(arg3):
            self.postCount[0] += 1
            #print "post1", arg3
            self.assertTrue(arg3 in self.valueToTest[0])
            return arg3
            
        @shellMethod(arg1=IntegerArgChecker())
        def pre2(arg1=0):
            self.preCount[1] += 1
            return 7+arg1
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro2(arg2):
            self.proCount[1] += 1
            return arg2*arg2*arg2
        
        @shellMethod(arg3=ArgChecker()) 
        def post2(arg3):
            self.postCount[1] += 1
            #print "post2", arg3
            self.assertTrue(arg3 in self.valueToTest[1])
            return arg3
            
        @shellMethod(arg1=IntegerArgChecker())
        def pre3(arg1=0):
            self.preCount[2] += 1
            return 1+arg1
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro3(arg2):
            self.proCount[2] += 1
            return arg2*arg2*arg2*arg2
        
        @shellMethod(arg3=ArgChecker()) 
        def post3(arg3):
            self.postCount[2] += 1
            #print "post3", arg3
            self.assertTrue(arg3 in self.valueToTest[2])
            return arg3
            
        mc.addProcess(pre1,pro1,post1)
        mc.addProcess(pre2,pro2,post2)
        mc.addProcess(pre3,pro3,post3)
        
        engine = engineV3([mc])
        engine.execute()
                
        for c in self.preCount:
            self.assertTrue(c == 1)

        for c in self.proCount:
            self.assertTrue(c == 1)
        
        for c in self.postCount:
            self.assertTrue(c == 1)
    
        self.preCount = [0,0,0]
        self.proCount = [0,0,0]
        self.postCount = [0,0,0]
        self.valueToTest = [[100, 1728, 1296, 144, 36], [1728, 144, 2744, 4096, 512], [1296, 4096, 36, 512, 16]]
        engine = engineV3([mc, mc])
        print
        engine.execute()
        
        for c in self.preCount:
            self.assertTrue(c == 4)

        for c in self.proCount:
            self.assertTrue(c == 3)
        
        for c in self.postCount:
            self.assertTrue(c == 6)
            

        self.preCount = [0,0,0]
        self.proCount = [0,0,0]
        self.postCount = [0,0,0]
        self.valueToTest = [[225, 4913, 14641, 289, 6859, 28561, 121, 2197, 2401, 361, 169, 49], [4913, 289, 6859, 28561, 2197, 361, 9261, 50625, 169, 3375, 6561, 729], [14641, 28561, 121, 2197, 2401, 28561, 50625, 169, 3375, 6561, 49, 729, 81]]
        engine = engineV3([mc, mc, mc])
        print
        engine.execute()
        
        for c in self.preCount:
            self.assertTrue(c == 13)

        for c in self.proCount:
            self.assertTrue(c == 9)
        
        for c in self.postCount:
            self.assertTrue(c == 27)
            

    #TODO test du mutliOutput avec multicommand
    def testMultiOuputAndMultiCommand(self):
        pass
    
    #TODO test du multiOutput avec multicommand et limite de commande
    def testMultiOuputAndMultiCommandAmdCommandLimit(self):
        pass
    
    #TODO yeaah et maintenant plus que 400 lignes de code restantes sur les 575...
        #oui mais avec le execute complétement testé, il sera moins necessaire de faire des vérifications avancées
    
if __name__ == '__main__':
    unittest.main()
