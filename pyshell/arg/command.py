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
    #TODO nettoyer, encore une raison d'etre avec le argfeeder?
        #pour l'instant oui, voir plus bas

    #check the args
    #if checker != None:
    #    argsValueDico = checker.checkArgs(args) # may raise argException
        #argsValueDico est un ordered dico, c'est necessaire pour pouvoir encapsuler les instructions avec les arguments dans l'ordre
        
    #else:
    #    argsValueDico = {}
    
    if not isinstance(args,list):
        args = [args]
    
    #check if the method has an argchecker
    try: #TODO use, test attribute
        argsValueDico = meth.checker.checkArgs(args)
        
    except AttributeError:
        argsValueDico = {}
    
    return argsValueDico    
            
    """#parse the command to execute
    inspect_result = inspect.getargspec(meth)

    #print inspect_result

    nextArgs = {}   
    if inspect_result.args != None:
        
        #how many default argument?
        if inspect_result.defaults == None:
            lendefault = 0
        else:
            lendefault = len(inspect_result.defaults)
        
        #When the command has only one unknwon arg name, we bind it to all the args
        keyList = []
        index = 0
        for argname in inspect_result.args:
            if argname != "self" and argname != "envi" and argname != "printer" and argname != "args" and (index < (len(inspect_result.args) - lendefault)) :
                keyList.append(argname)
            
            index += 1
                
        if len(keyList) == 1 and keyList[0] not in argsValueDico:
            argsValueDico[keyList[0]] = args
        
        #bind the args
        #TODO this part of code must disappear ==>
        index = 0
        for argname in inspect_result.args:
            if argname in argsValueDico:
                nextArgs[argname] = argsValueDico[argname]
                del argsValueDico[argname]
            elif argname == "self":
                pass
            #    nextArgs["self"] = self
            #elif argname == "envi":
            #    nextArgs["envi"] = envi
            #elif argname == "printer":
            #    nextArgs["printer"] = printer    
            #elif argname == "args":
                #rebuilt a list with the args
                #nextArgs["args"] = [v for (k, v) in argsValueDico.iteritems()] #argsValueDico
            #    nextArgs["args"] = args
            
            #TODO deplacer le "Default Value management" dans le arg feeder
                #deja fait
                #supprimer ici
            
            else: #Default Value               
                if index < (len(inspect_result.args) - lendefault):
                    #on assigne a None
                    #self.printOnShell("WARNING unknwon arg <"+str(argname)+"> in command "+commandToExecute.name)
                    print ("WARNING unknwon arg <"+str(argname)+"> in method "+meth.__name__)
                    nextArgs[argname] = None
                else:
                    #Si c'est un argument avec une valeur par defaut, ne pas assigner  
                    nextArgs[argname] = inspect_result.defaults[index - (len(inspect_result.args) - len(inspect_result.defaults))]

            index += 1
    
        for k in argsValueDico.keys():
            print "WARNING unused argument <"+k+"> in method "+meth.__name__
    
        #XXX <===
    
    #print nextArgs
    return nextArgs"""

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
        
        #TODO le point d'entree de chaque commande doit etre compatible, faire la verification
             
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





