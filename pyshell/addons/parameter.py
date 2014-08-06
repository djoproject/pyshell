#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject,net>

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

from pyshell.loader.command            import registerStopHelpTraversalAt, registerCommand, registerSetTempPrefix
from pyshell.arg.decorator             import shellMethod
from pyshell.command.exception         import engineInterruptionException
from pyshell.utils.parameter           import CONTEXT_NAME, ENVIRONMENT_NAME, EnvironmentParameter, ContextParameter 
from pyshell.simpleProcess.postProcess import printResultHandler, stringListResultHandler,listResultHandler
from pyshell.arg.argchecker            import defaultInstanceArgChecker,listArgChecker, parameterChecker, tokenValueArgChecker, stringArgChecker, booleanValueArgChecker

### various method to manage parameter ###

def _getChecker(valueType):
    if valueType == "string":
        return defaultInstanceArgChecker.getStringArgCheckerInstance()
    elif valueType == "integer":
        return defaultInstanceArgChecker.getIntegerArgCheckerInstance()
    elif valueType == "boolean":
        return defaultInstanceArgChecker.getbooleanValueArgCheckerInstance()
    elif valueType == "float":
        return defaultInstanceArgChecker.getFloatTokenArgCheckerInstance()
    
    raise engineInterruptionException("Unknow value type", True)

#TODO
    #-create generic method
        #for which one ?
            #createContextValuesFun/createEnvironmentValueFun
            #addContextValuesFun/addEnvironmentValuesFun
    
    #-create setter/getter for parameter settings (transient/readonly/...)
    
    #reset params
        #load from default
    
    #unset/reset params from addons
        
    #print in log

    #!!!! MERGE environment and parameter !!!
        #the difference between both is difficult to understand

## FUNCTION SECTION ##

### parameter ### 

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             parent     = stringArgChecker())
def removeParameterValues(key, parameters, parent=None):
    "remove a value from the Parameter"

    if not parameters.hasParameter(key, parent):
        return #no job to do

    parameters.unsetParameter(key, parent)

@shellMethod(key    = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             env    = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             parent = stringArgChecker())
def getParameterValues(key, env, parent=None): 
    "get a value from the environment"
    
    if not env.hasParameter(key, parent):
        raise engineInterruptionException("Unknow parameter key", True)

    return env.getParameter(key, parent).getValue()

@shellMethod(key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values    = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1),
             #FIXME parent=stringArgChecker(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def setParameterValue(key, values, parent = None, parameter = None):
    "assign a value to a parameter"
    parameter.setParameter(key,EnvironmentParameter(', '.join(str(x) for x in values)), parent)

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             parent    = stringArgChecker(),
             key       = stringArgChecker())
def listParameter(parameter, parent=None, key=None, printParent = True):
    "list every parameter sorted by the parent name"
    if parent != None:
        if parent not in parameter.params:
            raise engineInterruptionException("unknown parameter parent <"+str(parent)+">", True) 
        
        if key != None:
            if key not in parameter.params[parent]:
                raise engineInterruptionException("unknown key <"+str(key)+"> in parent <"+str(parent)+">", True) 
    
            return (str(parent)+"."+str(key)+" : \""+str(parameter.params[parent][key])+"\"",)
    
        keys = (parent,)
    else:
        keys = parameter.params.keys()
    
    to_ret = []
    for k in keys:
        if printParent:
            to_ret.append(k)

        for subk,subv in parameter.params[k].items():
            if printParent:
                to_ret.append("    "+subk+" : \""+str(subv)+"\"")
            else:
                to_ret.append(subk+" : \""+str(subv)+"\"")
            
    return to_ret

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def loadParameter(parameter):
    "load parameters from the settings file"
    
    try:
        parameter.load()
    except Exception as ex:
        print("fail to load parameter fail: "+str(ex))

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def saveParameter(parameter):
    "save not transient parameters to the settings file"
    
    try:
        parameter.save()
    except Exception as ex:
        print("fail to save parameter fail: "+str(ex))
    
### env management ###

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def removeEnvironmentContextValues(key, parameters):
    "remove an environment parameter"
    removeParameterValues(key, parameters, ENVIRONMENT_NAME)

