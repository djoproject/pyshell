#!/usr/bin/python
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

#TODO
    #should be able to set transient on global var, so create globalSettings...

from pyshell.system.parameter import ParameterManager, LocalParameterSettings
from pyshell.system.environment import EnvironmentParameter, DEFAULT_CHECKER
from pyshell.arg.argchecker  import listArgChecker, defaultInstanceArgChecker

class VariableParameterManager(ParameterManager):
    def getAllowedType(self):
        return VarParameter

class VariableGlobalParameterSettings(LocalParameterSettings):
    def __init__(self):
        pass

    def isTransient(self):
        return False

    def isReadOnly(self):
        return False

    def isRemovable(self):
        return True

class VarParameter(EnvironmentParameter):
    @staticmethod
    def getInitSettings():
        return VariableGlobalParameterSettings()

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
        to_ret = ""
        
        for v in self.value:
            to_ret += str(v)+" "
            
        return to_ret
    
    def __repr__(self):
        return "Variable, value:"+str(self.value)
        
    def getProperties(self):
        return ()
        
    def enableGlobal(self):
        pass
