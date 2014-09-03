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

#TODO
    #use loaded and autoload environment

    #check in rfidDefault if something must be retrieve

    #XXX what about scard data transmit ?

    #thread to manage card list, otherwise the list will always be empty
        #add card in the list
        #remove card from the list
            #and remove connection from list 
                #NEED A LOCK HERE
                    #because a lot of command access to this list
                #could be interesting to implement lock in parameter class system
        #start on loading of pcsc, not on addon loading
                    
    #thread to manage reader connection/disconnection
        #no need to hold a list, pcsc does it
        #to catch event (not really needed now)
        #start on loading of pcsc, not on addon loading
        
    
                    
from pyshell.loader.command            import registerStopHelpTraversalAt, registerCommand, registerSetGlobalPrefix
from pyshell.arg.decorator             import shellMethod
from pyshell.arg.argchecker            import defaultInstanceArgChecker,listArgChecker, IntegerArgChecker, environmentParameterChecker
from pyshell.simpleProcess.postProcess import stringListResultHandler, printColumn
from pyshell.loader.parameter          import registerSetEnvironment
from pyshell.utils.parameter           import EnvironmentParameter

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
        #because the raised exception will be print and the hint message too
        
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

@shellMethod(loaded = environmentParameterChecker("pcsc_contextready"))
def loadPCSC(loaded):

    if loaded.getValue():
        raise Exception("pcsc context is already loaded")

    #not already called in an import ?
    try:
        print "context loading... please wait"
        PCSCContext()
        print "context loaded"
        loaded.setValue(True)
        
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


@shellMethod(data=listArgChecker(IntegerArgChecker(0,255)),
             #connection_index= defaultInstanceArgChecker.getIntegerArgCheckerInstance() #FIXME DashPAram
             connections=environmentParameterChecker("pcsc_connexionlist"))
def transmit(data, connection_index=0, connections = None):

    #TODO manage every SW here
        #setErrorCheckingChain to the connection object
        #maybe could be interesting to set it at connection creation

    connection_list = connections.getValue()
    
    if len(connection_list) == 0:
        raise Exception("no connection available")
    
    connectionToUse = None
    try:
        connectionToUse = connection_list[connection_index]
    except IndexError:
        raise Exception("invalid connection index, expected a value between 0 and "+str(len(connection_list) -1)+", got "+str(connection_index)) #TODO will produce a weird message if only one item in list
        
    return connectionToUse.transmit(data)

@shellMethod(index       = IntegerArgChecker(),
             cards       = environmentParameterChecker("pcsc_cardlist"),
             connections = environmentParameterChecker("pcsc_connexionlist"))
def connectCard(index=0, cards = None,connections = None):
    #TODO check autoload and contextLoaded

    card_list = cards.getValue()
    
    if len(card_list) == 0:
        raise Exception("no card available")
    
    cardToUse = None
    try:
        cardToUse = card_list[index]
    except IndexError:
        raise Exception("invalid card index, expected a value between 0 and "+str(len(card_list) -1)+", got "+str(index)) #TODO will produce a weird message if only one item in list
    
    connection = cardToUse.createConnection()
    connection.connect()
    
    connection_list = connections.getValue()[:]
    connection_list.append(connection)
    connections.setValue(connection_list)

@shellMethod(index=IntegerArgChecker(0))
def connectReader(index=0, connections = None):
    #TODO check autoload and contextLoaded

    r = readers()

    if len(r) == 0:
        raise Exception("no reader available", True)

    readerToUse = none
    try:
        readerToUse = r[index]
    except IndexError:
        raise Exception("invalid reader index, expected a value between 0 and "+str(len(r) -1)+", got "+str(index)) #TODO will produce a weird message if only one item in list
        
    connection = readerToUse.createConnection()
    connection.connect()#create a connection to the card

    connection_list = connections.getValue()[:]
    connection_list.append(connection)
    connections.setValue(connection_list)


@shellMethod(index       = IntegerArgChecker(),
             connections = environmentParameterChecker("pcsc_connexionlist"))
def disconnect(index=0, connections = None):
    connection_list = connections.getValue()
    
    if len(connection_list) == 0:
        return
    
    connectionToUse = None
    try:
        connectionToUse = connection_list[index]
    except IndexError:
        raise Exception("invalid connection index, expected a value between 0 and "+str(len(connection_list) -1)+", got "+str(index)) #TODO will produce a weird message if only one item in list

    try:
        connectionToUse.disconnect()
    finally:
        connection_list.remove(connectionToUse)
        connections.setValue(connection_list)

@shellMethod(connections = environmentParameterChecker("pcsc_connexionlist"))
def getConnected(connections):
    connection_list = connections.getValue()
    
    if len(connection_list) == 0:
        return ()
        
    to_ret = []
    
    #TODO
        #create column, column title, get information about connection (see pyscard documentation), ...
    
    return to_ret

@shellMethod(cards = environmentParameterChecker("pcsc_cardlist"))
def getAvailableCard(cards):

    #TODO same kind of stuff than in getConnected
        #create column, column title, get information about card (see pyscard documentation), ...

    pass #TODO

def getAvailableReader():

    #TODO could be probably possible to get more information about reader
        #see documentation
        #create column, column title, ...
        #the number of card on the reader, the number of connection opened, ...
        #...

    return readers()

## register ENVIRONMENT ##

registerSetEnvironment(envKey="pcsc_autoload",     env=EnvironmentParameter(True,  typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(), transient = False, readonly = False, removable = False), noErrorIfKeyExist = True, override = False)
registerSetEnvironment(envKey="pcsc_contextready", env=EnvironmentParameter(False, typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(), transient = True,  readonly = False, removable = False), noErrorIfKeyExist = True, override = True)

registerSetEnvironment(envKey="pcsc_cardlist",      env=EnvironmentParameter([], typ=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()), transient = True,  readonly = False, removable = False), noErrorIfKeyExist = True, override = True)
registerSetEnvironment(envKey="pcsc_connexionlist", env=EnvironmentParameter([], typ=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()), transient = True,  readonly = False, removable = False), noErrorIfKeyExist = True, override = True)

#TODO autoConnect
    #to the first card only
    #need autoload enabled or context loaded

## register METHOD ##

registerSetGlobalPrefix( ("pcsc", ) )
registerStopHelpTraversalAt( () )
registerCommand( ("load",) ,             pro=loadPCSC)

registerCommand( ("reader","list",) ,    pro=getAvailableReader, post=stringListResultHandler)
registerCommand( ("reader","connect",) , pro=connectReader)

registerCommand( ("card","list",) ,      pro=getAvailableCard,   post=printColumn)
registerCommand( ("card","connect",) ,   pro=connectCard)

registerCommand( ("list",) ,             pro=getConnected,       post=printColumn)
registerCommand( ("disconnect",) ,       pro=disconnect)
registerCommand( ("transmit",) ,         pro=transmit)




