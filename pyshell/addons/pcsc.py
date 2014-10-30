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
    #a connexion id shouldn't change if an other connexion is closed

    #think about critical section on card list
        #will also occured on connection_list
        
        #what about boolean env ? (???)
            #use its own rlock (not implemented yet)

    #monitoring data/reader/card
    
    #autoconnect

    #XXX what about scard data transmit ?
        #it is a sublayer to pyscard
        #not really usefull
        #but it could be interesting to have an access to it

    #thread to manage card list, otherwise the list will always be empty
        #add card in the list
        #remove card from the list
            #and remove connection from list 
                #NEED A LOCK HERE
                    #because a lot of command access to this list
                #could be interesting to implement lock in parameter class system
                    
    #thread to manage reader connection/disconnection
        #no need to hold a list, pcsc does it
        #to catch event (not really needed now)
        #start on loading of pcsc, not on addon loading
        
                    
from pyshell.loader.command    import registerCommand, registerSetGlobalPrefix, registerSetTempPrefix, registerStopHelpTraversalAt
from pyshell.arg.decorator     import shellMethod
from pyshell.arg.argchecker    import defaultInstanceArgChecker,listArgChecker, IntegerArgChecker, environmentParameterChecker, contextParameterChecker, tokenValueArgChecker
from pyshell.utils.postProcess import printColumn
from pyshell.loader.parameter  import registerSetEnvironment
from pyshell.utils.parameter   import EnvironmentParameter
from pyshell.utils.printing    import Printer, notice, printShell, formatBolt
from pyshell.utils.exception   import DefaultPyshellException, LIBRARY_ERROR
from apdu.misc.apdu            import toHexString

try:
    from smartcard.System                 import readers
    #from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
    #from smartcard.ReaderMonitoring       import ReaderMonitor, ReaderObserver
    from smartcard.CardMonitoring         import CardObserver,CardMonitor
    from smartcard.CardConnection         import CardConnection
    from smartcard.ATR                    import ATR
    from smartcard.pcsc.PCSCContext       import PCSCContext
    from smartcard.pcsc.PCSCExceptions    import EstablishContextException
    #from smartcard.sw.ErrorCheckingChain    import ErrorCheckingChain
    #from smartcard.sw.ISO7816_4ErrorChecker import ISO7816_4ErrorChecker
    #from smartcard.sw.ISO7816_8ErrorChecker import ISO7816_8ErrorChecker
    #from smartcard.sw.ISO7816_9ErrorChecker import ISO7816_9ErrorChecker
except ImportError as ie:    
    import sys
    
    message  = "Fail to import smartcard : "+str(ie) 
    message += "\n\nmaybe the library is not installed on this system, you can download it from"
    message += "\nhttp://pyscard.sourceforge.net"
    
    message += "\n\nOR maybe pyscard is installed with another version of python"
    message += "\ncurrent is "+str(sys.version_info[0])+"."+str(sys.version_info[1])+", maybe try with a python "
    
    if sys.version_info[0] == 3:
        message += "2"
    elif sys.version_info[0] == 2:
        if sys.version_info[1] == 6:
            message += "2.7"
        elif sys.version_info[1] == 7:
            message += "2.6"
        else:
            message += "2.6 or 2.7"
    else:
        message += "2.6 or 2.7"
    message += " runtime if available"
    
    raise DefaultPyshellException(message, LIBRARY_ERROR)

## MISC SECTION ##


