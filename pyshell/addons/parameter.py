#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.arg.decorator     import shellMethod
from pyshell.arg.argchecker    import defaultInstanceArgChecker,listArgChecker, environmentParameterChecker, tokenValueArgChecker, stringArgChecker, booleanValueArgChecker, contextParameterChecker
from pyshell.command.command   import UniCommand
from pyshell.loader.command    import registerStopHelpTraversalAt, registerCommand, registerSetTempPrefix
from pyshell.utils.constants   import PARAMETER_NAME, CONTEXT_ATTRIBUTE_NAME, ENVIRONMENT_ATTRIBUTE_NAME, ENVIRONMENT_PARAMETER_FILE_KEY, VARIABLE_ATTRIBUTE_NAME, CONTEXT_EXECUTION_KEY, CONTEXT_EXECUTION_SCRIPT
from pyshell.utils.exception   import ListOfException, DefaultPyshellException, PyshellException
from pyshell.utils.misc        import createParentDirectory
from pyshell.utils.postProcess import listResultHandler,printColumn, listFlatResultHandler,printColumnWithouHeader
from pyshell.utils.parsing     import escapeString
from pyshell.utils.printing    import formatBolt, formatOrange
from pyshell.system.procedure  import ProcedureFromFile
from pyshell.system.container  import ParameterContainer
from pyshell.system.parameter  import Parameter, isAValidStringPath
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.context    import ContextParameter
from pyshell.system.variable   import VarParameter
import os 

## CONSTANT SECTION ##

AVAILABLE_TYPE = {"any"     :defaultInstanceArgChecker.getArgCheckerInstance,
                  "string"  :defaultInstanceArgChecker.getStringArgCheckerInstance, 
                  "integer" :defaultInstanceArgChecker.getIntegerArgCheckerInstance,
                  "boolean" :defaultInstanceArgChecker.getbooleanValueArgCheckerInstance, 
                  "float"   :defaultInstanceArgChecker.getFloatTokenArgCheckerInstance,
                  "filePath":defaultInstanceArgChecker.getFileChecker}
                  
ENVIRONMENT_SET_PROPERTIES = {"readonly":("setReadOnly",defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),),
                              "removable":("setRemovable",defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),),
                              "transient":("setTransient",defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),)}
                          
CONTEXT_SET_PROPERTIES = {"index_transient":("setTransientIndex",defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),),
                          "defaultIndex":("setDefaultIndex",defaultInstanceArgChecker.getIntegerArgCheckerInstance(),),
                          "index":("setIndex",defaultInstanceArgChecker.getIntegerArgCheckerInstance(),)}
CONTEXT_SET_PROPERTIES.update(ENVIRONMENT_SET_PROPERTIES)

ENVIRONMENT_GET_PROPERTIES = {"readonly":"isReadOnly",
                              "removable":"isRemovable",
                              "transient":"isTransient"}
                          
CONTEXT_GET_PROPERTIES = {"index_transient":"isTransientIndex",
                          "defaultIndex":"getDefaultIndex",
                          "index":"getIndex"}
CONTEXT_GET_PROPERTIES.update(ENVIRONMENT_GET_PROPERTIES)

## FUNCTION SECTION ##

#################################### GENERIC METHOD ####################################

def getParameter(key,parameters,attributeType, startWithLocal = True, exploreOtherLevel=True, perfectMatch = False):
    if not hasattr(parameters, attributeType):
        raise Exception("Unknow parameter type '"+str(attributeType)+"'")

    container = getattr(parameters, attributeType)
    param = container.getParameter(key, perfectMatch = perfectMatch, localParam = startWithLocal, exploreOtherLevel=exploreOtherLevel)
    
    if param is None:
        raise Exception("Unknow parameter of type '"+str(attributeType)+"' with key '"+str(key)+"'")

    return param

def setProperties(key, propertyInfo, propertyValue, parameters, attributeType, startWithLocal = True, exploreOtherLevel=True, perfectMatch = False):
    
    propertyName, propertyChecker = propertyInfo
    param = getParameter(key, parameters, attributeType, startWithLocal, exploreOtherLevel, perfectMatch)
    
    meth = getattr(param, propertyName)
    
    if meth is None:
        raise Exception("Unknown property '"+str(propertyName)+"', one of these was expected: readonly/removable/transient/index_transient")
    
    meth(propertyChecker.getValue(propertyValue,"value",0))
        
