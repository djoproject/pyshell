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

#TODO
    #listing with parent and key
        #does it work correctly ?
        
    #load/save 
        #if parameter is readonly AND exists
            #don't load anything from file for this parameter
                #except context index (if context)

            #so if readonly, no need to store object ?
                #no information is stored about the seed, so store it anyway
                    #seed could be addon or system

from pyshell.loader.command    import registerStopHelpTraversalAt, registerCommand, registerSetTempPrefix
from pyshell.arg.decorator     import shellMethod
from pyshell.utils.parameter   import Parameter, EnvironmentParameter, ContextParameter, VarParameter, FORBIDEN_SECTION_NAME, RESOLVE_SPECIAL_SECTION_ORDER
from pyshell.utils.postProcess import stringListResultHandler,listResultHandler,printColumn, listFlatResultHandler
from pyshell.arg.argchecker    import defaultInstanceArgChecker,listArgChecker, parameterChecker, tokenValueArgChecker, stringArgChecker, booleanValueArgChecker, contextParameterChecker
from pyshell.utils.constants   import CONTEXT_NAME, ENVIRONMENT_NAME
from pyshell.utils.printing    import formatBolt, formatOrange
from pyshell.utils.exception   import ListOfException, DefaultPyshellException, PyshellException
import os, sys

try:
    pyrev = sys.version_info.major
except AttributeError:
    pyrev = sys.version_info[0]

if pyrev == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser

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
        raise Exception("Unknown property '"+str(propertyName)+"', one of these was expected: readonly/removable/transient/index_transient")

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
        raise Exception("Unknown property '"+str(propertyName)+"', one of these was expected: readonly/removable/transient/index_transient")

"""def addValuesFun(key, values, parameters, parent):
    param = getParameter(key, parameters, parent)

    if not param.isAListType():
        raise Exception("This "+str(parent)+" parameter has not a list checker, can not add value")

    old_values = param.getValue()[:]
    old_values.extend(values)
    param.setValue(old_values)"""

def getParameter(key,parameters,parent=None):
    if not parameters.hasParameter(key, parent):
        if parent is None:
            raise Exception("Unknow parameter key '"+str(key)+"'")
        else:
            raise Exception("Unknow parameter key '"+str(key)+"' for parent '"+str(parent)+"'")

    return parameters.getParameter(key, parent)
    
def removeParameter(key, parameters, parent=None):
    if not parameters.hasParameter(key, parent):
        return #no job to do

    parameters.unsetParameter(key, parent)

"""@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             parent    = stringArgChecker(),
             key       = stringArgChecker())
def listParameter(parameter, parent=None, key=None, printParent = True, allParentExcept = ()):
    "list every parameter sorted by the parent name"
    if parent != None:
        if parent not in parameter.params:
            return ()
            #raise Exception("unknown parameter parent '"+str(parent)+"'") 
        
        if key != None:
            if key not in parameter.params[parent]:
                raise Exception("unknown key '"+str(key)+"' in parent '"+str(parent)+"'") 
    
            return (str(parent)+"."+str(key)+" : \""+repr(parameter.params[parent][key])+"\"",)
    
        keys = (parent,)
    else:
        keys = parameter.params.keys()
    
    to_ret = []
    firstKey = True
    for k in keys:
        if k in allParentExcept:
            continue
    
        if printParent:
            #empty line before title
            if firstKey:
                firstKey = False
            else:
                to_ret.append( () )
                
            to_ret.append( (k,) )

        for subk,subv in parameter.params[k].items():
            rep = repr(subv)
            
            #TODO got shell size (if shell), and set the limit in place of 100
            if len(rep) > 100:
                rep = rep[:97] + "..."
        
            if printParent:
                to_ret.append( ("    "+subk, ": \""+rep+"\"", ) )
            else:
                to_ret.append( (subk, ": \""+rep+"\"", ) )

            
    return to_ret"""

