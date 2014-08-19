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

MAUVE  = '\033[95m'
BLUE    = '\033[94m'
GREEN   = '\033[92m'
ORANGE  = '\033[93m'
RED     = '\033[91m'
ENDC    = '\033[0m'

def red(text):
    return RED+text+ENDC
    
def blue(text):
    return BLUE+text+ENDC
    
def green(text):
    return GREEN+text+ENDC
    
def orange(text):
    return ORANGE+text+ENDC
    
def mauve(text):
    return MAUVE+text+ENDC

def nocolor(text):
    return text
