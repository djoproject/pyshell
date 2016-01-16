#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

#Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.arg.argchecker     import listArgChecker, defaultInstanceArgChecker
from pyshell.system.environment import EnvironmentParameter, DEFAULT_CHECKER
from pyshell.system.parameter   import ParameterManager
from pyshell.system.settings    import LocalSettings, GlobalSettings, Settings
from pyshell.utils.constants    import EMPTY_STRING

class VariableParameterManager(ParameterManager):
    def getAllowedType(self):
        return VarParameter

class VariableSettings(Settings):
    def getProperties(self):
        return ()

class VariableLocalSettings(LocalSettings, VariableSettings):
    isReadOnly = Settings.isReadOnly
    isRemovable = Settings.isRemovable
    getProperties = VariableSettings.getProperties

    def __init__(self):
        pass
        
class VariableGlobalSettings(GlobalSettings, VariableSettings):
    isReadOnly = Settings.isReadOnly
    isRemovable = Settings.isRemovable
    getProperties = VariableSettings.getProperties

    def __init__(self, transient = False):
        GlobalSettings.__init__(self,readOnly = False, removable = True, transient = transient)
        
    def addLoader(self, loaderSignature):
        pass

class VarParameter(EnvironmentParameter):
    @staticmethod
    def getInitSettings():
        return VariableLocalSettings()

    def __init__(self,value): #value can be a list or not, it will be processed
        tmp_value_parsed = [value]
        parsed_value = []
        
        while len(tmp_value_parsed) > 0:
            value_to_parse = tmp_value_parsed
            tmp_value_parsed = []
            
            for v in value_to_parse:
                if type(v) == str or type(v) == unicode:
                    v = v.strip()
                    v = v.split(" ")

                    for subv in v:
                        if len(subv) == 0:
                            continue
                    
                        parsed_value.append(subv)
                        
                elif hasattr(v, "__iter__"):
                    value_to_parse.extend(v)
                else:
                    value_to_parse.append(str(v))

        EnvironmentParameter.__init__(self,parsed_value, typ=DEFAULT_CHECKER)    
    
    def __str__(self):
        if len(self.value) == 0:
            return EMPTY_STRING
    
        to_ret = ""
        
        for v in self.value:
            to_ret += str(v)+" "
            
        to_ret = to_ret[:-1]
            
        return to_ret
    
    def __repr__(self):
        if len(self.value) == 0:
            return "Variable (empty)"
    
        return "Variable, value: "+str(self.value)
                
    def enableGlobal(self):
        if isinstance(self.settings, VariableGlobalSettings):
            return
    
        self.settings = VariableGlobalSettings()

    def enableLocal(self):
        if isinstance(self.settings, VariableLocalSettings):
            return
    
        self.settings = VariableLocalSettings()