def _listGeneric(parameter, parent, key, formatValueFun, getTitleFun, forbidenParent = ()):
    #TODO re-apply a width limit on the printing
        #use it in printing ?
            #nope because we maybe want to print something on the several line
            
        #a util function allow to retrieve the terminal width
            #if in shell only 
            #or script ? without output redirection

    if parent is not None:
        if parent in forbidenParent:
            raise DefaultPyshellException("Parent '"+str(parent)+"' is not allowed to list vars", USER_ERROR)
        
        if parent not in parameter.params:
            raise DefaultPyshellException("Parent '"+str(parent)+"' does not exist", USER_WARNING)
        
        parents = (parent, )
    else:
        parents = parameter.params.keys()
        
    toRet = []
    for k in parents:
        if k in forbidenParent:
            continue
        
        if key is not None:
            if key not in parameter.params[k]:
                continue
            
            toRet.append( formatValueFun(k, key, parameter.params[k][key], formatOrange) )
            break
        
        for subk,subv in parameter.params[k].items():
            toRet.append( formatValueFun(k, subk, subv, formatOrange) )
    
    if len(toRet) == 0:
        return [("No var available",)]
    
    toRet.insert(0, getTitleFun(formatBolt) )
    return toRet

def _parameterRowFormating(parent, key, paramItem, valueFormatingFun):

    if paramItem.isAListType():
        value = ', '.join(str(x) for x in paramItem.getValue())
    else:
        value = str(paramItem.getValue())

    return (str(parent), str(key), valueFormatingFun(value), )

def _parameterGetTitle(titleFormatingFun):
    return (titleFormatingFun("Parent"), titleFormatingFun("Name"), titleFormatingFun("Value"), )


@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             parent    = stringArgChecker(),
             key       = stringArgChecker())
def listParameter(parameter, parent=None, key=None):
    return _listGeneric(parameter, parent, key, _parameterRowFormating, _parameterGetTitle)

