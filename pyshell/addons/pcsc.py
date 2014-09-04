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
        
    #enable/disable data watch (see old rfid file)
                    
from pyshell.loader.command            import registerStopHelpTraversalAt, registerCommand, registerSetGlobalPrefix
from pyshell.arg.decorator             import shellMethod
from pyshell.arg.argchecker            import defaultInstanceArgChecker,listArgChecker, IntegerArgChecker, environmentParameterChecker, contextParameterChecker, tokenValueArgChecker
from pyshell.simpleProcess.postProcess import printColumn
from pyshell.loader.parameter          import registerSetEnvironment
from pyshell.utils.parameter           import EnvironmentParameter
from pyshell.utils.coloration          import bolt, nocolor
from apdu.misc.apdu                    import toHexString

try:
    #TODO check if every items here are needed
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

## MISC SECTION ##

def _checkList(l, index, item_type):
    if len(l) == 0:
        raise Exception("no "+item_type+" available")
    
    connectionToUse = None
    
    try:
        return l[index]
    except IndexError:
        raise Exception("invalid "+item_type+" index, expected a value between 0 and "+str(len(l) -1)+", got "+str(index)) #TODO will produce a weird message if only one item in list
        

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

@shellMethod(autoload    = contextParameterChecker("pcsc_autoload"),
             loaded      = contextParameterChecker("pcsc_contextready"),
             autoconnect = contextParameterChecker("pcsc_autoconnect"))
def loadPCSC(autoload, loaded,autoconnect):
    if loaded:
        return
        
    if not autoload:
        raise Exception("pcsc is not loaded and autoload is disabled")

    #not already called in an import ?
    try:
        print "context loading... please wait"
        PCSCContext()
        print "context loaded"
        loaded.setValue(True)
        
    except EstablishContextException as e:
        #TODO should raise an exception 
        
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
            
        return
        
    #TODO start thread to monitor card connection


@shellMethod(data=listArgChecker(IntegerArgChecker(0,255)),
             #connection_index= defaultInstanceArgChecker.getIntegerArgCheckerInstance() #FIXME DashPAram
             connections=environmentParameterChecker("pcsc_connexionlist"))
def transmit(data, connection_index=0, connections = None):

    #TODO manage every SW here
        #setErrorCheckingChain to the connection object
        #maybe could be interesting to set it at connection creation

    connectionToUse = _checkList(connections.getValue(), connection_index, "connection")
    return connectionToUse.transmit(data)

@shellMethod(index       = IntegerArgChecker(0),
             cards       = environmentParameterChecker("pcsc_cardlist"),
             connections = environmentParameterChecker("pcsc_connexionlist"),
             autoload    = contextParameterChecker("pcsc_autoload"),
             loaded      = contextParameterChecker("pcsc_contextready"),
             autoconnect = contextParameterChecker("pcsc_autoconnect"))
def connectCard(index=0, cards = None,connections = None,loaded=False, autoload=False, autoconnect=False):
    loadPCSC(loaded.getValue(), autoload.getValue(), autoconnect.getValue())

    connectionToUse = _checkList(cards.getValue(), index, "card")
    
    connection = cardToUse.createConnection()
    connection.connect()
    
    connection_list = connections.getValue()[:]
    connection_list.append(connection)
    connections.setValue(connection_list)

@shellMethod(index=IntegerArgChecker(0),
             connections = environmentParameterChecker("pcsc_connexionlist"),
             autoload    = contextParameterChecker("pcsc_autoload"),
             loaded      = contextParameterChecker("pcsc_contextready"),
             autoconnect = contextParameterChecker("pcsc_autoconnect"))
def connectReader(index=0, connections = None,loaded=False, autoload=False, autoconnect=False):
    loadPCSC(loaded.getValue(), autoload.getValue(), autoconnect.getValue())

    readerToUse = _checkList(readers(), index, "reader")
    
    connection = readerToUse.createConnection()
    connection.connect()#create a connection to the card

    connection_list = connections.getValue()[:]
    connection_list.append(connection)
    connections.setValue(connection_list)

@shellMethod(index       = IntegerArgChecker(0),
             connections = environmentParameterChecker("pcsc_connexionlist"))
def disconnect(index=0, connections = None):
    connection_list = connections.getValue()
    
    if len(connection_list) == 0:
        return
        
    connectionToUse = _checkList(connection_list, connection_index, "connection")

    try:
        connectionToUse.disconnect()
    finally:
        connection_list.remove(connectionToUse)
        connections.setValue(connection_list)

@shellMethod(connections = environmentParameterChecker("pcsc_connexionlist"),
             execution_context = contextParameterChecker("execution"))
def getConnected(connections, execution_context):
    connection_list = connections.getValue()
    
    if len(connection_list) == 0:
        return ()
    
    if execution_context.getSelectedValue() == "shell":
        title = bolt 
    else:
        title = nocolor
    
    to_ret = []
    to_ret.append( (title("ID"), title("Reader"), title("Protocol"), title("ATR"), ) )
    
    index = 0
    for con in connection_list:        
        #protocole type
        if con.getProtocol() == CardConnection.RAW_protocol:
            prot = "RAW"
        elif con.getProtocol() == CardConnection.T15_protocol:
            prot = "T15"
        elif con.getProtocol() == CardConnection.T0_protocol:
            prot = "T0"
        elif con.getProtocol() == CardConnection.T1_protocol:
            prot = "T1"
        else:
            prot = "unknown"
    
        to_ret.append( (str(index), str(con.getReader()),prot, toHexString(con.getATR()), ) )
    
        index += 1 
    
    return to_ret

