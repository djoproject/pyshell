#!/usr/bin/python2.6
import inspect
from exception import argPostExecutionException,decoratorException
from argchecker import ArgFeeder2
from decorator import shellMethod
from argchecker import ArgChecker,listArgChecker

#
# this method check the args with respect to meth
#
# @argument args, the arguments to apply
# @argument meth, the method to wich apply the argument
# @return a dictionary with the argument bounded to the method
#
def selfArgChecker(args,meth):
    if hasattr(meth, "checker"):
        return meth.checker.checkArgs(args)
    else:
        return {} #no available binding

class Command(object):
    #def __init__(self,envi,printer,preProcess=None,process=None,argChecker=None,postProcess=None):
    def __init__(self,parentContainer = None):
        self.parentContainer = parentContainer      
        self.preInputBuffer  = None
        self.proInputBuffer  = None
        self.postInputBuffer = None

    #
    # set the next execution buffer of this command
    #
    def setBuffer(self,preBuffer,proBuffer,postBuffer):
        self.preInputBuffer  = preBuffer
        self.proInputBuffer  = proBuffer
        self.postInputBuffer = postBuffer

    #default preProcess
    #@listdecorator("args",ArgChecker())
    @shellMethod(args=listArgChecker(ArgChecker()))
    def preProcess(self,args):
        return args

    #default process
    
    #@listdecorator("args",ArgChecker())
    @shellMethod(args=listArgChecker(ArgChecker()))
    def process(self,args):
        return args
    
    #default postProcess
    #@listdecorator("args",ArgChecker())
    @shellMethod(args=listArgChecker(ArgChecker()))
    def postProcess(self,args):
        #print str(args)
        pass
        
    #
    # this method convert a string list to an arguments list, then preprocess the arguments
    #
    # @argument args : a string list, each item is an argument
    # @return : a preprocess result
    #
    def preProcessExecution(self,args):
        nextArgs = selfArgChecker(args,self.preProcess)
        return self.preProcess(**nextArgs) #may raise
        
    
    #
    # this method execute the process on the preprocess result
    # 
    # @argument args : the preprocess result
    # @return : the command result
    #    
    def ProcessExecution(self,args):
        nextArgs = selfArgChecker(args,self.process)
        return self.process(**nextArgs)
    
    #
    # this method parse the result from the processExecution
    #
    # @argument args : the process result
    # @return : the unconsumed result
    #
    def postProcessExecution(self,args):
        nextArgs = selfArgChecker(args,self.postProcess)
        return self.postProcess(**nextArgs)

#
# a multicommand will produce several process with only one call
#
class MultiCommand(list):
    def __init__(self,name,helpMessage,showInHelp=True):
        self.name = name
        self.helpMessage = helpMessage
        self.showInHelp = showInHelp
        self.usageBuilder = None
        
    def addProcess(self,preProcess=None,process=None,postProcess=None):
        c = Command(self)
             
        if preProcess != None:
            c.preProcess = preProcess
            
            if self.usageBuilder == None :
                try:
                    self.usageBuilder = preProcess.checker
                except AttributeError:
                    pass
        
        if process != None:
            c.process = process
            
            if self.usageBuilder == None :
                try:
                    self.usageBuilder = process.checker
                except AttributeError:
                    pass
            
        if postProcess != None:
            c.postProcess = postProcess
            
            if self.usageBuilder == None :
                try:
                    self.usageBuilder = postProcess.checker
                except AttributeError:
                    pass
        
        self.append(c)
        
    def usage(self):
        if self.usageBuilder == None :
            return "no args needed"
        else:
            return self.name+" "+self.usageBuilder.usage()

#
# special command class, with only one command (the starting point)
#
class UniCommand(MultiCommand):
    #def __init__(self,name,helpMessage,showInHelp=True):
    def __init__(self,name,helpMessage,preProcess=None,process=None,postProcess=None,showInHelp=True):
        MultiCommand.__init__(self,name,helpMessage,showInHelp)
        MultiCommand.addProcess(self,preProcess,process,postProcess)

    def addProcess(self,preProcess=None,process=None,postProcess=None):
        pass # blocked the procedure to add more commands

    def setBuffer(self,preBuffer,proBuffer,postBuffer):
        self[0].setBuffer(preBuffer,proBuffer,postBuffer)





