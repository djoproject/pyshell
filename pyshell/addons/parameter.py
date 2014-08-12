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
from pyshell.utils.parameter           import CONTEXT_NAME, ENVIRONMENT_NAME, EnvironmentParameter, ContextParameter, VarParameter, FORBIDEN_SECTION_NAME
from pyshell.simpleProcess.postProcess import printResultHandler, stringListResultHandler,listResultHandler
from pyshell.arg.argchecker            import defaultInstanceArgChecker,listArgChecker, parameterChecker, tokenValueArgChecker, stringArgChecker, booleanValueArgChecker

## FUNCTION SECTION ##

#################################### GENERIC METHOD ####################################

def setProperties(key, propertyName, propertyValue, parameters, parent):
    param = getParameter(key, parameters, parent)
    
    if propertyName == "readonly":
        param.setReadOnly(propertyValue)
    elif propertyName == "removable":
        param.setRemovable(propertyValue)
    elif propertyName == "transient":
        param.setTransient(propertyValue)
    elif propertyName == "index_transient":
        param.setTransientIndex(propertyValue)
    else:
        raise Exception("Unknown property <"+str(propertyName)+">, one of these was expected: readonly/removable/transient/index_transient")

def getProperties(key, propertyName, parameters, parent):
    param = getParameter(key, parameters, parent)
    
    if propertyName == "readonly":
        return param.isReadOnly()
    elif propertyName == "removable":
        return param.isRemovable()
    elif propertyName == "transient":
        return param.isTransient()
    elif propertyName == "index_transient":
        return param.isTransientIndex()
    else:
        raise Exception("Unknown property <"+str(propertyName)+">, one of these was expected: readonly/removable/transient/index_transient")

def addValuesFun(key, values, parameters, parent):
    param = getParameter(key, parameters, parent)

    if not isinstance(param.typ, listArgChecker):
        raise Exception("This "+str(parent)+" parameter has not a list checker, can not add value")

    old_values = param.getValue()[:]
    old_values.extend(values)
    param.setValue(old_values)

def getParameter(key,parameters,parent=None):
    if not parameters.hasParameter(key, parent):
        raise Exception("Unknow parameter key <"+str(key)+">")

    return parameters.getParameter(key, parent)
    
def removeParameter(key, parameters, parent=None):
    if not parameters.hasParameter(key, parent):
        return #no job to do

    parameters.unsetParameter(key, parent)

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             parent    = stringArgChecker(),
             key       = stringArgChecker())
def listParameter(parameter, parent=None, key=None, printParent = True):
    "list every parameter sorted by the parent name"
    if parent != None:
        if parent not in parameter.params:
            return ()
            #raise Exception("unknown parameter parent <"+str(parent)+">") 
        
        if key != None:
            if key not in parameter.params[parent]:
                raise Exception("unknown key <"+str(key)+"> in parent <"+str(parent)+">") 
    
            return (str(parent)+"."+str(key)+" : \""+repr(parameter.params[parent][key])+"\"",)
    
        keys = (parent,)
    else:
        keys = parameter.params.keys()
    
    to_ret = []
    for k in keys:
        if printParent:
            to_ret.append(k)

        for subk,subv in parameter.params[k].items():
            if printParent:
                to_ret.append("    "+subk+" : \""+repr(subv)+"\"")
            else:
                to_ret.append(subk+" : \""+repr(subv)+"\"")
            
    return to_ret

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def loadParameter(parameter):
    "load parameters from the settings file"
    parameter.load()

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def saveParameter(parameter):
    "save not transient parameters to the settings file"
    parameter.save()
        
def _createValuesFun(valueType, key, values, classDef, parent, noErrorIfExists=False, parameters=None, listEnabled = False): 
    #build checker
    if listEnabled:
        checker = listArgChecker(valueType(),1)
    else:
        checker = valueType()
    
    if parameters.hasParameter(key,parent):
        if noErrorIfExists:
            value = checker.getValue(values, None, str(parent).title()+" "+key)
            parameters.setParameter(key, classDef(value, checker),parent)
            return 

        raise Exception("Try to create a "+str(parent)+" with an existing key name <"+str(key)+">")

    #check value
    value = checker.getValue(values, None, str(parent).title()+" "+key)
    parameters.setParameter(key, classDef(value, checker),parent)
    
#################################### env management#################################### 

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def removeEnvironmentContextValues(key, parameters):
    "remove an environment parameter"
    removeParameter(key, parameters, ENVIRONMENT_NAME)

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getEnvironmentValues(key, parameters):
    "get an environment parameter value" 
    return getParameter(key, parameters, ENVIRONMENT_NAME).getValue()