@shellMethod(cards = environmentParameterChecker("pcsc_cardlist"),
             connections = environmentParameterChecker("pcsc_connexionlist"))
def getAvailableCard(cards,connections):

    card_list = cards.getValue()

    if len(card_list) == 0:
        return ()
        
    to_ret = []
    to_ret.append( ("ID", "Reader", "Connected", "ATR", ) )
    
    index = 0
    for card in card_list:
        for con in connections:
            if con.getATR() == card.atr:
                connected = "connected"
                break
        else:
            connected = "not connected"
    
        to_ret.append( (str(index), str(card.reader), connected, toHexString(con.atr), ) )
        index += 1
    
    return to_ret

@shellMethod(cards             = environmentParameterChecker("pcsc_cardlist"),
             connections       = environmentParameterChecker("pcsc_connexionlist"),
             execution_context = contextParameterChecker("execution"),
             autoload          = contextParameterChecker("pcsc_autoload"),
             loaded            = contextParameterChecker("pcsc_contextready"),
             autoconnect       = contextParameterChecker("pcsc_autoconnect"))
def getAvailableReader(cards, connections,execution_context, autoload=False, loaded=False, autoconnect=False):
    loadPCSC(loaded.getValue(), autoload.getValue(), autoconnect.getValue())
    
    r = readers()
    
    if len(r) == 0:
        return ()
    
    if execution_context.getSelectedValue() == "shell":
        title = bolt 
    else:
        title = nocolor
    
    to_ret = []
    to_ret.append( (title("Reader name"), title(" Card on reader"), title(" Card connected"),) )
    
    cards = cards.getValue()
    connections = connections.getValue()
    
    for reader in r:
        connected = 0
        onreader = 0
    
        for card in cards:
            if card.reader == reader:
                onreader += 1
                
        for con in connections:
            if con.getReader() == reader:
                connected += 1
                
        to_ret.append( (str(reader), "  "+str(onreader), "  "+str(connected),) )

    return to_ret
    
@shellMethod(connexion_index = IntegerArgChecker(0),
             connections = environmentParameterChecker("pcsc_connexionlist"),
             protocol    = tokenValueArgChecker({"T0":CardConnection.T0_protocol, "T1":CardConnection.T1_protocol, "T15":CardConnection.T15_protocol, "RAW":CardConnection.RAW_protocol}))
def setProtocol(connexion_index, protocol, connections):
    connectionToUse = _checkList(connections.getValue(), connection_index, "connection")
    connectionToUse.setProtocol(protocol)

@shellMethod(value    = defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             autoload = contextParameterChecker("pcsc_autoload"))
def setAutoLoad(value,autoload):
    autoload.setValue(value)
    
@shellMethod(value    = defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             autoconnect = contextParameterChecker("pcsc_autoconnect"))
def setAutoConnect(value,autoconnect):
    autoload.setValue(value)

## register ENVIRONMENT ##

registerSetEnvironment(envKey="pcsc_autoload",      env=EnvironmentParameter(True,  typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(), transient = False, readonly = False, removable = False), noErrorIfKeyExist = True, override = False)
registerSetEnvironment(envKey="pcsc_contextready",  env=EnvironmentParameter(False, typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(), transient = True,  readonly = False, removable = False), noErrorIfKeyExist = True, override = True)
registerSetEnvironment(envKey="pcsc_autoconnect",   env=EnvironmentParameter(False, typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(), transient = False, readonly = False, removable = False), noErrorIfKeyExist = True, override = False)

registerSetEnvironment(envKey="pcsc_cardlist",      env=EnvironmentParameter([], typ=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()), transient = True,  readonly = False, removable = False), noErrorIfKeyExist = True, override = True)
registerSetEnvironment(envKey="pcsc_connexionlist", env=EnvironmentParameter([], typ=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()), transient = True,  readonly = False, removable = False), noErrorIfKeyExist = True, override = True)

## register METHOD ##

registerSetGlobalPrefix( ("pcsc", ) )
registerStopHelpTraversalAt( () )
registerCommand( ("load",) ,             pro=loadPCSC)

registerCommand( ("reader","list",) ,    pro=getAvailableReader, post=printColumn)
registerCommand( ("reader","connect",) , pro=connectReader)

registerCommand( ("card","list",) ,      pro=getAvailableCard,   post=printColumn)
registerCommand( ("card","connect",) ,   pro=connectCard)

registerCommand( ("list",) ,             pro=getConnected,       post=printColumn)
registerCommand( ("disconnect",) ,       pro=disconnect)
registerCommand( ("transmit",) ,         pro=transmit)

registerCommand( ("set","autoload",) ,   pro=setAutoLoad)
registerCommand( ("set","autoconnect") , pro=setAutoConnect)
registerCommand( ("set","protocol") ,    pro=setProtocol)




