#!/usr/bin/python
from pyshell.arg.decorator import shellMethod
from pyshell.arg.argchecker import ArgChecker,listArgChecker
from exception import commandException
from utils import isAValidIndex

class MultiOutput(list): #just a marker class to differentiate an standard list from a multiple output 
    pass

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
    #default preProcess
    @shellMethod(args=listArgChecker(ArgChecker()))
    def preProcess(self,args):
        return args

    #default process
    @shellMethod(args=listArgChecker(ArgChecker()))
    def process(self,args):
        return args
    
    #default postProcess
    @shellMethod(args=listArgChecker(ArgChecker()))
    def postProcess(self,args):
        return args
    
    #this method is called on every processing to reset the internal state
    def reset(self):
        pass  #TO OVERRIDE if needed

#
# a multicommand will produce several process with only one call
#
class MultiCommand(list):
    #def __init__(self,name,helpMessage,showInHelp=True):
    def __init__(self,name,showInHelp=True):
        self.name         = name        #the name of the command
        self.helpMessage  = None #helpMessage #message to show in the help context
        self.showInHelp   = showInHelp  #is this command must appear in the help context ?
        self.usageBuilder = None        #which (pre/pro/post) process of the first command must be used to create the usage.
        
        self.onlyOnceDict = {}          #this dict is used to prevent the insertion of the an existing dynamic sub command
        self.dymamicCount = 0
        
        self.args         = None        #
        self.preCount = self.proCount = self.postCount = 0
        
    def addProcess(self,preProcess=None,process=None,postProcess=None, useArgs = True):
        c = Command()
        
        if preProcess == process == postProcess == None:
            raise commandException("(MultiCommand) addProcess, at least one of the three callable pre/pro/post object must be different of None")
        
        if preProcess != None:
            #preProcess must be callable
            if not hasattr(preProcess, "__call__"):
                raise commandException("(MultiCommand) addProcess, the given preProcess is not a callable object")
            
            #set preProcess
            c.preProcess = preProcess
            
            #check if this callable object has an usage builder
            if self.usageBuilder == None and hasattr(preProcess, "checker"):
                self.usageBuilder = preProcess.checker
                
            if self.helpMessage == None and hasattr(preProcess,"__doc__") and preProcess.__doc__ != None and len(preProcess.__doc__) > 0:
                self.helpMessage = preProcess.__doc__
        
        if process != None:
            #process must be callable
            if not hasattr(process, "__call__"):
                raise commandException("(MultiCommand) addProcess, the given process is not a callable object")
        
            #set process
            c.process = process
            
            #check if this callable object has an usage builder
            if self.usageBuilder == None and hasattr(process, "checker"):
                self.usageBuilder = process.checker
                
            if self.helpMessage == None and hasattr(process,"__doc__") and process.__doc__ != None and len(process.__doc__) > 0:
                self.helpMessage = process.__doc__
            
        if postProcess != None:
            #postProcess must be callable
            if not hasattr(postProcess, "__call__"):
                raise commandException("(MultiCommand) addProcess, the given postProcess is not a callable object")
        
            #set postProcess
            c.postProcess = postProcess
            
            if self.usageBuilder == None and hasattr(postProcess, "checker"):
                self.usageBuilder = postProcess.checker
                
            if self.helpMessage == None and hasattr(postProcess,"__doc__") and postProcess.__doc__ != None and len(postProcess.__doc__) > 0:
                self.helpMessage = postProcess.__doc__
        
        self.append( (c,useArgs,True,) )
    
    def addStaticCommand(self, cmd, useArgs = True):
        #cmd must be an instance of Command
        if not isinstance(cmd, Command):
            raise commandException("(MultiCommand) addStaticCommand, try to insert a non command object")
            
        #can't add static if dynamic in the list
        if self.dymamicCount > 0:
            raise commandException("(MultiCommand) addStaticCommand, can't insert static command while dynamic command are present, reset the MultiCommand then insert static command")
    
        #if usageBuilder is not set, take the preprocess builder of the cmd 
        if self.usageBuilder == None and hasattr(cmd.preProcess, "checker"):
            self.usageBuilder = cmd.preProcess.checker
    
        #build help message
        if self.helpMessage == None and hasattr(cmd.preProcess,"__doc__") and cmd.preProcess.__doc__ != None and len(cmd.preProcess.__doc__) > 0:
            self.helpMessage = cmd.preProcess.__doc__
    
        #add the command
        self.append( (cmd,useArgs,True,) )
    
    def usage(self):
        if self.usageBuilder == None :
            return self.name+": no args needed"
        else:
            return self.name+" "+self.usageBuilder.usage()

    def reset(self):
        #flush args
        self.args = None
        
        #remove dynamic command
        del self[len(self)-self.dymamicCount:]
        self.dymamicCount = 0
        
        #reset self.onlyOnceDict
        self.onlyOnceDict = {}
        
        #reset counter
        self.preCount = self.proCount = self.postCount = 0
        
        #reset every sub command
        for i in range(0,len(self)):
            c,a,e = self[i]
            c.preCount  = 0 #this counter is used to prevent an infinite execution of the pre process
            c.proCount  = 0 #this counter is used to prevent an infinite execution of the process
            c.postCount = 0 #this counter is used to prevent an infinite execution of the post process
            c.reset()
            self[i] = (c,a,True,)  

    def setArgs(self, args):
        if isinstance(args, MultiOutput):
            self.args = args
        else:
            self.args = MultiOutput([args])
    
    def getArgs(self):
        return self.args 

    def flushArgs(self):
        self.args = None

    def addDynamicCommand(self,c,onlyAddOnce=True, useArgs = True, enabled = True):
        #cmd must be an instance of Command
        if not isinstance(c, Command):
            raise commandException("(MultiCommand) addDynamicCommand, try to insert a non command object")
            
        #check if the method already exist in the dynamic
        h = hash(c)
        if onlyAddOnce and h in self.onlyOnceDict:
            return
            
        self.onlyOnceDict[h] = True
        
        #add the command
        self.append( (c,useArgs,enabled,) )
        self.dymamicCount += 1
        
    def enableCmd(self, index = 0):
        isAValidIndex(self, index, "enableCmd", "Command list", "MultiCommand", commandException)
        c,a,e = self[index]
        self[index] = (c, a, True,)
        
    def disableCmd(self, index = 0):
        isAValidIndex(self, index, "disableCmd", "Command list", "MultiCommand", commandException)
        c,a,e = self[index]
        self[index] = (c, a, False,)
        
    def enableArgUsage(self,index=0):
        isAValidIndex(self, index, "enableArgUsage", "Command list", "MultiCommand", commandException)
        c,a,e = self[index]
        self[index] = (c, True, e,)
        
    def disableArgUsage(self,index=0):
        isAValidIndex(self, index, "disableArgUsage", "Command list", "MultiCommand", commandException)
        c,a,e = self[index]
        self[index] = (c, False, e,)

    def isdisabledCmd(self, index = 0):
        isAValidIndex(self, index, "isdisabledCmd", "Command list", "MultiCommand", commandException)
        c,a,e = self[index]
        return not e

    def isArgUsage(self, index = 0):
        isAValidIndex(self, index, "isArgUsage", "Command list", "MultiCommand", commandException)
        c,a,e = self[index]
        return a

#
# special command class, with only one command (the starting point)
#
class UniCommand(MultiCommand):
    #def __init__(self,name,helpMessage,showInHelp=True):
    def __init__(self,name,preProcess=None,process=None,postProcess=None,showInHelp=True):
        MultiCommand.__init__(self,name,showInHelp)
        MultiCommand.addProcess(self,preProcess,process,postProcess)

    def addProcess(self,preProcess=None,process=None,postProcess=None, useArgs = True):
        pass # blocked the procedure to add more commands

    def addStaticCommand(self, cmd, useArgs = True):
        pass # blocked the procedure to add more commands