@shellMethod(filePath  = parameterChecker("parameterFile", ENVIRONMENT_NAME),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def loadParameter(filePath, parameter):
    "load parameters from the settings file"
    
    filePath = filePath.getValue()
    
    #load params
    config = None
    if os.path.exists(filePath):
        config = ConfigParser.RawConfigParser()
        try:
            config.read(filePath)
        except Exception as ex:
            raise ParameterLoadingException("(ParameterManager) load, fail to read parameter file : "+str(ex))
    else:
        #is there at least one parameter in one of the existing category ?
        emptyParameter = True
        for parentCategoryName,categoryList in parameter.params.items():
            if len(parameter.params[parentCategoryName]) > 0:
                emptyParameter = False
                break
        
        #if no parameter file, try to create it, then return
        if not emptyParameter:
            try:
                save(filePath, parameter)
            except Exception as ex:
                raise ParameterLoadingException("(ParameterManager) load, parameter file does not exist, fail to create it"+str(ex))
            return

    #read and parse, for each section
    errorList = ListOfException()
    for section in config.sections():
        specialSectionClassToUse = None
        for specialSectionClass in RESOLVE_SPECIAL_SECTION_ORDER:
            if not specialSectionClass.isParsable(config, section):
                continue
                
            specialSectionClassToUse = specialSectionClass
            break
        if specialSectionClassToUse != None:
        
            #a parent category with a similar name can not already exist (because of the structure of the parameter file)
            if section in parameter.params:
                errorList.addException(ParameterLoadingException("Section '"+str(section)+"', a parent category with this name already exist, can not create a "+specialSectionClassToUse.getStaticName()+" with this name"))
                continue
            
            #try to parse the parameter
            try:
                argument_dico = specialSectionClassToUse.parse(config, section)
            except PyshellException as ale:
                errorList.addException(ale)
                continue
            
            if section in parameter.params[specialSectionClassToUse.getStaticName()]:
                try:
                    parameter.params[specialSectionClassToUse.getStaticName()][section].setFromFile(argument_dico)
                except Exception as ex:
                    errorList.addException(ParameterLoadingException("(ParameterManager) load, fail to set information on "+specialSectionClassToUse.getStaticName()+" '"+str(section)+"' : "+str(ex)))
                    
            else:
                try:
                    parameter.params[specialSectionClassToUse.getStaticName()][section] = specialSectionClassToUse(**argument_dico)
                except Exception as ex:
                    errorList.addException(ParameterLoadingException("(ParameterManager) load, fail to create new "+specialSectionClassToUse.getStaticName()+" '"+str(section)+"' : "+str(ex)))
                    continue
    
        ### GENERIC ### 
        else:
            if section in FORBIDEN_SECTION_NAME:
                errorList.addException(ParameterLoadingException( "(ParameterManager) load, parent section name '"+str(section)+"' not allowed"))
                continue
        
            #if section in 

            for option in config.options(section):
                if section not in parameter.params:
                    parameter.params[section] = {}
                
                parameter.params[section][option] = VarParameter(config.get(section, option))
    
    #manage errorList
    if errorList.isThrowable():
        raise errorList
    
    #parameter.load()

@shellMethod(filePath  = parameterChecker("parameterFile", ENVIRONMENT_NAME),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def saveParameter(filePath, parameter):
    "save not transient parameters to the settings file"

    filePath = filePath.getValue()

    #manage standard parameter
    config = ConfigParser.RawConfigParser()
    for parent, childs in parameter.params.items():   
        if parent in FORBIDEN_SECTION_NAME:
            continue
        
        if parent == None:
            parent = MAIN_CATEGORY
        
        for childName, childValue in childs.items():
            if isinstance(childValue, Parameter):
                if childValue.isTransient():
                    continue
            """
                value = str(childValue.getValue())
            else:"""
            
            value = str(childValue)
        
            if not config.has_section(parent):
                config.add_section(parent)

            config.set(parent, childName, value)
    
    #manage context and environment
    for s in FORBIDEN_SECTION_NAME:
        if s in parameter.params:
            for contextName, contextValue in parameter.params[s].items():
                if contextValue.isTransient():
                    continue
            
                if not config.has_section(contextName):
                    config.add_section(contextName)

                for name, value in contextValue.getParameterSerializableField().items():
                    config.set(contextName, name, value)
    
    #create config directory
    #TODO manage if the directory already exist or if it is a file
        #TODO manage it in the other place where config is saved
    if not os.path.exists(os.path.dirname(filePath)):
        os.makedirs(os.path.dirname(filePath))

    #save file
    with open(filePath, 'wb') as configfile:
        config.write(configfile)
    
    #parameter.save()
        
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

        raise Exception("Try to create a "+str(parent)+" with an existing key name '"+str(key)+"'")

    #check value
    value = checker.getValue(values, None, str(parent).title()+" "+key)
    parameters.setParameter(key, classDef(value, checker),parent)
    
#################################### env management#################################### 

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values     = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def subtractEnvironmentValuesFun(key, values, parameters):
    "remove some elements from an environment parameter"
    param = getParameter(key, parameters, ENVIRONMENT_NAME)
    param.removeValues(values)

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

    if envParam.isAListType():
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
             noErrorIfExists=booleanValueArgChecker(),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def createEnvironmentValuesFun(valueType, key, values, noErrorIfExists=False, parameters=None): 
    "create an environment parameter value list" 
    _createValuesFun(valueType, key, values, EnvironmentParameter, ENVIRONMENT_NAME, noErrorIfExists, parameters, True)

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values     = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def addEnvironmentValuesFun(key, values, parameters):
    "add values to an environment parameter list"
    param = getParameter(key, parameters, ENVIRONMENT_NAME)
    param.addValues(values)

def _envRowFormating(parent, key, envItem, valueFormatingFun):
    if envItem.isAListType():
        return (str(key), "true", valueFormatingFun(', '.join(str(x) for x in envItem.getValue())), ) 
    else:
        return (str(key), "false", valueFormatingFun(str(envItem.getValue())), ) 

def _envGetTitle(titleFormatingFun):
    return (titleFormatingFun("Name"), titleFormatingFun("IsList"), titleFormatingFun("Value(s)"), )

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             key       = stringArgChecker())
def listEnvs(parameter, key=None):
    return _listGeneric(parameter, ENVIRONMENT_NAME, key, _envRowFormating, _envGetTitle)
    
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

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values     = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def subtractContextValuesFun(key, values, parameters):
    "remove some elements from a context parameter"
    param = getParameter(key, parameters, CONTEXT_NAME)
    param.removeValues(values)

@shellMethod(valueType       = tokenValueArgChecker({"any"    :defaultInstanceArgChecker.getArgCheckerInstance,
                                               "string" :defaultInstanceArgChecker.getStringArgCheckerInstance, 
                                               "integer":defaultInstanceArgChecker.getIntegerArgCheckerInstance,
                                               "boolean":defaultInstanceArgChecker.getbooleanValueArgCheckerInstance, 
                                               "float"  :defaultInstanceArgChecker.getFloatTokenArgCheckerInstance}), 
             key             = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values          = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             noErrorIfExists = booleanValueArgChecker(),
             parameter       = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def createContextValuesFun(valueType, key, values, noErrorIfExists=False, parameter=None): 
    "create a context parameter value list"
    _createValuesFun(valueType, key, values, ContextParameter, CONTEXT_NAME, noErrorIfExists, parameter, True)

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter  = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def removeContextValues(key, parameter):
    "remove a context parameter"
    removeParameter(key, parameter, CONTEXT_NAME)

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter  = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getContextValues(key, parameter): 
    "get a context parameter value" 
    return getParameter(key,parameter,CONTEXT_NAME).getValue()

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values     = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1),
             parameter  = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def setContextValuesFun(key, values, parameter):
    "set a context parameter value"
    getParameter(key,parameter,CONTEXT_NAME).setValue(values)

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values     = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def addContextValuesFun(key, values, parameters):
    "add values to a context parameter list"    
    #addValuesFun(key, values, parameters, CONTEXT_NAME)
    param = getParameter(key, parameters, CONTEXT_NAME)
    param.addValues(values)

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

@shellMethod(key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getSelectedContextIndex(key, parameter):
    "get the selected value index for the current context"
    return getParameter(key,parameter,CONTEXT_NAME).getIndex()

def _conRowFormating(parent, key, conItem, valueFormatingFun):
    return (str(key), str(conItem.getIndex()), valueFormatingFun(str(conItem.getSelectedValue())), ', '.join(str(x) for x in conItem.getValue()), )

def _conGetTitle(titleFormatingFun):
    return (titleFormatingFun("Name"), titleFormatingFun("Index"), titleFormatingFun("Value"), titleFormatingFun("Values"), )

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             key       = stringArgChecker())
def listContexts(parameter, key=None):
    return _listGeneric(parameter, CONTEXT_NAME, key, _conRowFormating, _conGetTitle)
    
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

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values     = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parent     = stringArgChecker(),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def subtractValuesVar(key, values, parent = None, parameters=None):

    #parent must be different of forbidden name
    if parent in FORBIDEN_SECTION_NAME:
        raise Exception("parent '"+str(parent)+"' can not be used in var system")

    param = getParameter(key, parameters, parent)
    param.removeValues(values)

@shellMethod(key        = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values     = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parent     = stringArgChecker(),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def addValuesVar(key, values, parent=None, parameters=None):
    "add values to a var"    

    #parent must be different of forbidden name
    if parent in FORBIDEN_SECTION_NAME:
        raise Exception("parent '"+str(parent)+"' can not be used in var system")

    if parameters.hasParameter(key, parent):
        param = getParameter(key, parameters, parent)
        param.addValues(values)
    else:
        parameters.setParameter(key,VarParameter(values), parent)

@shellMethod(key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values    = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1),
             parent    = stringArgChecker(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def setVar(key, values, parameter, parent=None):
    "assign a value to a var"

    #parent must be different of forbidden name
    if parent in FORBIDEN_SECTION_NAME:
        raise Exception("parent '"+str(parent)+"' can not be used in var system")

    parameter.setParameter(key,VarParameter(values), parent)

@shellMethod(key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parent    = stringArgChecker(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def getVar(key, parameter, parent=None):
    "get the value of a var"

    #parent must be different of forbidden name
    if parent in FORBIDEN_SECTION_NAME:
        raise Exception("parent '"+str(parent)+"' can not be used in var system")

    return getParameter(key, parameter, parent).getValue()

@shellMethod(key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parent    = stringArgChecker(),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def unsetVar(key, parameter, parent=None):
    "unset a var"

    #parent must be different of forbidden name
    if parent in FORBIDEN_SECTION_NAME:
        raise Exception("parent '"+str(parent)+"' can not be used in var system")

    removeParameter(key, parameter, parent)

def _varRowFormating(parent, key, varItem, valueFormatingFun):
    return (str(parent), str(key), valueFormatingFun(', '.join(str(x) for x in varItem.getValue())), )

def _varGetTitle(titleFormatingFun):
    return ( titleFormatingFun("Parent"),titleFormatingFun("Name"),titleFormatingFun("Values"), )

@shellMethod(parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             parent    = stringArgChecker(),
             key       = stringArgChecker())
def listVars(parameter, parent=None, key=None):
    return _listGeneric(parameter, parent, key, _varRowFormating, _varGetTitle, FORBIDEN_SECTION_NAME)

#################################### REGISTER SECTION #################################### 

#var 
registerSetTempPrefix( ("var", ) )
registerCommand( ("set",) ,                    post=setVar)
registerCommand( ("get",) ,                    pre=getVar, pro=stringListResultHandler)
registerCommand( ("unset",) ,                  pro=unsetVar)
registerCommand( ("list",) ,                   pre=listVars, pro=printColumn)
registerCommand( ("add",) ,                    pro=addValuesVar)
registerCommand( ("subtract",) ,               post=subtractValuesVar)
registerStopHelpTraversalAt( ("var",) )

#context 
registerSetTempPrefix( ("context", ) )
registerCommand( ("unset",) ,              pro=removeContextValues)
registerCommand( ("get",) ,                pre=getContextValues, pro=listResultHandler)
registerCommand( ("set",) ,                post=setContextValuesFun)
registerCommand( ("create",) ,             post=createContextValuesFun)
registerCommand( ("add",) ,                post=addContextValuesFun)
registerCommand( ("subtract",) ,           post=subtractContextValuesFun)
registerCommand( ("value",) ,              pre=getSelectedContextValue, pro=listFlatResultHandler)
registerCommand( ("index",) ,              pre=getSelectedContextIndex, pro=listFlatResultHandler)
registerCommand( ("select", "index",) ,    post=selectValueIndex)
registerCommand( ("select", "value",) ,    post=selectValue)
registerCommand( ("list",) ,               pre=listContexts, pro=printColumn)
registerCommand( ("properties","set") ,    pro=setContextProperties)
registerCommand( ("properties","get"),     pre=getContextProperties, pro=listFlatResultHandler)
registerStopHelpTraversalAt( ("context",) )

#env 
registerSetTempPrefix( ("environment", ) )
registerCommand( ("list",) ,           pro=listEnvs,   post=printColumn )
registerCommand( ("create","single",), post=createEnvironmentValueFun)
registerCommand( ("create","list",),   post=createEnvironmentValuesFun)
registerCommand( ("get",) ,            pre=getEnvironmentValues, pro=listResultHandler)
registerCommand( ("unset",) ,          pro=removeEnvironmentContextValues)
registerCommand( ("set",) ,            post=setEnvironmentValuesFun)
registerCommand( ("add",) ,            post=addEnvironmentValuesFun)
registerCommand( ("subtract",) ,       post=subtractEnvironmentValuesFun)
registerCommand( ("properties","set"), pro=setEnvironmentProperties) 
registerCommand( ("properties","get"), pre=getEnvironmentProperties, pro=listFlatResultHandler) 
registerStopHelpTraversalAt( ("environment",) ) 

#parameter
registerSetTempPrefix( ("parameter", ) )
registerCommand( ("save",) ,           pro=saveParameter)
registerCommand( ("load",) ,           pro=loadParameter)
registerCommand( ("list",) ,           pro=listParameter, post=printColumn)
registerStopHelpTraversalAt( ("parameter",) )
    
