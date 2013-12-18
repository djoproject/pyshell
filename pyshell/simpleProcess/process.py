from tries.multiLevelTries import buildDictionnary #TODO
from tries.exception import triesException #TODO

from arg.argchecker import *
from arg.decorator import *

def noneFun():
    pass
    
def exitFun():
    "Exit the program"
    exit()

#@listdecorator("args",stringArgChecker())
#@environmentdecorator("envi","envi")

@shellMethod(envi=environmentChecker("envi",environment),args=listArgChecker(stringArgChecker()))
def helperFun(envi,args):
    "print the help"
    #TODO
    #   print the complete command
    
    StartNode = None
    if len(args) > 0:
        try:
            StartNode,args = envi["levelTries"].searchEntryFromMultiplePrefix(args,True)
        except triesException as e:
            print "   "+str(e)
            return
    
    if StartNode == None:
        StartNode = envi["levelTries"].levelOneTries
    
    dico = buildDictionnary(StartNode) 
    for k in sorted(dico):
        if dico[k].showInHelp:
            print "   "+str(k)+ " : " + str(dico[k].helpMessage)

#@listdecorator("args",stringArgChecker(),1)
#@environmentdecorator("envi","envi")

@shellMethod(envi=environmentChecker("envi",environment),args=listArgChecker(stringArgChecker(),1))
def usageFun(envi,args):
    "print the usage of a fonction"
    
    if len(args) > 0:
        try:
            StartNode,args = envi["levelTries"].searchEntryFromMultiplePrefix(args)
        except triesException as e:
            print "   "+str(e)
            return
            
        print StartNode.value.usage()
                
def listAddonFun():
    "list the available addons"
    
    l = []
    if os.path.exists("./addons/"):
        for dirname, dirnames, filenames in os.walk('./addons/'):
            for name in filenames:
                if name.endswith(".py") and name != "__init__.py":
                    l.append(name[0:-3])

    return l

#@environmentdecorator("envi","envi")    

@shellMethod(envi=environmentChecker("envi",environment))
def listEnvFun(envi):
    "list all the environment variable"
    return [str(k)+" : "+str(v) for k,v in envi.iteritems()]

#@string("name")
#@environmentdecorator("executer","executer") 

@shellMethod(executer=environmentChecker("executer",environment),name=stringArgChecker())
def loadAddonFun(name,executer):
    "load an external shell addon"
    
    toLoad = "addons."+str(name)
    print "toLoad : "+str(toLoad)
    #try: #TODO enlever les commentaires
    module = __import__(toLoad) #load the module and store the __init__
    submodule = getattr(module,name)
    submodule.loader(executer)

    print "   "+toLoad+" loaded !"
    #except ImportError as ie:
    #    print "import error in <"+name+"> loading : "+str(ie)
    #except NameError as ne:
    #    print "name error in <"+name+"> loading : "+str(ne)

#@listdecorator("args",ArgChecker())

@shellMethod(args=listArgChecker(ArgChecker()))   
def echo(args):
    "echo all the args"
    
    s = ""
    for a in args:
        s += str(a)+" "
        
    return s

#@listdecorator("args",ArgChecker()) 

@shellMethod(args=listArgChecker(ArgChecker()))  
def echo16(args):
    "echo all the args in hexa"
    
    s = ""
    for a in args:
        try:
            s += "0x%x "%int(a)
        except ValueError:
            s += str(a)+" "

    return s

#@listdecorator("args",IntegerArgChecker())

@shellMethod(args=listArgChecker(IntegerArgChecker()))       
def intToAscii(args):
    #print args
    "echo all the args into chars"
    s = ""
    for a in args:
        try:
            s += chr(a)
        except ValueError:
            s += str(a)

    return s

#def preTraitementForwardArgs(args):
#    return args
    
#def printTrqceBack():
#    for k,v in sys._current_frames().iteritems():
#        print "TRQCEBACK : "+str(v.f_exc_traceback)
#        
#        if v.f_exc_traceback != None:
#            traceback.print_tb(v.f_exc_traceback)

