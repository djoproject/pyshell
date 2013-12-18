#!/usr/bin/python2.6
from arg.resultHandler import *
import os, sys
from arg.args import CommandExecuter
import traceback
from simpleProcess import *

#def my_excepthook(type, value, traceback):
#    print 'Unhandled error:', type, value

#sys.excepthook = my_excepthook

#def printTrqceBack():
#    for k,v in sys._current_frames().iteritems():
#        print "TRQCEBACK : "+str(v.f_exc_traceback)
#        
#        if v.f_exc_traceback != None:
#            traceback.print_tb(v.f_exc_traceback)

class shell(CommandExecuter):
    def __init__(self, prompt=None)
        CommandExecuter.__init__(self)
        if prompt != None:
            #TODO check prompt value
            self.environment["prompt"] = "rfid>"

        ## comment management ##
        c = Executer.addCommand(["%*"])
        if c != None:
            c.name        = "Comment"
            c.helpMessage = "Comment a line"
            c.showInHelp = False
            
        c = Executer.addCommand(["//*"])
        if c != None:
            c.name        = "Comment"
            c.helpMessage = "Comment a line"
            c.showInHelp = False
            
        c = Executer.addCommand(["#*"])
        if c != None:
            c.name        = "Comment"
            c.helpMessage = "Comment a line"
            c.showInHelp = False

        ## utils ##
        Executer.addCommand(CommandStrings=["exit"]         ,process=exitFun)
        Executer.addCommand(CommandStrings=["quit"]         ,process=exitFun)
        Executer.addCommand(CommandStrings=["help"]         ,process=helperFun      )
        Executer.addCommand(CommandStrings=["usage"]        ,process=usageFun       )
        
        ## debug management ##
        Executer.addCommand(CommandStrings=["empty"])
            #TODO
                #set debug [on,off,False,True, ...]
                #Executer.addCommand(CommandStrings=["t"]           ,process=printTrqceBack) 
            
        ## environment management ##
        Executer.addCommand(CommandStrings=["list","environment"] ,preProcess=listEnvFun,postProcess=stringListResultHandler)
            #TODO
                #get
                #set
        
        ## addon management ##
        Executer.addCommand(CommandStrings=["list","addon"] ,preProcess=listAddonFun,postProcess=stringListResultHandler)
        Executer.addCommand(CommandStrings=["loadaddon"]    ,process=loadAddonFun   )
            #TODO
                #load
                #unload
                #list loaded
                #list unloaded
                #list all

        ## printing management ##
        Executer.addCommand(CommandStrings=["echo"]         ,process=echo                        ,postProcess=printResultHandler)        
        Executer.addCommand(CommandStrings=["echo16"]       ,process=echo16                      ,postProcess=printResultHandler)
        Executer.addCommand(CommandStrings=["toascii"]      ,process=intToAscii           ,postProcess=printResultHandler)
            #TODO
                #tostring encoding

if __name__ == "__main__":
    s = shell()

    #is there a script in the argument
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            if s.executeFile(sys.argv[1]):
                exit()
    
    #start mainloop 
    s.mainLoop()
    
    
    
    
    
    
