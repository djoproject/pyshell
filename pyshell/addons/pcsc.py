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

from pyshell.utils.loader import *
from pyshell.arg.decorator import shellMethod
from pyshell.arg.argchecker import ArgChecker,listArgChecker, IntegerArgChecker, engineChecker, stringArgChecker, parameterChecker, tokenValueArgChecker, completeEnvironmentChecker, booleanValueArgChecker

#TODO move import from load to here
	#try/catch it then raise an adpated message

def loadPCSC():
	#load smartcard
	try:
	    from smartcard.System import readers
	    from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
	    from smartcard.ReaderMonitoring import ReaderMonitor, ReaderObserver
	    from smartcard.CardMonitoring import CardMonitor, CardObserver
	    from smartcard.CardConnection import CardConnection
	    from smartcard.ATR import ATR
	    from smartcard.pcsc.PCSCContext import PCSCContext
	    from smartcard.pcsc.PCSCExceptions import EstablishContextException

	    from smartcard.sw.ErrorCheckingChain import ErrorCheckingChain
	    from smartcard.sw.ISO7816_4ErrorChecker import ISO7816_4ErrorChecker
	    from smartcard.sw.ISO7816_8ErrorChecker import ISO7816_8ErrorChecker
	    from smartcard.sw.ISO7816_9ErrorChecker import ISO7816_9ErrorChecker
	except ImportError as ie:
	    print "failed to load smartcard : "+str(ie)
	    print "maybe the library is not installed"
	    print "http://pyscard.sourceforge.net"
	    
	    import sys
	    if(sys.platform == 'darwin'):
	        print "HINT : on macos system, try to execute this script with python2.6"

	#load context
	#not already called in an import ?
	try:
	    print "context loading... please wait"
	    PCSCContext()
	    print "context loaded"
	except EstablishContextException as e:
	    print "   "+str(e)
	    
	    import platform
	    pf = platform.system()
	    if pf == 'Darwin':
	        print "   HINT : connect a reader and use a tag/card with it, then retry the command"
	    elif pf == 'Linux':
	        print "   HINT : check if the 'pcscd' daemon is running, maybe it has not yet started or it crashed"
	    elif pf == 'Windows':
	        print "   HINT : check if the 'scardsvr' service is running, maybe it has not yet started or it crashed"
	    else:
	        print "   HINT : check the os process that manage card reader"

def transmit(data, connection=0):
	pass

def connectCard(index=0):
	pass

def connectReader(index=0):
	pass

def getConnectedCard():
	pass

def getReader():
	pass

registerSetGlobalPrefix( ("pcsc", ) )
registerCommand( ("load",) ,           pro=loadPCSC)




