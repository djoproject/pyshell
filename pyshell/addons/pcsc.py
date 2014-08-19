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

from pyshell.loader.command            import registerStopHelpTraversalAt, registerCommand, registerSetGlobalPrefix
from pyshell.arg.decorator             import shellMethod
from pyshell.arg.argchecker            import defaultInstanceArgChecker,listArgChecker, IntegerArgChecker
from pyshell.simpleProcess.postProcess import stringListResultHandler

try:
    from smartcard.System                 import readers
    from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
    from smartcard.ReaderMonitoring       import ReaderMonitor, ReaderObserver
    from smartcard.CardMonitoring         import CardMonitor, CardObserver
    from smartcard.CardConnection         import CardConnection
    from smartcard.ATR                    import ATR
    from smartcard.pcsc.PCSCContext       import PCSCContext
    from smartcard.pcsc.PCSCExceptions    import EstablishContextException

    from smartcard.sw.ErrorCheckingChain    import ErrorCheckingChain
    from smartcard.sw.ISO7816_4ErrorChecker import ISO7816_4ErrorChecker
    from smartcard.sw.ISO7816_8ErrorChecker import ISO7816_8ErrorChecker
    from smartcard.sw.ISO7816_9ErrorChecker import ISO7816_9ErrorChecker
except ImportError as ie:
    #TODO improve
        #the printed message will not be really pretty
        #becaus the raised exception will be print and the hint message too
        
    #print "failed to import smartcard : "+str(ie)
    print "maybe the library is not installed for this version of python"
    print "http://pyscard.sourceforge.net"
    
    import sys
    if(sys.platform == 'darwin'):
        print "HINT : on macos system, try to execute this script with python2.6"
        #TODO not a problem of macos, we try to execute the script with python2.7 and pyscard is installed with python2.6
            #yeah but why this occured each times with macos ???
    
    raise Exception("Fail to import smartcard : "+str(ie))

## FUNCTION SECTION ##

@shellMethod(bytes=listArgChecker(IntegerArgChecker(0,255)))
def printATR(bytes):
    if bytes == None or not isinstance(bytes,list) or len(bytes) < 1:
        Executer.printOnShell("The value is not a valid ATR")
        return
    
    atr = ATR(bytes)
    
    print atr
    print
    atr.dump()
    print 'T15 supported: ', atr.isT15Supported()

def loadPCSC():
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


@shellMethod(data=listArgChecker(IntegerArgChecker(0,255)))#,
             #connection= defaultInstanceArgChecker.getIntegerArgCheckerInstance()) #FIXME DashPAram
def transmit(data, connection=0):

    #TODO manage every SW here

    pass

@shellMethod(index=IntegerArgChecker())
def connectCard(index=0):
    pass #TODO

@shellMethod(index=IntegerArgChecker(0))
def connectReader(index=0):
    r = readers()

    if len(r) == 0:
        raise engineInterruptionException("no reader available", True)

    if index >= len(r):
        raise engineInterruptionException("too big index, maximum value allowed is <"+str(len(r)-1)+">, get <"+str(index)+">", True)

    reader = r[index]
        
    try:
        connection = reader.createConnection()
        connection.connect()#create a connection to the card

        #TODO store the connexion

    except Exception as e:
        raise engineInterruptionException("fail to create a connexion to the reader '"+str(reader)+"'", True)

@shellMethod(index=IntegerArgChecker())
def disconnect(index=0):
    pass #TODO 

def getConnected():
    pass #TODO

def getAvailableCard():
    pass #TODO

def getAvailableReader():
    return readers()

#TODO check in rfidDefault if something must be retrieve

#XXX what about scard data transmit ?

## register ENVIRONMENT ##

#TODO  
    #create variables
        #one to store connection
            #need transient
        #one for enable autoload
#registerSetEnvironmentValue(envKey="autoload", value=True, typ = defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(), noErrorIfKeyExist = True, override = False, subLoaderName = "pcsc")
#registerSetEnvironmentValue(envKey="contextready", value=False, typ = defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(), noErrorIfKeyExist = True, override = True, subLoaderName = "pcsc")

## register METHOD ##

registerSetGlobalPrefix( ("pcsc", ) )
registerStopHelpTraversalAt( () )
registerCommand( ("load",) ,           pro=loadPCSC)
registerCommand( ("reader",) ,         pro=getAvailableReader, post=stringListResultHandler)






