#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.command.engine import *
from pyshell.command.command import *
from pyshell.arg.decorator import shellMethod
from pyshell.arg.argchecker import ArgChecker, IntegerArgChecker

#TODO pour l'instant dans les tests, on ne tiens pas compte de
    #-args (engine)
    #-useArgs (MultiCommand)
    #-enable (MultiCommand)

#TODO choses qui ne vont pas dans ces tests :
	#-s'il n'y a qu'un argument l'ensemble des args ne lui est pas lié automatiquement
		#ok le comportement correcte a avoir
			#s'il n'y a qu'un args, on bind to sur lui
			#s'il n'y a pas d'arg, pas grave
			#s'il y a plusieurs args, on doit faire sauter une exception a l'ajout du process
	#-pas vraiment un probleme mais obligation d'avoir un retour dans le post pour ce cas ci, sinon l'encapsulation ne marche pas
		#-car arg3 n'a pas de valeur par défaut

#TODO TO TEST
	#_computeTheNextChildToExecute
	#_executeMethod
	#stopExecution

def noneFun():
    pass

class EngineCoreTest(unittest.TestCase):
    def setUp(self):
        pass

    #__init__
    def testInit(self):
        #check list
        self.assertRaises(executionInitException,engineV3,None, [])
        self.assertRaises(executionInitException,engineV3,[], [])
        self.assertRaises(executionInitException,engineV3,42, [])
        
        #check command
        mc = MultiCommand("Multiple test", "help me")
        self.assertRaises(executionInitException,engineV3,[mc], [[]])
        
        mc.addProcess(noneFun,noneFun,noneFun)
        self.assertRaises(executionInitException,engineV3,[mc, 42], [[], []])
        
        mc.dymamicCount = 42
        e = engineV3([mc], [[]])
        self.assertIs(e.cmdList[0],mc)
        self.assertEqual(mc.dymamicCount, 0) #check the call on reset
        
        mc.addProcess(noneFun,noneFun,noneFun) #because the reset with the dynamic at 42 will remove every command...
        
        #empty dict
        self.assertIsInstance(e.env,dict)
        self.assertEqual(len(e.env), 0)
        
        #nawak dico
        self.assertRaises(executionInitException,engineV3,[mc], 42)
        
        #non empty dico
        a = {}
        a["ddd"] = 53
        a[88] = "plop"
        e = engineV3([mc], [[]],a)
        self.assertIsInstance(e.env,dict)
        self.assertEqual(len(e.env), 2)

    def testExecuteSimpleOne(self):
        @shellMethod(arg1=IntegerArgChecker())
        def pre(arg1=0):
            self.preCount +=1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return 5+arg1
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro(arg2):
            self.proCount += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return arg2*arg2
        
        @shellMethod(arg3=ArgChecker()) 
        def post(arg3):
            self.assertTrue(arg3 == self.valueToTest)
            self.postCount += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return arg3 #needed to the next post method in case of encapsulation
        
        #simple test
        self.valueToTest = 25
        self.preCount = self.proCount = self.postCount = 0
        uc = UniCommand("simple test", pre, pro, post)
        self.engine = engineV3([uc], [[]])
        self.engine.execute()
        self.assertEqual(self.preCount,1)
        self.assertEqual(self.proCount,1)
        self.assertEqual(self.postCount,1)
        
        self.valueToTest = 100
        self.preCount = self.proCount = self.postCount = 0
        #uni command encapsulation test, the most used case
        self.engine = engineV3([uc, uc], [[], []])
        self.engine.execute()
        self.assertEqual(self.preCount ,2)
        self.assertEqual(self.proCount,1)
        self.assertEqual(self.postCount,2)
        
        self.valueToTest = 225
        self.preCount = self.proCount = self.postCount = 0
        self.engine = engineV3([uc, uc, uc], [[], [], []])
        self.engine.execute()
        self.assertEqual(self.preCount,3)
        self.assertEqual(self.proCount,1)
        self.assertEqual(self.postCount,3)
        
        #...
    
    #test du mutliOutput
    def testSimpleOneWithMultiOutput(self):
        @shellMethod(arg1=IntegerArgChecker())
        def pre(arg1=0):
            self.preCount +=1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([5+arg1, 10+arg1])
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro(arg2):
            self.proCount += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([arg2*arg2, arg2*arg2*arg2])
        
        @shellMethod(arg3=ArgChecker()) 
        def post(arg3):
            #print arg3
            self.assertTrue(arg3 in self.valueToTest)
            self.postCount += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([arg3,arg3])
        
        #simple test
        self.valueToTest = [25,125, 100, 1000]
        self.preCount = self.proCount = self.postCount = 0
        uc = UniCommand("simple test", pre, pro, post)
        self.engine = engineV3([uc], [[]])
        self.engine.execute()
        self.assertEqual(self.preCount,1)
        self.assertEqual(self.proCount,2)
        self.assertEqual(self.postCount,4)

        self.valueToTest = [100, 1000, 225, 3375, 400, 8000]
        self.preCount = self.proCount = self.postCount = 0
        #uni command encapsulation test, the most used case
        self.engine = engineV3([uc, uc], [[], []])
        self.engine.execute()
        self.assertEqual(self.preCount,3)
        self.assertEqual(self.proCount,4)
        self.assertEqual(self.postCount,24)
        
        self.valueToTest = [225, 3375, 400, 8000, 625, 15625, 900, 27000]
        self.preCount = self.proCount = self.postCount = 0
        self.engine = engineV3([uc, uc, uc], [[], [], []])
        self.engine.execute()
        self.assertEqual(self.preCount,7)
        self.assertEqual(self.proCount,8)
        self.assertEqual(self.postCount,112)
        
        #...
    
    #test du mutlicommand
    def testMultiCommand(self):
        mc = MultiCommand("Multiple test")
        self.preCount = [0,0,0]
        self.proCount = [0,0,0]
        self.postCount = [0,0,0]
        self.valueToTest = [[25], [343], [1]]
    
        @shellMethod(arg1=IntegerArgChecker())
        def pre1(arg1=0):
            self.preCount[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return 5+arg1
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro1(arg2):
            self.proCount[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return arg2*arg2
        
        @shellMethod(arg3=ArgChecker()) 
        def post1(arg3):
            self.postCount[0] += 1
            #print "post1", arg3
            self.assertTrue(arg3 in self.valueToTest[0])
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return arg3
            
        @shellMethod(arg1=IntegerArgChecker())
        def pre2(arg1=0):
            self.preCount[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return 7+arg1
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro2(arg2):
            self.proCount[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return arg2*arg2*arg2
        
        @shellMethod(arg3=ArgChecker()) 
        def post2(arg3):
            self.postCount[1] += 1
            #print "post2", arg3
            self.assertTrue(arg3 in self.valueToTest[1])
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return arg3
            
        @shellMethod(arg1=IntegerArgChecker())
        def pre3(arg1=0):
            self.preCount[2] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return 1+arg1
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro3(arg2):
            self.proCount[2] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return arg2*arg2*arg2*arg2
        
        @shellMethod(arg3=ArgChecker()) 
        def post3(arg3):
            self.postCount[2] += 1
            #print "post3", arg3
            self.assertTrue(arg3 in self.valueToTest[2])
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return arg3
            
        mc.addProcess(pre1,pro1,post1)
        mc.addProcess(pre2,pro2,post2)
        mc.addProcess(pre3,pro3,post3)
        
        self.engine = engineV3([mc], [[]])
        self.engine.execute()
                
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
        self.engine = engineV3([mc, mc], [[], []])
        self.engine.execute()
        
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
        self.engine = engineV3([mc, mc, mc], [[], [], []])
        self.engine.execute()
        
        for c in self.preCount:
            self.assertTrue(c == 13)

        for c in self.proCount:
            self.assertTrue(c == 9)
        
        for c in self.postCount:
            self.assertTrue(c == 27)
            

    #test du mutliOutput avec multicommand
    def testMultiOuputAndMultiCommand(self):
        mc = MultiCommand("Multiple test")
        self.preCount = [0,0]
        self.proCount = [0,0]
        self.postCount = [0,0]
        self.valueToTest1 = [[1, 2, 3], [1, 2, 3]]
        self.valueToTest2 = [[6,7,8,4,5], [8,9,10,2,3,4]]
        self.valueToTest3 = [[36,49,64,16,25,81,100,4,9, 1296, 2401, 4096, 256, 625], [8,9,10,2,3,4, 512, 729, 1000, 8,27,64]]
    
        @shellMethod(arg1=IntegerArgChecker())
        def pre1(arg1=0):
            self.assertIn(arg1,self.valueToTest1[0])
            self.preCount[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([5+arg1, 3+arg1])
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro1(arg2):
            self.assertIn(arg2,self.valueToTest2[0])
            self.proCount[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([arg2*arg2, arg2**4])
        
        @shellMethod(arg3=ArgChecker()) 
        def post1(arg3):
            self.assertIn(arg3,self.valueToTest3[0])
            self.postCount[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([arg3,arg3])
        
        
        @shellMethod(arg1=IntegerArgChecker())
        def pre2(arg1=0):
            self.assertIn(arg1,self.valueToTest1[1])
            self.preCount[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([7+arg1, 1+arg1])
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro2(arg2):
            self.assertIn(arg2,self.valueToTest2[1])
            self.proCount[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([arg2**3, arg2])
        
        @shellMethod(arg3=ArgChecker()) 
        def post2(arg3):
            self.assertIn(arg3,self.valueToTest3[1])
            self.postCount[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([arg3, arg3])

            
        mc.addProcess(pre1,pro1,post1)
        mc.addProcess(pre2,pro2,post2)
        
        self.engine = engineV3([mc], [[]])
        self.engine.setData(1)
        self.engine.addData(2,1)
        self.engine.addData(3,2)
        
        self.engine.execute()
        
        for c in self.preCount:
            self.assertTrue(c == 3)

        for c in self.proCount:
            self.assertTrue(c == 6)
        
        for c in self.postCount:
            self.assertTrue(c == 12)
        
        
        self.preCount = [0,0]
        self.proCount = [0,0]
        self.postCount = [0,0]
        
        self.valueToTest1 = [[1, 2, 3, 6, 7, 8, 4, 5, 9, 10], [1, 2, 3, 6, 7, 8, 4, 5, 9, 10]] 
        self.valueToTest2 = [[5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]] #6, 7, 8, 4, 5, 9, 10 #+5 3 7 1
        self.valueToTest3 = [[256, 512, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 20736, 15, 1296, 28561, 2197, 38416, 25, 27, 10000, 6561, 4096, 36, 14641, 169, 3375, 49, 1331, 2744, 1728, 64, 50625, 196, 225, 81, 14, 83521, 343, 216, 729, 4913, 65536, 2401, 100, 16, 17, 1000, 144, 289, 625, 121, 125], [256, 512, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 20736, 15, 1296, 28561, 2197, 38416, 25, 27, 10000, 6561, 4096, 36, 14641, 169, 3375, 49, 1331, 2744, 1728, 64, 50625, 196, 225, 81, 14, 83521, 343, 216, 729, 4913, 65536, 2401, 100, 16, 17, 1000, 144, 289, 625, 121, 125]]
        
        self.engine = engineV3([mc, mc], [[], []])
        self.engine.setData(1)
        self.engine.addData(2,1)
        self.engine.addData(3,2)
        self.engine.execute()
        
        for c in self.preCount:
            self.assertIs(c,15)

        for c in self.proCount:
            self.assertTrue(c == 24)
        
        for c in self.postCount:
            self.assertTrue(c == 144)
        
        #it's too big with three command...
    
    #test du multiOutput avec multicommand et limite de commande
    def testMultiOuputAndMultiCommandAmdCommandLimit(self):
        @shellMethod(arg1=IntegerArgChecker())
        def pre1(arg1=0):
            self.assertIn(arg1,self.valueToTest1[0])
            self.preCount[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([5+arg1, 3+arg1])
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro1(arg2):
            self.assertIn(arg2,self.valueToTest2[0])
            self.proCount[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([arg2*arg2, arg2**4])
        
        @shellMethod(arg3=ArgChecker()) 
        def post1(arg3):
            self.assertIn(arg3,self.valueToTest3[0])
            self.postCount[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([arg3,arg3])
        
        
        @shellMethod(arg1=IntegerArgChecker())
        def pre2(arg1=0):
            self.assertIn(arg1,self.valueToTest1[1])
            self.preCount[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([7+arg1, 1+arg1])
        
        @shellMethod(arg2=IntegerArgChecker())
        def pro2(arg2):
            self.assertIn(arg2,self.valueToTest2[1])
            self.proCount[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([arg2**3, arg2])
        
        @shellMethod(arg3=ArgChecker()) 
        def post2(arg3):
            self.assertIn(arg3,self.valueToTest3[1])
            self.postCount[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmdList)
            return MultiOutput([arg3, arg3])

        mc = MultiCommand("Multiple test")
        mc.addProcess(pre1,pro1,post1)
        mc.addProcess(pre2,pro2,post2)
        
        self.preCount = [0,0]
        self.proCount = [0,0]
        self.postCount = [0,0]
        self.valueToTest1 = [[1, 2, 3], []]
        self.valueToTest2 = [[6,7,8,4,5], []]
        self.valueToTest3 = [[36,49,64,16,25, 1296, 2401, 4096, 256, 625], []]
        self.engine = engineV3([mc], [[]])
        self.engine.setData(1)
        self.engine.addData(2,1)
        self.engine.addData(3,2)
        #engine.setCmdRange(0,1)
        self.engine.disableSubCommandInCurrentDataBunchMap(1)  
        self.engine.execute()
        
        self.assertIs(self.preCount[0],3)
        self.assertIs(self.proCount[0],6)
        self.assertIs(self.postCount[0],12)
        self.assertIs(self.preCount[1],0)
        self.assertIs(self.proCount[1],0)
        self.assertIs(self.postCount[1],0)
        
        #limit the second command
        self.preCount = [0,0]
        self.proCount = [0,0]
        self.postCount = [0,0]
        self.valueToTest1 = [[], [1, 2, 3]]
        self.valueToTest2 = [[], [2,3,4,8,9,10]]
        self.valueToTest3 = [[], [2,3,4,8,9,10,  8,27,64,512,729,1000]]
        self.engine = engineV3([mc], [[]])
        self.engine.setData(1)
        self.engine.addData(2,1)
        self.engine.addData(3,2)
        #engine.skipNextCommandOnTheCurrentData() #the next command will raise an exception otherwise
        #engine.setCmdRange(1,2)
        self.engine.disableSubCommandInCurrentDataBunchMap(0)
        self.engine.execute()
        
        self.assertIs(self.preCount[0],0)
        self.assertIs(self.proCount[0],0)
        self.assertIs(self.postCount[0],0)  
        self.assertIs(self.preCount[1],3)
        self.assertIs(self.proCount[1],6)
        self.assertIs(self.postCount[1],12)
        
        #no limit 1
        self.preCount = [0,0]
        self.proCount = [0,0]
        self.postCount = [0,0]
        self.valueToTest1 = [[1, 2, 3], [1, 2, 3]]
        self.valueToTest2 = [[6,7,8,4,5], [2,3,4,8,9,10]]
        self.valueToTest3 = [[36,49,64,16,25, 1296, 2401, 4096, 256, 625], [2,3,4,8,9,10,  8,27,64,512,729,1000]]
        self.engine = engineV3([mc], [[]])
        self.engine.setData(1)
        self.engine.addData(2,1)
        self.engine.addData(3,2)
        #engine.setCmdRange(0,None)
        self.engine.disableEnablingMapOnDataBunch()
        self.engine.execute()
        
        self.assertIs(self.preCount[0],3)
        self.assertIs(self.proCount[0],6)
        self.assertIs(self.postCount[0],12)
        self.assertIs(self.preCount[1],3)
        self.assertIs(self.proCount[1],6)
        self.assertIs(self.postCount[1],12)
        
        #no limit 2
        self.preCount = [0,0]
        self.proCount = [0,0]
        self.postCount = [0,0]
        self.engine = engineV3([mc], [[]])
        self.engine.setData(1)
        self.engine.addData(2,1)
        self.engine.addData(3,2)
        #engine.setCmdRange(0,2)
        self.engine.enableSubCommandInCurrentDataBunchMap(0)
        self.engine.enableSubCommandInCurrentDataBunchMap(1)
        self.engine.execute()
        
        self.assertIs(self.preCount[0],3)
        self.assertIs(self.proCount[0],6)
        self.assertIs(self.postCount[0],12)
        self.assertIs(self.preCount[1],3)
        self.assertIs(self.proCount[1],6)
        self.assertIs(self.postCount[1],12)
        
        #test with two command in the pipe
        self.preCount = [0,0]
        self.proCount = [0,0]
        self.postCount = [0,0]
        
        self.valueToTest1 = [[1, 2, 3, 6, 7, 8, 4, 5], [6, 7, 8, 4, 5]] 
        self.valueToTest2 = [[9,10,11,7,8,12,13], [7,8,9,5,6,13, 14, 15, 11, 12]]
        self.valueToTest3 = [[81,6561,100,10000,121,14641,49,2401,64,4096,144,20736,169,28561, 343,512,729,125,216,2197,2744,3375,1331,1728, 7,8,9,5,6,13, 14, 15, 11, 12],[343,512,729,125,216,2197,2744,3375,1331,1728, 7,8,9,5,6,13, 14, 15, 11, 12]]
        
        self.engine = engineV3([mc, mc], [[], []])
        self.engine.setData(1)
        self.engine.addData(2,1)
        self.engine.addData(3,2)
        #engine.setCmdRange(0,1)
        self.engine.disableSubCommandInCurrentDataBunchMap(1)
        self.engine.execute()
        
        self.assertIs(self.preCount[0],9)
        self.assertIs(self.proCount[0],12)
        self.assertIs(self.postCount[0],120)
        
        self.assertIs(self.preCount[1],6)
        self.assertIs(self.proCount[1],12)
        self.assertIs(self.postCount[1],24)

        #cas limite où tout est disable
        self.engine = engineV3([mc, mc],[[],[]])
        self.engine.stack.setEnableMapOnIndex(-1,[False,False])
        #self.engine.disableSubCommandInCurrentDataBunchMap(0)
        #self.engine.disableSubCommandInCurrentDataBunchMap(1)
        self.assertRaises(executionException, self.engine.execute)
    
    #jeu de test qui verifie la consistence de la pile a chaque iteration
    def checkStack(self,stack,cmdList):
        for data,path,typ,enablingMap in stack:
            #check data
            self.assertIsInstance(data, list)
            self.assertTrue(len(data) > 0)

            #check path
            self.assertTrue(len(path) >0 and len(path) <= len(cmdList))
            for i in range(0,len(path)):
                self.assertTrue(path[i] >= 0 and path[i] < len(cmdList[i]))
                
            cmd = cmdList[len(path)-1]
            
            #check type
            self.assertTrue(typ == PREPROCESS_INSTRUCTION or typ == PROCESS_INSTRUCTION or typ == POSTPROCESS_INSTRUCTION)
            
            #check enablingMap
            if enablingMap != None:
                self.assertEqual(type(enablingMap), list)
                self.assertEqual(len(enablingMap), len(cmd))
                for b in enablingMap:
                    self.assertTrue(b or not b)

            #an index can not be set if it is disabled in map or in cmd
            c,u,e = cmd[path[-1]]
            self.assertTrue(e and (enablingMap == None or enablingMap[path[-1]]))
            
            
    def test_limitReaching(self):
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
            self.postCount += 1
            return arg3 #needed to the next post method in case of encapsulation

        #simple test
        self.valueToTest = 25
        self.preCount = self.proCount = self.postCount = 0
        uc = UniCommand("simple test", pre, pro, post)
        
        #set a large amount of data for the pre, then the pro, then the post
        engine = engineV3([uc], [[]])
        engine.stack[0] = ([5]*(DEFAULT_EXECUTION_LIMIT+1),[0],0,None )
        self.assertRaises(executionException, engine.execute)
        self.assertEqual(uc[0][0].preCount,256)
        self.assertEqual(uc[0][0].proCount,255)
        self.assertEqual(uc[0][0].postCount,255)

        engine = engineV3([uc], [[]])
        engine.stack[0] = ([5]*(DEFAULT_EXECUTION_LIMIT+1),[0],1,None )
        self.assertRaises(executionException, engine.execute)
        self.assertEqual(uc[0][0].preCount,0)
        self.assertEqual(uc[0][0].proCount,256)
        self.assertEqual(uc[0][0].postCount,255)
        
        engine = engineV3([uc], [[]])
        engine.stack[0] = ([5]*(DEFAULT_EXECUTION_LIMIT+1),[0],2,None )
        self.assertRaises(executionException, engine.execute)
        self.assertEqual(uc[0][0].preCount,0)
        self.assertEqual(uc[0][0].proCount,0)
        self.assertEqual(uc[0][0].postCount,256)        
    
        
    #getEnv
    def test_GetEnv(self):
        mc = MultiCommand("Multiple test", "help me")
        mc.addProcess(noneFun,noneFun,noneFun)  
    
        e = engineV3([mc], [[]])
        
        self.assertIs(e.env, e.getEnv())
        
        a = {}
        a["ddd"] = 53
        a[88] = "plop"
        e = engineV3([mc], [[]],a)
        
        self.assertIs(e.env, e.getEnv())
        self.assertIs(a, e.getEnv())
            
if __name__ == '__main__':
    unittest.main()
