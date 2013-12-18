from arg import environment
from argchecker import ArgChecker,stringArgChecker,IntegerArgChecker,tokenValueArgChecker,listArgChecker,environmentChecker,ArgFeeder2,defaultValueChecker
from exception import decoratorException
import inspect


###############################################################################################
##### UTIL FUNCTION ###########################################################################
###############################################################################################

"""def __decorator_init(fun,argname,needData = True):
    try:
        fun.checker
    except AttributeError:
        fun.checker = ArgFeeder2()
    
    #new argument after a variable or default one is not allowed
    if len(fun.checker.argTypeList) > 0:
        (name,checker) = fun.checker.argTypeList[-1]
        if needData:
            #TODO devrait uniquement limiter quand maxsize est a none
            if checker.isVariableSize():
                raise decoratorException("(decorator) the previous argument <"+str(name)+"> has a variable size, you can't add a new argment <"+str(argname)+"> at function <"+fun.__name__+">")

            #condition trop contraignante, verification a l'execution 
            #if checker.hasDefault and checker.needData():
            #    if not __arg_has_default(fun,argname):
            #        raise decoratorException("(decorator) the previous argument <"+str(name)+"> has a default value, you can't add a new argment <"+str(argname)+"> without default value at function <"+fun.__name__+">")

        for (name,checker) in fun.checker.argTypeList:
            if name == argname:
                raise decoratorException("(decorator) the argument <"+str(name)+"> is already used in a previous decorator at function <"+fun.__name__+">")
"""
def __arg_has_default(fun,argname):
    inspect_result = inspect.getargspec(fun)
    
    #how much default value ?
    if inspect_result.defaults == None:
        lendefault = 0
    else:
        lendefault = len(inspect_result.defaults)
    
    #existing argument ?
    if argname not in inspect_result.args:
        raise decoratorException("(decorator) unknonw argument <"+str(argname)+"> at function <"+fun.__name__+">")

    return not ( (inspect_result.args.index(argname) < (len(inspect_result.args) - lendefault)) )

    
def __arg_get_default(fun,argname):
    inspect_result = inspect.getargspec(fun)
    
    #how much default value ?
    if inspect_result.defaults == None:
        lendefault = 0
    else:
        lendefault = len(inspect_result.defaults)
    
    #existing argument ?
    if argname not in inspect_result.args:
        raise decoratorException("(decorator) unknonw argument <"+str(argname)+"> at function <"+fun.__name__+">")

    index = inspect_result.args.index(argname)
    if not (index < (len(inspect_result.args) - lendefault)):
        return inspect_result.defaults[index - (len(inspect_result.args) - len(inspect_result.defaults))]
    
    raise decoratorException("(decorator) no default value to the argument <"+str(argname)+"> at function <"+fun.__name__+">")

def __decorator_set_checker(fun,argname,checker):
    if __arg_has_default(fun,argname):
        checker.setDefaultValue(__arg_get_default(fun,argname))

    return checker

###############################################################################################
##### DECORATOR ###############################################################################
###############################################################################################

"""def argument():
    #return decoratorChecker(argName,ArgChecker())
    return ArgChecker()

def string():
    #return decoratorChecker(argName,stringArgChecker())
    return stringArgChecker()
    
def integer(minimum=None,maximum=None):
    #return decoratorChecker(argName,IntegerArgChecker(minimum,maximum))
    return IntegerArgChecker(minimum,maximum)
    
def token(tokenDictionary):
    #return decoratorChecker(argName,tokenValueArgChecker(tokenDictionary))
    return tokenValueArgChecker(tokenDictionary)
    
def listdecorator(checker,minimum=None,maximum=None):
    #return decoratorChecker(argName,listArgChecker(checker,minimum,maximum))
    return listArgChecker(checker,minimum,maximum)
    
def environmentdecorator(argName,keyname):
    #return decoratorChecker(argName,environmentChecker(keyname,environment))
    return environmentChecker(keyname,environment)
    
def decoratorChecker(argName,checker):
    def decorator(fun):
        __decorator_init(fun,argName)
        
        fun.checker.argTypeList.append((argName,__decorator_set_checker(fun,argName,checker)))
        return fun
        
    return decorator"""
    
#def shellMethod(suffix,**argList):
def shellMethod(**argList):
    #no need to check collision key, it's a dictionary

    #check the suffix string
    """if isistance(suffix,str):
        suffix = [suffix]
    elif isistance(suffix,list):
        for s in suffix:
            if not isistance(s,str):
                raise decoratorException("(shellMethod decorator) element <"+str(s)+"> in the suffix list is not a valid string")
    else:
        raise decoratorException("(shellMethod decorator) suffix must be a string or a string list, not a <"+type(suffix)+">")"""

    #check the checkers
    for key,checker in argList.iteritems():
        if not isinstance(checker,ArgChecker):
            raise decoratorException("(shellMethod decorator) the checker linked to the key <"+key+"> is not a valid checker")

    #define decorator method
    def decorator(fun):
        try:
            fun.checker
            raise decoratorException("(decorator) the function <"+fun.__name__+"> has already a shellMethod decorator")
        except AttributeError:
            pass
    
        inspect_result = inspect.getargspec(fun)
        
        argCheckerList = []
        for argname in inspect_result.args:
            if argname in argList: #check if the argname is in the argList
                #print argList
                checker = argList[argname]
                del argList[argname]
                
                #check the compatibilty with the previous argument checker
                if checker.needData() and len(argCheckerList) > 0:
                    (previousName,previousChecker) = argCheckerList[-1]
                    
                    #check if the previous checker remain a few arg to the following or not
                    if previousChecker.isVariableSize() and previousChecker.maximumSize == None:
                        raise decoratorException("(decorator) the previous argument <"+str(previousName)+"> has an infinite variable size, you can't add a new argment <"+str(argname)+"> at function <"+fun.__name__+">")
            
                argCheckerList.append( (argname,__decorator_set_checker(fun,argname,checker)) )
            elif __arg_has_default(fun,argname): #check if the arg has a DEFAULT value
                argCheckerList.append( (argname,defaultValueChecker(__arg_get_default(fun,argname)))  )
            else:
                if argname != "self":
                    raise decoratorException("(shellMethod decorator) the arg <"+argname+"> is not used and has no default value")
        
        #All the key are used in the function call?
        string = None
        first = True
        for key,checker in argList.iteritems():
            if first:
                string = ""+key
                first = False
            else:
                string = ","+key
        
        if string != None:
            raise decoratorException("(shellMethod decorator) the following key(s) had no match in the function prototype : <"+string+">")
        
        fun.checker = ArgFeeder2(argCheckerList)
    
        return fun
    
    return decorator































