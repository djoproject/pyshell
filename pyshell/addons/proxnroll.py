#!/usr/bin/env python -t
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
    #quid du status word
        #on le traite ici ou pas (sinon dans l'addon pcsc) ??
        
        #si on le recupere ici, il faut le retirer avant de convertir en string ou autre
        
        #si on ne le recupere pas ici, risque de perdre certaines info
            #le garder et le retirer à chaque fois alors ?
                #semble être le plus sage
                
    #after a read, return the data extracted
        #maybe we want to use them after the prox post process


from apdu.readers.proxnroll      import ProxnrollAPDUBuilder
from pyshell.loader.command      import registerStopHelpTraversalAt, registerCommand, registerSetGlobalPrefix, registerSetTempPrefix
from pyshell.arg.decorator       import shellMethod
from pyshell.arg.argchecker      import defaultInstanceArgChecker,listArgChecker, IntegerArgChecker, tokenValueArgChecker, booleanValueArgChecker, keyStoreTranslatorArgChecker
from pyshell.command.exception   import engineInterruptionException
from pyshell.utils.postProcess   import printStringCharResult, printBytesAsString

from pyshell.addons.pcsc         import printATR #FIXME create a dependancy... 
                                                           #TODO remove it and only return a list of byte
                                                           #use piping to call the method from pcsc
                                                           
from pyshell.loader.dependancies import registerDependOnAddon
from pyshell.utils.printing      import printShell

## FUNCTION SECTION ##

_colourTokenChecker = tokenValueArgChecker(ProxnrollAPDUBuilder.ColorSettings)
@shellMethod(red = _colourTokenChecker, green=_colourTokenChecker, yellow_blue=_colourTokenChecker)
def setLight(red, green, yellow_blue = None):
    return ProxnrollAPDUBuilder.setLedColorFun(red, green, yellow_blue)

@shellMethod(duration=IntegerArgChecker(0,60000))
def setBuzzer(duration=2000):
    return ProxnrollAPDUBuilder.setBuzzerDuration(duration)