class CardManager( CardObserver ):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """
    
    def __init__(self, cardListEnv, autoConnectEnv):
        self.cardmonitor    = CardMonitor()
        self.cardListEnv    = cardListEnv
        self.autoConnectEnv = autoConnectEnv #TODO
        #self.enable = True
        #self.cardList = []
        self.cardmonitor.addObserver( self )
        #self.autocon = False
    
    def update( self, observable, (addedcards, removedcards) ):
        #FIXME should raise an event and no more (WAIT FOR EVENT MANAGER)
            #the business should not occured here (because of lock, etc..)
        
        r = ""  #card connected or removed
        #ac = "" #autoconnect result
        if addedcards != None and len(addedcards) > 0:
            r += "Added card(s) " + str(addedcards) 
            
            #TODO should be in critical section
            cardList = self.cardListEnv.getValue()[:]
            
            for c in addedcards:
                cardList.append(c)
            
            self.cardListEnv.setValue(cardList)
            #XXX
            
            #ac = self.autoConnect()
        
        if removedcards != None and len(removedcards) > 0:
            
            if len(r) > 0:
                r += "\n"
            
            r += "Removed cards" + str(removedcards)
            
            #TODO should be in critical section
            cardList = self.cardListEnv.getValue()[:]
            
            for c in removedcards:
                cardList.remove(c)

            self.cardListEnv.setValue(cardList)
            #XXX

            #if hasattr(c,'connection'):
            #    disconnectReaderFromCardFun(Executer.envi)
            #    print("WARNING : the card has been removed, the connection is broken")
        
        if len(r) > 0:
            notice(r)
        
        #if self.enable and len(r) > 0:
        #    if len(ac) > 0:
        #        r += ac + "\n"
        #    
        #    print(r)
        #else:
        #    if len(ac) > 0:
        #        print(ac)
        
    #def activate(self):
        #if not self.enable:
        #    self.cardmonitor.addObserver( self )
        
    #    self.enable = True
        
    #def desactivate(self):
        #if self.enable:
        #    self.cardmonitor.deleteObserver(self)
        
    #    self.enable = False
        
    #def enableAutoCon(self):
    #    self.autocon = True
    #    Executer.printOnShell(self.autoConnect())
        
    #def disableAutoCon(self):
    #    self.autocon = False
        
    #def autoConnect(self):
    #    if "connection" not in Executer.envi and self.autocon:
    #        if len(self.cardList) == 1:
    #            if connectReaderFromCardFun(Executer.envi):
    #                return "connected to a card"
    #        elif len(self.cardList) > 1:
    #            return "WARNING : autoconnect is enable but there is more than one card available, no connection established"
    #    
    #   return None

def _checkList(l, index, item_type):
    if len(l) == 0:
        raise Exception("no "+item_type+" available")
    
    connectionToUse = None
    
    try:
        return l[index]
    except IndexError:
        if len(l) == 1:
            raise Exception("invalid "+item_type+" index, only the value 0 is actually allowed, got "+str(index))
        else:
            raise Exception("invalid "+item_type+" index, expected a value between 0 and "+str(len(l) -1)+", got "+str(index))
        

## FUNCTION SECTION ##

#TODO not used but useful...
@shellMethod(bytes=listArgChecker(IntegerArgChecker(0,255)))
def printATR(bytes):
    "convert a string of bytes into a human readable comprehension of the ATR"
    if bytes == None or not isinstance(bytes,list) or len(bytes) < 1:
        printShell("The value is not a valid ATR")
        return
    
    atr = ATR(bytes)
    
    with Printer.getInstance(): #use of this critical section because dump produce some print without control
        printShell(str(atr)+"\n")
        atr.dump()
        printShell('T15 supported: ', atr.isT15Supported())

@shellMethod(cards = environmentParameterChecker("pcsc_cardlist"),
             autoload    = environmentParameterChecker("pcsc_autoload"),
             loaded      = environmentParameterChecker("pcsc_contextready"),
             autoconnect = environmentParameterChecker("pcsc_autoconnect"))
def loadPCSC(cards, autoload, loaded,autoconnect):
    "try to load the pcsc context, this method must be called before any pcsc action if autoload is disabled"

    if loaded.getValue():
        return
        
    if not autoload.getValue():
        raise Exception("pcsc is not loaded and autoload is disabled")

    #not already called in an import ?
    try:
        notice("context loading... please wait")
        PCSCContext()
        notice("context loaded")
        loaded.setValue(True)
        
    except EstablishContextException as e:
        message = str(e)
        
        import platform
        pf = platform.system()
        if pf == 'Darwin':
            message += "\nHINT : connect a reader and use a tag/card with it, then retry the command"
        elif pf == 'Linux':
            message += "\nHINT : check if the 'pcscd' daemon is running, maybe it has not been started or it crashed"
        elif pf == 'Windows':
            message += "\nHINT : check if the 'scardsvr' service is running, maybe it has not been started or it crashed"
        else:
            message += "\nHINT : check the os process that manage card reader"
            
        raise DefaultPyshellException(message,LIBRARY_ERROR)
        
    #start thread to monitor card connection
    CardManager(cards, autoconnect)

@shellMethod(data=listArgChecker(IntegerArgChecker(0,255)),
             connection_index= IntegerArgChecker(0),
             connections=environmentParameterChecker("pcsc_connexionlist"))
def transmit(data, connection_index=0, connections = None):
    "transmit a list of bytes to a card connection"

    #print data

    #TODO manage every SW here
        #setErrorCheckingChain to the connection object
        #maybe could be interesting to set it at connection creation

    connectionToUse = _checkList(connections.getValue(), connection_index, "connection")
    
    data, sw1, sw2 = connectionToUse.transmit(data)
    
    print "sw1=%.2x sw2=%.2x"%(sw1, sw2)
    #print "data=",data
    
    return data
    
    #TODO if connection is broken, disconnect and remove from the list
        #how to know it ?
        #manage it in the thread ?

@shellMethod(index       = IntegerArgChecker(0),
             cards       = environmentParameterChecker("pcsc_cardlist"),
             connections = environmentParameterChecker("pcsc_connexionlist"),
             autoload    = environmentParameterChecker("pcsc_autoload"),
             loaded      = environmentParameterChecker("pcsc_contextready"),
             autoconnect = environmentParameterChecker("pcsc_autoconnect"))
def connectCard(index=0, cards = None,connections = None,loaded=False, autoload=False, autoconnect=False):
    "create a connection over a specific card"
    loadPCSC(cards, autoload, loaded, autoconnect)

    cardToUse = _checkList(cards.getValue(), index, "card")
    
    connection = cardToUse.createConnection()
    connection.connect()
    
    connection_list = connections.getValue()[:]
    connection_list.append(connection)
    connections.setValue(connection_list)
    
    #TODO return connection id

@shellMethod(index=IntegerArgChecker(0),
             cards       = environmentParameterChecker("pcsc_cardlist"),
             connections = environmentParameterChecker("pcsc_connexionlist"),
             autoload    = environmentParameterChecker("pcsc_autoload"),
             loaded      = environmentParameterChecker("pcsc_contextready"),
             autoconnect = environmentParameterChecker("pcsc_autoconnect"))
def connectReader(index=0,cards = None, connections = None,loaded=False, autoload=False, autoconnect=False):
    "create a connection over a specific reader"
    
    loadPCSC(cards, autoload, loaded, autoconnect)

    readerToUse = _checkList(readers(), index, "reader")
    
    connection = readerToUse.createConnection()
    
    #FIXME if an error occurs here, the exception raised does not give the id of the reader
    connection.connect()#create a connection to the card

    connection_list = connections.getValue()[:]
    connection_list.append(connection)
    connections.setValue(connection_list)
    
    #TODO return connection id

@shellMethod(index       = IntegerArgChecker(0),
             connections = environmentParameterChecker("pcsc_connexionlist"))
def disconnect(index=0, connections = None):
    "close a connection"
    
    connection_list = connections.getValue()
    
    if len(connection_list) == 0:
        return
        
    connectionToUse = _checkList(connection_list, index, "connection")

    try:
        connectionToUse.disconnect()
    finally:
        connection_list.remove(connectionToUse)
        connections.setValue(connection_list)

@shellMethod(connections = environmentParameterChecker("pcsc_connexionlist"))
def getConnected(connections):
    "list the existing connection(s)"    
    
    connection_list = connections.getValue()
    
    if len(connection_list) == 0:
        return ()
    
    to_ret = []
    to_ret.append( (formatBolt("ID"), formatBolt("Reader name"), formatBolt("Protocol"), formatBolt("ATR"), ) )
    
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
    "list available card(s) on the system connected or not"

    #FIXME if not loaded, even if a card if available, the list will be empty

    card_list = cards.getValue()

    if len(card_list) == 0:
        return ()
        
    to_ret = []
    to_ret.append( (formatBolt("ID"), formatBolt("Reader name"), formatBolt("Connected"), formatBolt("ATR"), ) )
    
    index = 0
    connections = connections.getValue()
    for card in card_list:
        for con in connections:
            if con.getATR() == card.atr:
                connected = "connected"
                break
        else:
            connected = "not connected"
    
        to_ret.append( (str(index), str(card.reader), connected, toHexString(card.atr), ) )
        index += 1
    
    return to_ret

@shellMethod(cards             = environmentParameterChecker("pcsc_cardlist"),
             connections       = environmentParameterChecker("pcsc_connexionlist"),
             autoload          = environmentParameterChecker("pcsc_autoload"),
             loaded            = environmentParameterChecker("pcsc_contextready"),
             autoconnect       = environmentParameterChecker("pcsc_autoconnect"))
def getAvailableReader(cards, connections, autoload=False, loaded=False, autoconnect=False):
    "list available reader(s)"

    loadPCSC(cards, autoload, loaded, autoconnect)
    
    r = readers()
    
    if len(r) == 0:
        return ()
        
    to_ret = []
    to_ret.append( (formatBolt("ID"),formatBolt("Reader name"), formatBolt("Card on reader"), formatBolt("Card connected"),) )
    
    cards = cards.getValue()
    connections = connections.getValue()
    
    index = 0
    for reader in r:
        connected = 0
        onreader = 0
    
        for card in cards:
            if str(card.reader) == str(reader):
                onreader += 1
                
        for con in connections:
            if str(con.getReader()) == str(reader):
                connected += 1
                
        to_ret.append( (str(index), str(reader), str(onreader), str(connected),) )
        index += 1
        
    return to_ret
    
@shellMethod(connexion_index = IntegerArgChecker(0),
             connections = environmentParameterChecker("pcsc_connexionlist"),
             protocol    = tokenValueArgChecker({"T0":CardConnection.T0_protocol, "T1":CardConnection.T1_protocol, "T15":CardConnection.T15_protocol, "RAW":CardConnection.RAW_protocol}))
def setProtocol(connexion_index, protocol, connections):
    "set communication protocol on a card connection"

    connectionToUse = _checkList(connections.getValue(), connection_index, "connection")
    connectionToUse.setProtocol(protocol)

@shellMethod(value    = defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             autoload = environmentParameterChecker("pcsc_autoload"))
def setAutoLoad(value,autoload):
    "set auto loadding context on any call to pcsc method"

    autoload.setValue(value)
    
@shellMethod(value    = defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             autoconnect = environmentParameterChecker("pcsc_autoconnect"))
def setAutoConnect(value,autoconnect):
    "set auto connection to the first card available and only to the first card"

    autoload.setValue(value)

@shellMethod(enable = defaultInstanceArgChecker.getbooleanValueArgCheckerInstance())
def monitorCard(enable):
    "enable/disable card monitoring"
    pass #TODO
    
@shellMethod(enable = defaultInstanceArgChecker.getbooleanValueArgCheckerInstance())
def monitorReader(enable):
    "enable/disable reader monitoring"
    pass #TODO
    
@shellMethod(enable = defaultInstanceArgChecker.getbooleanValueArgCheckerInstance())
def monitorData(enable):
    "enable/disable data monitoring"
    pass #TODO
        
## register ENVIRONMENT ##

registerSetEnvironment(envKey="pcsc_autoload",      env=EnvironmentParameter(True,  typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(), transient = False, readonly = False, removable = False), noErrorIfKeyExist = True, override = False)
registerSetEnvironment(envKey="pcsc_contextready",  env=EnvironmentParameter(False, typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(), transient = True,  readonly = False, removable = False), noErrorIfKeyExist = True, override = True)
registerSetEnvironment(envKey="pcsc_autoconnect",   env=EnvironmentParameter(False, typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(), transient = False, readonly = False, removable = False), noErrorIfKeyExist = True, override = False)

registerSetEnvironment(envKey="pcsc_cardlist",      env=EnvironmentParameter([], typ=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()), transient = True,  readonly = False, removable = False), noErrorIfKeyExist = True, override = True)
registerSetEnvironment(envKey="pcsc_connexionlist", env=EnvironmentParameter([], typ=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()), transient = True,  readonly = False, removable = False), noErrorIfKeyExist = True, override = True)

## register METHOD ##

registerSetGlobalPrefix( ("pcsc", ) )
registerStopHelpTraversalAt( () )

registerCommand( ("list",) ,             pro=getConnected,       post=printColumn)
registerCommand( ("disconnect",) ,       pro=disconnect)
registerCommand( ("transmit",) ,         pro=transmit)
registerCommand( ("load",) ,             pro=loadPCSC)

registerSetTempPrefix( ("reader", ) )
registerCommand( ("list",) ,    pro=getAvailableReader, post=printColumn)
registerCommand( ("connect",) , pro=connectReader)
registerStopHelpTraversalAt( ("reader",) )

registerSetTempPrefix( ("card", ) )
registerCommand( ("list",) ,      pro=getAvailableCard,   post=printColumn)
registerCommand( ("connect",) ,   pro=connectCard)
registerStopHelpTraversalAt( ("card",) )

registerSetTempPrefix( ("set", ) )
registerCommand( ("autoload",) ,   pro=setAutoLoad)
registerCommand( ("autoconnect",) , pro=setAutoConnect)
registerCommand( ("protocol",) ,    pro=setProtocol)
registerStopHelpTraversalAt( ("set",) )

registerSetTempPrefix( ("monitor", ) )
registerCommand( ("card",) ,   pro=monitorCard)
registerCommand( ("reader",) , pro=monitorReader)
registerCommand( ("data",) ,   pro=monitorData)
registerStopHelpTraversalAt( ("monitor",) )