@shellMethod(key = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             env = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getEnvironmentValues(key, env):
    "get an environment parameter value" 
    return getParameterValues(key, env, ENVIRONMENT_NAME)

@shellMethod(key    = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1),
             env    = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def setEnvironmentValuesFun(key, values, env):
    "set an environment parameter value"
     
    if not env.hasParameter(key, ENVIRONMENT_NAME):
        raise engineInterruptionException("Unknow environment key <"+str(key)+">", True)

    envParam = env.getParameter(key, ENVIRONMENT_NAME)

    if isinstance(envParam.typ, listArgChecker):
        envParam.setValue(values)
    else:
        envParam.setValue(values[0])

@shellMethod(valueType       = tokenValueArgChecker({"string":"string", "integer":"integer", "boolean":"boolean", "float":"float"}),
             key             = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             value           = defaultInstanceArgChecker.getArgCheckerInstance(),
             noErrorIfExists = booleanValueArgChecker(),
             env             = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def createEnvironmentValueFun(valueType, key, value, noErrorIfExists=False, env=None): 
    "create an environment parameter value" 
    if env.hasParameter(key,ENVIRONMENT_NAME):
        if noErrorIfExists:
            #TODO value assign

            return 

    #build checker
    checker = _getChecker(valueType)
    
    #check value
    value = checker.getValue(value, None, "Environment "+key)
    env.setParameter(key, EnvironmentParameter(value, checker),ENVIRONMENT_NAME)

@shellMethod(valueType = tokenValueArgChecker({"string":"string", "integer":"integer", "boolean":"boolean", "float":"float"}), 
             key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values    = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             #FIXME noErrorIfExists=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             env       = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def createEnvironmentValuesFun(valueType, key, values, noErrorIfExists=False, env=None): 
    "create an environment parameter value list" 
    if env.hasParameter(key,ENVIRONMENT_NAME):
        if noErrorIfExists:
            #TODO value assign

            return 

    #build checker
    checker = listArgChecker(_getChecker(valueType),1)
    
    #check value
    value = checker.getValue(values, None, "Environment "+key)
    env.setParameter(key, EnvironmentParameter(value, checker),ENVIRONMENT_NAME)

@shellMethod(key    = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             env    = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def addEnvironmentValuesFun(key, values, env):
    "add values to an environment parameter list"
     
    if not env.hasParameter(key, ENVIRONMENT_NAME):
        raise engineInterruptionException("Unknow environment key <"+str(key)+">", True)

    envParam = env.getParameter(key, ENVIRONMENT_NAME)

    if not isinstance(envParam.typ, listArgChecker):
        raise engineInterruptionException("This environment has not a list checker, can not add value", True)

    values = envParam.getValue()[:]
    values.extend(values)
    envParam.setValue(values)

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             key       = stringArgChecker())
def listEnvFun(parameter, key=None):
    "list all the environment variable"
    return listParameter(parameter, ENVIRONMENT_NAME, key, False)

### context management ###

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def removeContextValues(key, parameters):
    "remove a context parameter"
    removeParameterValues(key, parameters, CONTEXT_NAME)

@shellMethod(key = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             env = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getContextValues(key, env): 
    "get a context parameter value" 
    return getParameterValues(key, env, CONTEXT_NAME)

@shellMethod(key    = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1),
             env    = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def setContextValuesFun(key, values, env):
    "set a context parameter value"

    if not env.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = env.getParameter(key, CONTEXT_NAME)
    envParam.setValue(values)

@shellMethod(valueType = tokenValueArgChecker({"string":"string", "integer":"integer", "boolean":"boolean", "float":"float"}), 
             key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values    = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             #FIXME noErrorIfExists=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             env       = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def createContextValuesFun(valueType, key, values, noErrorIfExists=False, env=None): 
    "create a context parameter value list"
    if env.hasParameter(key,CONTEXT_NAME):
        if noErrorIfExists:
            #TODO value assign

            return 

    #build checker
    checker = listArgChecker(_getChecker(valueType),1)
    
    #check value
    value = checker.getValue(values, None, "Context "+key)
    env.setParameter(key, ContextParameter(value, checker),CONTEXT_NAME)

@shellMethod(key    = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             env    = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def addContextValuesFun(key, values, env):
    "add values to a context parameter list"
    if not env.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = env.getParameter(key, CONTEXT_NAME)
    values = envParam.getValue()[:]
    values.extend(values)
    envParam.setValue(values)


@shellMethod(key     = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             value   = defaultInstanceArgChecker.getArgCheckerInstance(),
             context = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def selectValue(key, value, context):
    "select the value for the current context"
    if not context.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = context.getParameter(key, CONTEXT_NAME)
    envParam.setIndexValue(value)
    
@shellMethod(key     = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             index   = defaultInstanceArgChecker.getIntegerArgCheckerInstance(),
             context = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def selectValueIndex(key, index, context):
    "select the value index for the current context"
    if not context.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = context.getParameter(key, CONTEXT_NAME)
    envParam.setIndex(index)

@shellMethod(key     = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             context = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getSelectedContextValue(key, context):
    "get the selected value for the current context"
    if not context.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = context.getParameter(key, CONTEXT_NAME)

    return envParam.getSelectedValue()

@shellMethod(key     = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             context = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getSelectedContextIndex(key, context):
    "get the selected value index for the current context"
    if not context.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = context.getParameter(key, CONTEXT_NAME)

    return envParam.getIndex()

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             key       = stringArgChecker())
def listContext(parameter, key=None):
    "list all the context variable"
    return listParameter(parameter, CONTEXT_NAME, key, False)

### var management ###

@shellMethod(key    = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1),
             _vars  = parameterChecker("vars"))
def setVar(key, values, _vars):
    "assign a value to a var"
    #TODO parameter.setParameter(key,EnvironmentParameter(value=values,typ=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1), transient=True), "__vars__")
    _vars.getValue()[key] = values

@shellMethod(key   = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             _vars = parameterChecker("vars"))
def getVar(key, _vars):
    "get the value of a var"
    if key not in _vars.getValue():
        raise engineInterruptionException("(getVar) Unknow var key <"+str(key)+">",True)

    return _vars.getValue()[key]

@shellMethod(key   = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             _vars = parameterChecker("vars"))
def unsetVar(key, _vars):
    "unset a var"
    if key in _vars.getValue():
        del _vars.getValue()[key]

@shellMethod(_vars = parameterChecker("vars"))
def listVar(_vars):
    "list every existing var"
    ret = []
    
    for k,v in _vars.getValue().items():
        ret.append(str(k)+" : "+str(v))
    
    return ret

### REGISTER SECTION ###

#var
registerSetTempPrefix( ("var", ) )
registerCommand( ("set",) ,                    post=setVar)
registerCommand( ("get",) ,                    pre=getVar, pro=stringListResultHandler)
registerCommand( ("unset",) ,                  pro=unsetVar)
registerCommand( ("list",) ,                   pre=listVar, pro=stringListResultHandler)
registerStopHelpTraversalAt( ("var",) )

#context
registerSetTempPrefix( ("context", ) )
registerCommand( ("unset",) ,              pro=removeContextValues)
registerCommand( ("get",) ,                pre=getContextValues, pro=listResultHandler)
registerCommand( ("set",) ,                post=setContextValuesFun)
registerCommand( ("create",) ,             post=createContextValuesFun)
registerCommand( ("add",) ,                post=addContextValuesFun)
registerCommand( ("value",) ,              pre=getSelectedContextValue, pro=printResultHandler)
registerCommand( ("index",) ,              pre=getSelectedContextIndex, pro=printResultHandler)
registerCommand( ("select", "index",) ,    post=selectValueIndex)
registerCommand( ("select", "value",) ,    post=selectValue)
registerCommand( ("list",) ,               pre=listContext, pro=stringListResultHandler)
registerStopHelpTraversalAt( ("context",) )

#parameter   
registerSetTempPrefix( ("parameter", ) )
registerCommand( ("unset",) ,            pro=removeParameterValues)
registerCommand( ("get",) ,              pre=getParameterValues, pro=listResultHandler)
registerCommand( ("set",) ,              post=setParameterValue)
registerCommand( ("list",) ,             pre=listParameter, pro=stringListResultHandler)
registerCommand( ("load",) ,             pro=loadParameter)
registerCommand( ("save",) ,             pro=saveParameter)
registerStopHelpTraversalAt( ("parameter",) )

#env
registerSetTempPrefix( ("environment", ) )
registerCommand( ("list",) ,           pro=listEnvFun,   post=stringListResultHandler)
registerCommand( ("create","single",), post=createEnvironmentValueFun)
registerCommand( ("create","list",),   post=createEnvironmentValuesFun)
registerCommand( ("get",) ,            pre=getEnvironmentValues, pro=listResultHandler)
registerCommand( ("unset",) ,          pro=removeEnvironmentContextValues)
registerCommand( ("set",) ,            post=setEnvironmentValuesFun)
registerCommand( ("add",) ,            post=addEnvironmentValuesFun)
registerStopHelpTraversalAt( ("environment",) )    
    