@shellMethod(key           = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values        = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1),
             parameters    = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def setEnvironmentValuesFun(key, values, parameters):
    "set an environment parameter value"
    
    envParam = getParameter(key, parameters, ENVIRONMENT_NAME)

    if isinstance(envParam.typ, listArgChecker):
        envParam.setValue(values)
    else:
        envParam.setValue(values[0])

@shellMethod(valueType       = tokenValueArgChecker({"any"    :defaultInstanceArgChecker.getArgCheckerInstance,
                                                     "string" :defaultInstanceArgChecker.getStringArgCheckerInstance, 
                                                     "integer":defaultInstanceArgChecker.getIntegerArgCheckerInstance,
                                                     "boolean":defaultInstanceArgChecker.getbooleanValueArgCheckerInstance, 
                                                     "float"  :defaultInstanceArgChecker.getFloatTokenArgCheckerInstance}),
             key             = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             value           = defaultInstanceArgChecker.getArgCheckerInstance(),
             noErrorIfExists = booleanValueArgChecker(),
             parameters      = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def createEnvironmentValueFun(valueType, key, value, noErrorIfExists=False, parameters=None): 
    "create an environment parameter value" 
    _createValuesFun(valueType, key, value, EnvironmentParameter, ENVIRONMENT_NAME, noErrorIfExists, parameters, False)

@shellMethod(valueType  = tokenValueArgChecker({"any"    :defaultInstanceArgChecker.getArgCheckerInstance,
                                               "string" :defaultInstanceArgChecker.getStringArgCheckerInstance, 
                                               "integer":defaultInstanceArgChecker.getIntegerArgCheckerInstance,
                                               "boolean":defaultInstanceArgChecker.getbooleanValueArgCheckerInstance, 
                                               "float"  :defaultInstanceArgChecker.getFloatTokenArgCheckerInstance}), 
             key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values     = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             #FIXME noErrorIfExists=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def createEnvironmentValuesFun(valueType, key, values, noErrorIfExists=False, parameters=None): 
    "create an environment parameter value list" 
    _createValuesFun(valueType, key, values, EnvironmentParameter, ENVIRONMENT_NAME, noErrorIfExists, parameters, True)

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values     = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def addEnvironmentValuesFun(key, values, parameters):
    "add values to an environment parameter list"
    addValuesFun(key, values, parameters, ENVIRONMENT_NAME)

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             key       = stringArgChecker())
def listEnvFun(parameter, key=None):
    "list all the environment variable"
    return listParameter(parameter, ENVIRONMENT_NAME, key, False)
    
@shellMethod(key           = stringArgChecker(),
             propertyName  = tokenValueArgChecker({"readonly":"readonly",
                                                   "removable":"removable",
                                                   "transient":"transient"}),
             propertyValue = defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             parameter     = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def setEnvironmentProperties(key, propertyName, propertyValue, parameter):
    setProperties(key, propertyName, propertyValue, parameter, ENVIRONMENT_NAME)
    
@shellMethod(key           = stringArgChecker(),
             propertyName  = tokenValueArgChecker({"readonly":"readonly",
                                                   "removable":"removable",
                                                   "transient":"transient"}),
             parameter     = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getEnvironmentProperties(key, propertyName, parameter):
    return getProperties(key, propertyName, parameter, ENVIRONMENT_NAME)

#################################### context management #################################### 

@shellMethod(valueType  = tokenValueArgChecker({"any"    :defaultInstanceArgChecker.getArgCheckerInstance,
                                               "string" :defaultInstanceArgChecker.getStringArgCheckerInstance, 
                                               "integer":defaultInstanceArgChecker.getIntegerArgCheckerInstance,
                                               "boolean":defaultInstanceArgChecker.getbooleanValueArgCheckerInstance, 
                                               "float"  :defaultInstanceArgChecker.getFloatTokenArgCheckerInstance}), 
             key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values     = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             #FIXME noErrorIfExists=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def createContextValuesFun(valueType, key, values, noErrorIfExists=False, parameter=None): 
    "create a context parameter value list"
    _createValuesFun(valueType, key, values, ContextParameter, CONTEXT_NAME, noErrorIfExists, parameter, True)

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def removeContextValues(key, parameter):
    "remove a context parameter"
    removeParameter(key, parameter, CONTEXT_NAME)

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getContextValues(key, parameter): 
    "get a context parameter value" 
    return getParameter(key,parameter,CONTEXT_NAME).getValue()

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values     = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def setContextValuesFun(key, values, parameter):
    "set a context parameter value"
    getParameter(key,parameter,CONTEXT_NAME).setValue(values)

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values     = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def addContextValuesFun(key, values, parameter):
    "add values to a context parameter list"
    addValuesFun(key, values, parameter, CONTEXT_NAME)

@shellMethod(key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             value     = defaultInstanceArgChecker.getArgCheckerInstance(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def selectValue(key, value, parameter):
    "select the value for the current context"
    getParameter(key,parameter,CONTEXT_NAME).setIndexValue(value)
    
@shellMethod(key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             index     = defaultInstanceArgChecker.getIntegerArgCheckerInstance(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def selectValueIndex(key, index, parameter):
    "select the value index for the current context"
    getParameter(key,parameter,CONTEXT_NAME).setIndex(index)

@shellMethod(key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getSelectedContextValue(key, parameter):
    "get the selected value for the current context"
    return getParameter(key,parameter,CONTEXT_NAME).getSelectedValue()

@shellMethod(key     = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getSelectedContextIndex(key, parameter):
    "get the selected value index for the current context"
    return getParameter(key,parameter,CONTEXT_NAME).getIndex()

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             key       = stringArgChecker())
def listContext(parameter, key=None):
    "list all the context variable"
    return listParameter(parameter, CONTEXT_NAME, key, False)
    
@shellMethod(key           = stringArgChecker(),
             propertyName  = tokenValueArgChecker({"readonly":"readonly",
                                                   "removable":"removable",
                                                   "transient":"transient",
                                                   "index_transient":"index_transient"}),
             propertyValue = defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             parameter     = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def setContextProperties(key, propertyName, propertyValue, parameter):
    setProperties(key, propertyName, propertyValue, parameter, CONTEXT_NAME)
    
@shellMethod(key           = stringArgChecker(),
             propertyName  = tokenValueArgChecker({"readonly":"readonly",
                                                   "removable":"removable",
                                                   "transient":"transient",
                                                   "index_transient":"index_transient"}),
             parameter     = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getContextProperties(key, propertyName, parameter):
    return getProperties(key, propertyName , parameter, CONTEXT_NAME)

#################################### var management #################################### 

@shellMethod(key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values    = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1),
             #FIXME parent    = stringArgChecker(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def setVar(key, values, parameter, parent=None):
    "assign a value to a var"

    #parent must be different of forbidden name
    if parent in FORBIDEN_SECTION_NAME:
        raise Exception("parent <"+str(parent)+"> can not be used in var system")

    parameter.setParameter(key,VarParameter(values), parent)

@shellMethod(key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parent    = stringArgChecker(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getVar(key, parameter, parent=None):
    "get the value of a var"

    #parent must be different of forbidden name
    if parent in FORBIDEN_SECTION_NAME:
        raise Exception("parent <"+str(parent)+"> can not be used in var system")

    return getParameter(key, parameter, parent).getValue()

@shellMethod(key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parent    = stringArgChecker(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def unsetVar(key, parameter, parent=None):
    "unset a var"

    #parent must be different of forbidden name
    if parent in FORBIDEN_SECTION_NAME:
        raise Exception("parent <"+str(parent)+"> can not be used in var system")

    removeParameter(key, parameter, parent)

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             key       = stringArgChecker(),
             parent    = stringArgChecker())
def listVar(parameter, key=None, parent=None):
    "list every existing var"

    #parent must be different of forbidden name
    if parent in FORBIDEN_SECTION_NAME:
        raise Exception("parent <"+str(parent)+"> can not be used in var system")

    return listParameter(parameter, parent, key, False)

#################################### REGISTER SECTION #################################### 

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
registerCommand( ("properties","set") ,    pro=setContextProperties)
registerCommand( ("properties","get"),     pre=getContextProperties, pro=printResultHandler)
registerStopHelpTraversalAt( ("context",) )

#env 
registerSetTempPrefix( ("environment", ) )
registerCommand( ("list",) ,           pro=listEnvFun,   post=stringListResultHandler)
registerCommand( ("create","single",), post=createEnvironmentValueFun)
registerCommand( ("create","list",),   post=createEnvironmentValuesFun)
registerCommand( ("get",) ,            pre=getEnvironmentValues, pro=listResultHandler)
registerCommand( ("unset",) ,          pro=removeEnvironmentContextValues)
registerCommand( ("set",) ,            post=setEnvironmentValuesFun)
registerCommand( ("save",) ,           pro=saveParameter)
registerCommand( ("properties","set"), pro=setEnvironmentProperties) 
registerCommand( ("properties","get"), pre=getEnvironmentProperties, pro=printResultHandler) 
registerStopHelpTraversalAt( ("environment",) ) 

#parameter
registerSetTempPrefix( ("parameter", ) )
registerCommand( ("add",) ,            post=addEnvironmentValuesFun)
registerCommand( ("load",) ,           pro=loadParameter)
registerCommand( ("list",) ,            pro=listParameter, post=stringListResultHandler)
registerStopHelpTraversalAt( ("parameter",) )
    
