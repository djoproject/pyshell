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

import sys, os

if sys.version_info.major ==2:
    import ConfigParser 
else:
    import configparser as ConfigParser

DEFAULT_PARAMETER_FILE = os.path.join(os.path.expanduser("~"), ".pyshellrc")
MAIN_CATEGORY          = "main"

TAB_LENGTH        = "TAB_LENGTH"
HISTORY_FILE_PATH = "HISTORY_FILE_PATH"
ADDONS_TO_LOAD    = "ADDONS_TO_LOAD"

DEFAULT_PARAMETER = {HISTORY_FILE_PATH:os.path.join(os.path.expanduser("~"), ".pyshell_history"),
                     TAB_LENGTH       :"4",
                     ADDONS_TO_LOAD   :""}
                     
class ParameterManager(object):
    def __init__(self, file_path = DEFAULT_PARAMETER_FILE):
        self.path = DEFAULT_PARAMETER_FILE
        self.config = ConfigParser.RawConfigParser()
        
        self.config.add_section(MAIN_CATEGORY)
        for k,v in DEFAULT_PARAMETER.items():
            self.config.set(MAIN_CATEGORY, k, str(v))
        
    def loadFile(self):
        if os.path.exists(self.path):
            try:
                self.config.read(self.path)
            except Exception as ex:
                print("(ParameterManager) loadFile, fail to read parameter file : "+str(ex))
        else:
            self.saveFile()
        
    def saveFile(self):
        try:
            with open(self.path, 'wb') as configfile:
                self.config.write(configfile)
        except Exception as ex:
            print("(ParameterManager) saveFile, fail to save parameter file : "+str(ex))
        
    def setValue(self, key, value, parent=MAIN_CATEGORY):
        self.config.set(parent, key, str(value))
        
    def getValue(self, key, parent=MAIN_CATEGORY):
        try:
            return self.config.get(parent, key)
        except NoOptionError as noe:
            print("(ParameterManager) getValue, unknow key <"+str(key)+"> : "+str(noe))
            return None
        