def getProperties(key, propertyName, parameters, attributeType, startWithLocal = True, exploreOtherLevel=True, perfectMatch = False):
    param = getParameter(key, parameters, attributeType, startWithLocal, exploreOtherLevel, perfectMatch)
    
    meth = getattr(param, propertyName)
    
    if meth is None:
        raise Exception("Unknown property '"+str(propertyName)+"', one of these was expected: readonly/removable/transient/index_transient")
    
    return meth()
        
def listProperties(key, parameters, attributeType, startWithLocal = True, exploreOtherLevel=True, perfectMatch = False):
    param = getParameter(key, parameters, attributeType, startWithLocal, exploreOtherLevel, perfectMatch)
    prop  = list(param.getProperties())
    prop.insert(0, (formatBolt("Key"), formatBolt("Value")) )
    return prop
    
def removeParameter(key, parameters, attributeType, startWithLocal = True, exploreOtherLevel=True):
    if not hasattr(parameters, attributeType):
        raise Exception("Unknow parameter type '"+str(attributeType)+"'")

    container = getattr(parameters, attributeType)

    if not container.hasParameter(key, perfectMatch=True, localParam = startWithLocal, exploreOtherLevel=exploreOtherLevel):
        return #no job to do

    container.unsetParameter(key, localParam = startWithLocal, exploreOtherLevel=exploreOtherLevel)

def _listGeneric(parameters, attributeType, key, formatValueFun, getTitleFun, startWithLocal = True, exploreOtherLevel=True):
    #TODO re-apply a width limit on the printing, too big value will show a really big print on the terminal
        #use it in printing ?
            #nope because we maybe want to print something on the several line
            
        #an util function allow to retrieve the terminal width
            #if in shell only 
            #or script ? without output redirection

    #TODO try to display if global or local
        #don't print that column if exploreOtherLevel == false
        
        #for context and env, use the boolean lockEnabled
            #but for the var ?

    if not hasattr(parameters, attributeType):
        raise Exception("Unknow parameter type '"+str(attributeType)+"'")

    container = getattr(parameters, attributeType)

    if key is None:
        key = ""

    #retrieve all value from corresponding mltries
    dico = container.buildDictionnary(key,startWithLocal,exploreOtherLevel)

    toRet = [] 
    for subk,subv in dico.items():
        toRet.append( formatValueFun(subk, subv, formatOrange) )
    
    if len(toRet) == 0:
        return [("No item available",)]
    
    toRet.insert(0, getTitleFun(formatBolt) )
    return toRet

def _parameterRowFormating(key, paramItem, valueFormatingFun):

    if paramItem.isAListType():
        value = ', '.join(str(x) for x in paramItem.getValue())
    else:
        value = str(paramItem.getValue())

    return ("  "+".".join(key), valueFormatingFun(value), )

def _parameterGetTitle(titleFormatingFun):
    return (" "+titleFormatingFun("Name"), titleFormatingFun("Value"), )


@shellMethod(parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             key       = stringArgChecker())
def listParameter(parameters, key=None):
    toPrint = []
    for subcontainername in ParameterContainer.SUBCONTAINER_LIST:
        if not hasattr(parameters, subcontainername):
            raise Exception("Unknow parameter type '"+str(attributeType)+"'")
            
        toPrint.append(formatBolt(subcontainername.upper()))
        toPrint.extend(_listGeneric(parameters, subcontainername, key, _parameterRowFormating, _parameterGetTitle))
        
    return toPrint