@shellMethod(anything=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def stopAsMainProcess(anything):
    #TODO in place of printing an error, print a description of the apdu (class, ins, length, ...)

    raise engineInterruptionException("A proxnroll command can not be directly executed, this command need to be piped into a transmit command",False)

@shellMethod(address=IntegerArgChecker(0,255),
             expected=IntegerArgChecker(0,255))
def read(address = 0,expected=0):
    return ProxnrollAPDUBuilder.readBinary(address,expected)

@shellMethod(datas   = listArgChecker(IntegerArgChecker(0,255),1),
             address = IntegerArgChecker(0,65535))
def update(datas, address=0):
    return ProxnrollAPDUBuilder.updateBinary(datas, address)
    
@shellMethod(datas=listArgChecker(IntegerArgChecker(0,255)),
             expected=IntegerArgChecker(0,255),
             delay=IntegerArgChecker(0,255))
def test(datas, expected=0, delay=0):
    return ProxnrollAPDUBuilder.test(expected, delay, datas)

@shellMethod(datas        = listArgChecker(IntegerArgChecker(0,255)),
             protocolType = tokenValueArgChecker(ProxnrollAPDUBuilder.protocolType),
             timeoutType  = tokenValueArgChecker(ProxnrollAPDUBuilder.timeout))
def encapsulateStandard(datas, protocolType = "ISO14443_TCL", timeoutType="Default"):
    return ProxnrollAPDUBuilder.encapsulate(datas, protocolType, timeoutType)
 
@shellMethod(datas        = listArgChecker(IntegerArgChecker(0,255)),
             protocolType = tokenValueArgChecker(ProxnrollAPDUBuilder.redirection),
             timeoutType  = tokenValueArgChecker(ProxnrollAPDUBuilder.timeout))
def encapsulateRedirection(datas, protocolType = "MainSlot", timeoutType="Default"):
    return ProxnrollAPDUBuilder.encapsulate(datas, protocolType, timeoutType)

@shellMethod(datas       =listArgChecker(IntegerArgChecker(0,255)),
             protocolType=tokenValueArgChecker(ProxnrollAPDUBuilder.lastByte),
             timeoutType =tokenValueArgChecker(ProxnrollAPDUBuilder.timeout))
def encapsulatePartial(datas, protocolType="complete", timeoutType="Default"):
    return ProxnrollAPDUBuilder.encapsulate(datas, protocolType, timeoutType)

@shellMethod(speed=booleanValueArgChecker("9600", "115200"))
def setSpeed(speed="9600"):
    if speed:
        return ProxnrollAPDUBuilder.configureCalypsoSamSetSpeed9600()
    else:
        return ProxnrollAPDUBuilder.configureCalypsoSamSetSpeed115200()

@shellMethod(acti=booleanValueArgChecker("a", "b"))
def setActivation(acti="a"):
    if acti:
        return ProxnrollAPDUBuilder.slotControlTCLActivationTypeA()
    else:
        return ProxnrollAPDUBuilder.slotControlTCLActivationTypeB()
        
@shellMethod(disable=booleanValueArgChecker("next", "every"))
def setDisable(disable="next"):
    if disable:
        return ProxnrollAPDUBuilder.slotControlDisableNextTCL()
    else:
        return ProxnrollAPDUBuilder.slotControlDisableEveryTCL


@shellMethod(KeyIndex=IntegerArgChecker(0,15),
             Key=keyStoreTranslatorArgChecker(6),
             isTypeA=booleanValueArgChecker("a","b"),
             InVolatile=booleanValueArgChecker("volatile", "notvolatile"))
def mifareLoadKey(KeyIndex, Key, isTypeA="a", InVolatile="volatile"):
    return ProxnrollAPDUBuilder.loadKey(KeyIndex, Key, isTypeA, InVolatile)

@shellMethod(blockNumber=IntegerArgChecker(0,0xff),
             KeyIndex=IntegerArgChecker(0,15),
             isTypeA=booleanValueArgChecker("a","b"),
             InVolatile=booleanValueArgChecker("volatile", "notvolatile"))
def mifareAuthenticate(blockNumber, KeyIndex, isTypeA="a", InVolatile="volatile"):
    return ProxnrollAPDUBuilder.generalAuthenticate(blockNumber, KeyIndex, isTypeA, InVolatile)

@shellMethod(blockNumber=IntegerArgChecker(0,0xff),
             Key=keyStoreTranslatorArgChecker(6))
def mifareRead(blockNumber=0, Key=None):
    return ProxnrollAPDUBuilder.mifareClassicRead(blockNumber, Key)

@shellMethod(datas=listArgChecker(IntegerArgChecker(0,255)),
             blockNumber=IntegerArgChecker(0,0xff),
             Key=keyStoreTranslatorArgChecker(6))
def mifareUpdate(datas, blockNumber=0, Key=None):
    return ProxnrollAPDUBuilder.mifareClassifWrite(blockNumber, Key,datas)

@shellMethod(datas=listArgChecker(IntegerArgChecker(0,255),3))
def parseDataCardType(datas):
    #TODO a print is used inside of this method, replace with printing system
    ss, nn = ProxnrollAPDUBuilder.parseDataCardType(datas)
    
    printShell("Procole : "+ss + ", Type : " + nn)

## REGISTER ##

# MAIN #
registerDependOnAddon("pyshell.addons.pcsc")
registerSetGlobalPrefix( ("proxnroll", ) )
registerStopHelpTraversalAt()
registerCommand( ( "setlight",),  pre=setLight,                               pro=stopAsMainProcess) 
registerCommand( ( "setbuzzer",), pre=setBuzzer,                              pro=stopAsMainProcess)
registerCommand( ( "vendor",),    pre=ProxnrollAPDUBuilder.getDataVendorName, pro=stopAsMainProcess, post=printStringCharResult)
registerCommand( ( "test",),      pre=test,                                   pro=stopAsMainProcess, post=printBytesAsString)
registerCommand( ( "read",),      pre=read,                                   pro=stopAsMainProcess, post=printBytesAsString)
registerCommand( ( "update",),    pre=update,                                 pro=stopAsMainProcess)
registerCommand( ( "hardwareIdentifier",), pre=ProxnrollAPDUBuilder.getDataHarwareIdentifier, pro=stopAsMainProcess, post=printBytesAsString)

# CALYPSO #
registerSetTempPrefix( ("calypso",  ) )
registerCommand( ( "setspeed",),            pre=setSpeed,                                                            pro=stopAsMainProcess)
registerCommand( ( "enabledigestupdate",),  pre=ProxnrollAPDUBuilder.configureCalypsoSamEnableInternalDigestUpdate,  pro=stopAsMainProcess)
registerCommand( ( "disabledigestupdate",), pre=ProxnrollAPDUBuilder.configureCalypsoSamDisableInternalDigestUpdate, pro=stopAsMainProcess)
registerStopHelpTraversalAt()

# PRODUCT #
registerSetTempPrefix( ("product",  ) )
registerCommand( ( "name",),          pre=ProxnrollAPDUBuilder.getDataProductName,          pro=stopAsMainProcess, post=printStringCharResult)
registerCommand( ( "serialString",),  pre=ProxnrollAPDUBuilder.getDataProductSerialNumber,  pro=stopAsMainProcess, post=printStringCharResult)
registerCommand( ( "usbidentifier",), pre=ProxnrollAPDUBuilder.getDataProductUSBIdentifier, pro=stopAsMainProcess, post=printStringCharResult)
registerCommand( ( "version",),       pre=ProxnrollAPDUBuilder.getDataProductVersion,       pro=stopAsMainProcess, post=printStringCharResult)
registerCommand( ( "serial",),        pre=ProxnrollAPDUBuilder.getDataProductSerialNumber,  pro=stopAsMainProcess, post=printStringCharResult)
registerStopHelpTraversalAt()

# CARD #
registerSetTempPrefix( ("card",  ) )
registerCommand( ( "serial",),             pre=ProxnrollAPDUBuilder.getDataCardSerialNumber,       pro=stopAsMainProcess, post=printBytesAsString)
registerCommand( ( "ats",),                pre=ProxnrollAPDUBuilder.getDataCardATS,                pro=stopAsMainProcess, post=printBytesAsString)
registerCommand( ( "completeIdentifier",), pre=ProxnrollAPDUBuilder.getDataCardCompleteIdentifier, pro=stopAsMainProcess, post=printBytesAsString)
registerCommand( ( "type",),               pre=ProxnrollAPDUBuilder.getDataCardType,               pro=stopAsMainProcess, post=parseDataCardType)
registerCommand( ( "shortSerial",),        pre=ProxnrollAPDUBuilder.getDataCardShortSerialNumber,  pro=stopAsMainProcess, post=printBytesAsString)
registerCommand( ( "atr",),                pre=ProxnrollAPDUBuilder.getDataCardATR,                pro=stopAsMainProcess, post=printATR)
registerStopHelpTraversalAt()

# TRACKING #
registerSetTempPrefix( ("control","tracking",  ) )
registerCommand( ( "resume",),  pre=ProxnrollAPDUBuilder.slotControlResumeCardTracking,  pro=stopAsMainProcess)
registerCommand( ( "suspend",), pre=ProxnrollAPDUBuilder.slotControlSuspendCardTracking, pro=stopAsMainProcess)
registerStopHelpTraversalAt()

# RFFIELD #
registerSetTempPrefix( ("control","rffield",  ) )
registerCommand( ( "stop",),  pre=ProxnrollAPDUBuilder.slotControlStopRFField,  pro=stopAsMainProcess)
registerCommand( ( "start",), pre=ProxnrollAPDUBuilder.slotControlStartRFField, pro=stopAsMainProcess)
registerCommand( ( "reset",), pre=ProxnrollAPDUBuilder.slotControlResetRFField, pro=stopAsMainProcess)
registerStopHelpTraversalAt()

# T=CL #
registerSetTempPrefix( ("control","t=cl",  ) )
registerCommand( ( "deactivation",), pre=ProxnrollAPDUBuilder.slotControlTCLDeactivation,                           pro=stopAsMainProcess)
registerCommand( ( "activation",),   pre=setActivation,                                                             pro=stopAsMainProcess)
registerCommand( ( "disable",),      pre=setDisable,                                                                pro=stopAsMainProcess)           
registerCommand( ( "enable",),       pre=ProxnrollAPDUBuilder.slotControlEnableTCLAgain,                            pro=stopAsMainProcess)
registerCommand( ( "reset",),        pre=ProxnrollAPDUBuilder.slotControlResetAfterNextDisconnectAndDisableNextTCL, pro=stopAsMainProcess)
registerStopHelpTraversalAt()

# STROP CONTROL #
registerSetTempPrefix( ("control", ) )
registerStopHelpTraversalAt()
registerCommand( ( "stop",), pre=ProxnrollAPDUBuilder.slotControlStop)

# ENCAPSULATE # 
#TODO try to merge these three and add the last param "defaultSW"
registerSetTempPrefix( ("encapsulate", ) )
registerCommand( ( "standard",),    pre=encapsulateStandard,    pro=stopAsMainProcess, post=printBytesAsString)
registerCommand( ( "redirection",), pre=encapsulateRedirection, pro=stopAsMainProcess, post=printBytesAsString)
registerCommand( ( "partial",),     pre=encapsulatePartial,     pro=stopAsMainProcess, post=printBytesAsString)
registerStopHelpTraversalAt()

# MIFARE #
registerSetTempPrefix( ("mifare", ) )
registerCommand( ( "loadkey",),      pre=mifareLoadKey,      pro=stopAsMainProcess)
registerCommand( ( "authenticate",), pre=mifareAuthenticate, pro=stopAsMainProcess)
registerCommand( ( "read",),         pre=mifareRead,         pro=stopAsMainProcess, post=printBytesAsString)
registerCommand( ( "update",),       pre=mifareUpdate,       pro=stopAsMainProcess)
registerStopHelpTraversalAt()


