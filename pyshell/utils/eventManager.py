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

EVENT_AT_STARTUP      = 0 #at application launch
EVENT_AT_EXIT         = 1 #at application exit
EVENT_AT_ADDON_LOAD   = 2 #at addon load (args=addon name)
EVENT_AT_ADDON_UNLOAD = 3 #at addon unload (args=addon name)

#XXX brainstorming
    #event avec ou sans argument ?
    
    #comment sont identifier les events