@shellMethod(filePath  = environmentParameterChecker(ENVIRONMENT_PARAMETER_FILE_KEY),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def loadParameter(filePath, parameters):
    "load parameters from the settings file"

    if os.path.exists(filePath.getValue()):
        afile = ProcedureFromFile(filePath.getValue())
        afile.setErrorGranularity(None) #never stop to execute
        afile.execute(parameters=parameters)
    else:
        saveParameter(filePath, parameters)

@shellMethod(filePath  = environmentParameterChecker(ENVIRONMENT_PARAMETER_FILE_KEY),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def saveParameter(filePath, parameters):
    "save not transient parameters to the settings file"

    #TODO is there something to save ?
        #SOLUTION1 should compare the content of the file, the memory and the starting parameter...
        #SOLUTION2 historized parameters
            #store old value, when it has been change and by what
    
    filePath = filePath.getValue()

    #create directory if needed
    createParentDirectory(filePath)
    
    with open(filePath, 'wb') as configfile:
        for subcontainername in ParameterContainer.SUBCONTAINER_LIST:
            container = getattr(parameters, subcontainername)
            dico = container.buildDictionnary("", localParam = False, exploreOtherLevel=False)

            for key, parameter in dico.items():
                if parameter.isTransient():
                    continue

                if parameter.isAListType():
                    configfile.write( subcontainername+" create "+parameter.typ.checker.getTypeName()+" "+".".join(key)+" "+" ".join( escapeString(str(x)) for x in parameter.getValue())+" -noCreationIfExist true -localVar false\n" )
                else:
                    configfile.write( subcontainername+" create "+parameter.typ.getTypeName()+" "+".".join(key)+" "+escapeString(str(parameter.getValue()))+" -isList false -noCreationIfExist true -localVar false\n" )
                
                properties = parameter.getProperties()
                
                if len(properties) > 0:
                    #disable readOnly 
                    configfile.write( subcontainername + " properties set " + ".".join(key) + " readonly false\n" )

                    #set value
                    if parameter.isAListType():
                        configfile.write( subcontainername+" set "+".".join(key)+" "+" ".join(str(x) for x in parameter.getValue())+"\n" )
                    else:
                        configfile.write( subcontainername+" set "+".".join(key)+" "+str(parameter.getValue())+"\n" )

                    readOnlyValue = False
                    for propName,propValue in parameter.getProperties():
                        if propName.lower() == "readonly":#readonly should always be written on last
                            readOnlyValue = propValue
                            continue
                    
                        configfile.write( subcontainername + " properties set " + ".".join(key) + " " +propName+ " " + str(propValue) + "\n" )
                    configfile.write( subcontainername + " properties set " + ".".join(key) + " readonly "+str(readOnlyValue)+"\n" )
                configfile.write("\n")
        
def _createValuesFun(valueType, key, values, classDef, attributeType, noCreationIfExist, parameters, listEnabled, localParam = True): 
    if not hasattr(parameters, attributeType):
        raise Exception("Unknow parameter type '"+str(attributeType)+"'")

    container = getattr(parameters, attributeType)

    #build checker
    if listEnabled:
        checker = listArgChecker(valueType(),1)
    else:
        checker = valueType()
    
    if container.hasParameter(key, perfectMatch=True,localParam = localParam, exploreOtherLevel=False) and noCreationIfExist:
        return
        #no need to manage readonly or removable setting here, it will be checked in setParameter

    #check value
    value = checker.getValue(values, None, str(attributeType).title()+" "+key)
    container.setParameter(key, classDef(value, checker))
    
#################################### env management#################################### 

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values            = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parameters        = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def subtractEnvironmentValuesFun(key, values, parameters, startWithLocal = True, exploreOtherLevel=True):
    "remove some elements from an environment parameter"
    param = getParameter(key, parameters, ENVIRONMENT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)
    param.removeValues(values)

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameters        = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def removeEnvironmentContextValues(key, parameters, startWithLocal = True, exploreOtherLevel=True):
    "remove an environment parameter"
    removeParameter(key, parameters, ENVIRONMENT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameters        = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def getEnvironmentValues(key, parameters, startWithLocal = True, exploreOtherLevel=True):
    "get an environment parameter value" 
    return getParameter(key, parameters, ENVIRONMENT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel).getValue()

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values            = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1),
             parameters        = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def setEnvironmentValuesFun(key, values, parameters, startWithLocal = True, exploreOtherLevel=True):
    "set an environment parameter value"
    
    envParam = getParameter(key, parameters, ENVIRONMENT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)

    if envParam.isAListType():
        envParam.setValue(values)
    else:
        envParam.setValue(values[0])

@shellMethod(valueType         = tokenValueArgChecker(AVAILABLE_TYPE),
             key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             value             = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             isList            = booleanValueArgChecker(),
             noCreationIfExist = booleanValueArgChecker(),
             parameters        = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             localVar          = booleanValueArgChecker())
def createEnvironmentValueFun(valueType, key, value, isList=True, noCreationIfExist=False, parameters=None, localVar=True): 
    "create an environment parameter value" 
    _createValuesFun(valueType, key, value, EnvironmentParameter, ENVIRONMENT_ATTRIBUTE_NAME, noCreationIfExist, parameters, isList,localVar)

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values            = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parameters        = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def addEnvironmentValuesFun(key, values, parameters, startWithLocal = True, exploreOtherLevel=True):
    "add values to an environment parameter list"
    param = getParameter(key, parameters, ENVIRONMENT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)
    param.addValues(values)

def _envRowFormating(key, envItem, valueFormatingFun):
    if envItem.isAListType():
        return (".".join(key), "true", valueFormatingFun(', '.join(str(x) for x in envItem.getValue())), ) 
    else:
        return (".".join(key), "false", valueFormatingFun(str(envItem.getValue())), ) 

def _envGetTitle(titleFormatingFun):
    return (titleFormatingFun("Name"), titleFormatingFun("IsList"), titleFormatingFun("Value(s)"), )

@shellMethod(parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             key               = stringArgChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def listEnvs(parameter, key=None, startWithLocal = True, exploreOtherLevel=True):
    "list every existing contexts"
    return _listGeneric(parameter, ENVIRONMENT_ATTRIBUTE_NAME, key, _envRowFormating, _envGetTitle, startWithLocal, exploreOtherLevel)
    
@shellMethod(key               = stringArgChecker(),
             propertyName      = tokenValueArgChecker(ENVIRONMENT_SET_PROPERTIES),
             propertyValue     = defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def setEnvironmentProperties(key, propertyName, propertyValue, parameter, startWithLocal = True, exploreOtherLevel=True):
    "set environment property"
    setProperties(key, propertyName, propertyValue, parameter, ENVIRONMENT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)
    
@shellMethod(key               = stringArgChecker(),
             propertyName      = tokenValueArgChecker(ENVIRONMENT_GET_PROPERTIES),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def getEnvironmentProperties(key, propertyName, parameter, startWithLocal = True, exploreOtherLevel=True):
    "get environment property"
    return getProperties(key, propertyName, parameter, ENVIRONMENT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)

@shellMethod(key               = stringArgChecker(),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def listEnvironmentProperties(key,parameter, startWithLocal = True, exploreOtherLevel=True):
    "list every properties from a specific environment object"
    return listProperties(key, parameter, ENVIRONMENT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)

#################################### context management #################################### 

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values            = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parameters        = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def subtractContextValuesFun(key, values, parameters, startWithLocal = True, exploreOtherLevel=True):
    "remove some elements from a context parameter"
    param = getParameter(key, parameters, CONTEXT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)
    param.removeValues(values)

@shellMethod(valueType         = tokenValueArgChecker(AVAILABLE_TYPE), 
             key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values            = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             noCreationIfExist = booleanValueArgChecker(),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             localVar          = booleanValueArgChecker())
def createContextValuesFun(valueType, key, values, noCreationIfExist=False, parameter=None, localVar=True): 
    "create a context parameter value list"
    _createValuesFun(valueType, key, values, ContextParameter, CONTEXT_ATTRIBUTE_NAME, noCreationIfExist, parameter, True,localVar)

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def removeContextValues(key, parameter, startWithLocal = True, exploreOtherLevel=True):
    "remove a context parameter"
    removeParameter(key, parameter, CONTEXT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def getContextValues(key, parameter, startWithLocal = True, exploreOtherLevel=True): 
    "get a context parameter value" 
    return getParameter(key,parameter,CONTEXT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel).getValue()

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values            = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def setContextValuesFun(key, values, parameter, startWithLocal = True, exploreOtherLevel=True):
    "set a context parameter value"
    getParameter(key,parameter,CONTEXT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel).setValue(values)

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values            = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parameters        = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def addContextValuesFun(key, values, parameters, startWithLocal = True, exploreOtherLevel=True):
    "add values to a context parameter list"    
    param = getParameter(key, parameters, CONTEXT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)
    param.addValues(values)

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             value             = defaultInstanceArgChecker.getArgCheckerInstance(),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def selectValue(key, value, parameter, startWithLocal = True, exploreOtherLevel=True):
    "select the value for the current context"
    getParameter(key,parameter,CONTEXT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel).setIndexValue(value)
    
@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             index             = defaultInstanceArgChecker.getIntegerArgCheckerInstance(),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def selectValueIndex(key, index, parameter, startWithLocal = True, exploreOtherLevel=True):
    "select the value index for the current context"
    getParameter(key,parameter,CONTEXT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel).setIndex(index)

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def getSelectedContextValue(key, parameter, startWithLocal = True, exploreOtherLevel=True):
    "get the selected value for the current context"
    return getParameter(key,parameter,CONTEXT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel).getSelectedValue()

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def getSelectedContextIndex(key, parameter, startWithLocal = True, exploreOtherLevel=True):
    "get the selected value index for the current context"
    return getParameter(key,parameter,CONTEXT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel).getIndex()

def _conRowFormating(key, conItem, valueFormatingFun):
    return (".".join(key), str(conItem.getIndex()), valueFormatingFun(str(conItem.getSelectedValue())), ', '.join(str(x) for x in conItem.getValue()), )

def _conGetTitle(titleFormatingFun):
    return (titleFormatingFun("Name"), titleFormatingFun("Index"), titleFormatingFun("Value"), titleFormatingFun("Values"), )

@shellMethod(parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             key               = stringArgChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def listContexts(parameter, key=None, startWithLocal = True, exploreOtherLevel=True):
    "list every existing contexts"
    return _listGeneric(parameter, CONTEXT_ATTRIBUTE_NAME, key, _conRowFormating, _conGetTitle, startWithLocal, exploreOtherLevel)
    
@shellMethod(key               = stringArgChecker(),
             propertyName      = tokenValueArgChecker(CONTEXT_SET_PROPERTIES),
             propertyValue     = defaultInstanceArgChecker.getArgCheckerInstance(),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def setContextProperties(key, propertyName, propertyValue, parameter, startWithLocal = True, exploreOtherLevel=True):
    "set a context property"
    setProperties(key, propertyName, propertyValue, parameter, CONTEXT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)
    
@shellMethod(key               = stringArgChecker(),
             propertyName      = tokenValueArgChecker(CONTEXT_GET_PROPERTIES),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def getContextProperties(key, propertyName, parameter, startWithLocal = True, exploreOtherLevel=True):
    "get a context property"
    return getProperties(key, propertyName , parameter, CONTEXT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)
    
@shellMethod(key               = stringArgChecker(),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def listContextProperties(key,parameter, startWithLocal = True, exploreOtherLevel=True):
    "list every properties of a specific context object"
    return listProperties(key, parameter, CONTEXT_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)

#################################### var management #################################### 

#################################################### beginning OF POC

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values            = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             engine            = defaultInstanceArgChecker.getEngineChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def pre_addValues(key, values, engine=None, startWithLocal = True, exploreOtherLevel=True):
    
    cmd = engine.getCurrentCommand()
    cmd.dynamicParameter["key"]               = key
    cmd.dynamicParameter["disabled"]          = False
    cmd.dynamicParameter["startWithLocal"]    = startWithLocal
    cmd.dynamicParameter["exploreOtherLevel"] = exploreOtherLevel

    return values

@shellMethod(values = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             engine = defaultInstanceArgChecker.getEngineChecker())
def pro_addValues(values, engine):

    #if no previous command, default behaviour
    if not engine.hasPreviousCommand():
        return values

    #if not, clone this command and add it at the end of cmd list
    cmd = engine.getCurrentCommand()
    cmdClone = cmd.clone()
    engine.addCommand(cmdClone, convertProcessToPreProcess = True)

    for k,v in cmd.dynamicParameter.items():
        cmdClone.dynamicParameter[k] = v

    cmd.dynamicParameter["disabled"] = True
    cmdClone.dynamicParameter["disabled"] = True

    #TODO execute previous

    return values

@shellMethod(values     = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             engine     = defaultInstanceArgChecker.getEngineChecker())
def post_addValues(values, parameters=None, engine=None):
    "add values to a var"   
    
    cmd = engine.getCurrentCommand()

    if cmd.dynamicParameter["disabled"]:
        return values

    key = cmd.dynamicParameter["key"]

    if parameters.variable.hasParameter(key,cmd.dynamicParameter["startWithLocal"],cmd.dynamicParameter["exploreOtherLevel"]):
        param = getParameter(key, parameters, VARIABLE_ATTRIBUTE_NAME,cmd.dynamicParameter["startWithLocal"],cmd.dynamicParameter["exploreOtherLevel"])
        param.addValues(values)
    else:
        parameters.variable.setParameter(key,VarParameter(values),cmd.dynamicParameter["startWithLocal"])

    return values

#################################################### END OF POC

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values            = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parameters        = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def subtractValuesVar(key, values, parameters=None, startWithLocal = True, exploreOtherLevel=True):
    "remove existing value from a variable, remove first occurence met"
    param = getParameter(key, parameters, VARIABLE_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)
    param.removeValues(values)

@shellMethod(key       = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values    = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()),
             parameter = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             localVar  = booleanValueArgChecker())
def setVar(key, values, parameter, localVar=True):
    "assign a value to a variable"
    parameter.variable.setParameter(key,VarParameter(values),localVar)

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def getVar(key, parameter, startWithLocal = True, exploreOtherLevel=True):
    "get the value of a variable"
    return getParameter(key, parameter, VARIABLE_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel).getValue()

@shellMethod(key               = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def unsetVar(key, parameter, startWithLocal = True, exploreOtherLevel=True):
    "unset a variable, no error if does not exist"
    removeParameter(key, parameter, VARIABLE_ATTRIBUTE_NAME, startWithLocal, exploreOtherLevel)

def _varRowFormating(key, varItem, valueFormatingFun):
    return (".".join(key), valueFormatingFun(', '.join(str(x) for x in varItem.getValue())), )

def _varGetTitle(titleFormatingFun):
    return ( titleFormatingFun("Name"),titleFormatingFun("Values"), )

@shellMethod(parameter         = defaultInstanceArgChecker.getCompleteEnvironmentChecker(),
             key               = stringArgChecker(),
             startWithLocal    = booleanValueArgChecker(),
             exploreOtherLevel = booleanValueArgChecker())
def listVars(parameter, key=None, startWithLocal = True, exploreOtherLevel=True):
    "list every existing variables"
    return _listGeneric(parameter, VARIABLE_ATTRIBUTE_NAME, key, _varRowFormating, _varGetTitle, startWithLocal, exploreOtherLevel)

#################################### REGISTER SECTION #################################### 

#var 
registerSetTempPrefix( (VARIABLE_ATTRIBUTE_NAME, ) )
registerCommand( ("set",) ,                    post=setVar)
registerCommand( ("create",) ,                 post=setVar) #compatibility issue
registerCommand( ("get",) ,                    pre=getVar, pro=listResultHandler)
registerCommand( ("unset",) ,                  pro=unsetVar)
registerCommand( ("list",) ,                   pre=listVars, pro=printColumn)
registerCommand( ("add",) ,                    pre=pre_addValues, pro=pro_addValues, post=post_addValues)
registerCommand( ("subtract",) ,               post=subtractValuesVar)
registerStopHelpTraversalAt( (VARIABLE_ATTRIBUTE_NAME,) )

#context 
registerSetTempPrefix( (CONTEXT_ATTRIBUTE_NAME, ) )
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
registerStopHelpTraversalAt( (CONTEXT_ATTRIBUTE_NAME,"select") )
registerCommand( ("properties","list"),    pre=listContextProperties, pro=printColumn) 
registerCommand( ("list",) ,               pre=listContexts, pro=printColumn)
registerCommand( ("properties","set") ,    pro=setContextProperties)
registerCommand( ("properties","get"),     pre=getContextProperties, pro=listFlatResultHandler)
registerStopHelpTraversalAt( (CONTEXT_ATTRIBUTE_NAME,"properties") )
registerStopHelpTraversalAt( (CONTEXT_ATTRIBUTE_NAME,) )

#env 
registerSetTempPrefix( (ENVIRONMENT_ATTRIBUTE_NAME, ) )
registerCommand( ("list",) ,            pro=listEnvs,   post=printColumn )
registerCommand( ("create",),           post=createEnvironmentValueFun)
registerCommand( ("get",) ,             pre=getEnvironmentValues, pro=listResultHandler)
registerCommand( ("unset",) ,           pro=removeEnvironmentContextValues)
registerCommand( ("set",) ,             post=setEnvironmentValuesFun)
registerCommand( ("add",) ,             post=addEnvironmentValuesFun)
registerCommand( ("subtract",) ,        post=subtractEnvironmentValuesFun)
registerCommand( ("properties","set"),  pro=setEnvironmentProperties) 
registerCommand( ("properties","get"),  pre=getEnvironmentProperties, pro=listFlatResultHandler) 
registerCommand( ("properties","list"), pre=listEnvironmentProperties, pro=printColumn) 
registerStopHelpTraversalAt( (ENVIRONMENT_ATTRIBUTE_NAME,"properties",) )
registerStopHelpTraversalAt( (ENVIRONMENT_ATTRIBUTE_NAME,) ) 

#parameter
registerSetTempPrefix( (PARAMETER_NAME, ) )
registerCommand( ("save",) ,           pro=saveParameter)
registerCommand( ("load",) ,           pro=loadParameter)
registerCommand( ("list",) ,           pro=listParameter, post=printColumnWithouHeader)
registerStopHelpTraversalAt( (PARAMETER_NAME,) )
    
