#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# TODO
#   quid du status word
#   on le traite ici ou pas (sinon dans l'addon pcsc) ??
#   si on le recupere ici, il faut le retirer avant de convertir en string
#   ou autre

#   si on ne le recupere pas ici, risque de perdre certaines info
#       le garder et le retirer à chaque fois alors ?
#           semble être le plus sage

#   after a read, return the data extracted
#       maybe we want to use them after the prox post process


from apdu.readers.proxnroll import ProxnrollAPDUBuilder as ApduBuilder

from pyshell.addons.pcsc import printATR  # FIXME create a dependancy...
from pyshell.arg.argchecker import IntegerArgChecker
from pyshell.arg.argchecker import booleanValueArgChecker
from pyshell.arg.argchecker import defaultInstanceArgChecker
from pyshell.arg.argchecker import keyStoreTranslatorArgChecker
from pyshell.arg.argchecker import listArgChecker
from pyshell.arg.argchecker import tokenValueArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.command.exception import EngineInterruptionException
from pyshell.loader.command import registerCommand
from pyshell.loader.command import registerSetGlobalPrefix
from pyshell.loader.command import registerSetTempPrefix
from pyshell.loader.command import registerStopHelpTraversalAt
from pyshell.loader.dependancies import registerDependOnAddon
from pyshell.utils.postprocess import printBytesAsString
from pyshell.utils.postprocess import printStringCharResult
from pyshell.utils.printing import printShell


# # FUNCTION SECTION # #

_colourTokenChecker = tokenValueArgChecker(ApduBuilder.ColorSettings)


@shellMethod(red=_colourTokenChecker, green=_colourTokenChecker,
             yellow_blue=_colourTokenChecker)
def setLight(red, green, yellow_blue=None):
    return ApduBuilder.setLedColorFun(red, green, yellow_blue)


@shellMethod(duration=IntegerArgChecker(0, 60000))
def setBuzzer(duration=2000):
    return ApduBuilder.setBuzzerDuration(duration)


@shellMethod(anything=listArgChecker(
    defaultInstanceArgChecker.getArgCheckerInstance()))
def stopAsMainProcess(anything):
    # TODO in place of printing an error, print a description of the apdu
    # (class, ins, length, ...)

    raise EngineInterruptionException("A proxnroll command can not be directly"
                                      " executed, this command need to be "
                                      "piped into a transmit command",
                                      False)


@shellMethod(address=IntegerArgChecker(0, 255),
             expected=IntegerArgChecker(0, 255))
def read(address=0, expected=0):
    return ApduBuilder.readBinary(address, expected)


@shellMethod(datas=listArgChecker(IntegerArgChecker(0, 255), 1),
             address=IntegerArgChecker(0, 65535))
def update(datas, address=0):
    return ApduBuilder.updateBinary(datas, address)


@shellMethod(datas=listArgChecker(IntegerArgChecker(0, 255)),
             expected=IntegerArgChecker(0, 255),
             delay=IntegerArgChecker(0, 255))
def test(datas, expected=0, delay=0):
    return ApduBuilder.test(expected, delay, datas)


@shellMethod(
    datas=listArgChecker(IntegerArgChecker(0, 255)),
    protocol_type=tokenValueArgChecker(ApduBuilder.protocol_type),
    timeout_type=tokenValueArgChecker(ApduBuilder.timeout))
def encapsulateStandard(datas,
                        protocol_type="ISO14443_TCL",
                        timeout_type="Default"):
    return ApduBuilder.encapsulate(datas, protocol_type, timeout_type)


@shellMethod(
    datas=listArgChecker(IntegerArgChecker(0, 255)),
    protocol_type=tokenValueArgChecker(ApduBuilder.redirection),
    timeout_type=tokenValueArgChecker(ApduBuilder.timeout))
def encapsulateRedirection(datas,
                           protocol_type="MainSlot",
                           timeout_type="Default"):
    return ApduBuilder.encapsulate(datas, protocol_type, timeout_type)


@shellMethod(datas=listArgChecker(IntegerArgChecker(0, 255)),
             protocol_type=tokenValueArgChecker(ApduBuilder.lastByte),
             timeout_type=tokenValueArgChecker(ApduBuilder.timeout))
def encapsulatePartial(datas,
                       protocol_type="complete",
                       timeout_type="Default"):
    return ApduBuilder.encapsulate(datas, protocol_type, timeout_type)


@shellMethod(speed=booleanValueArgChecker("9600", "115200"))
def setSpeed(speed="9600"):
    if speed:
        return ApduBuilder.configureCalypsoSamSetSpeed9600()
    else:
        return ApduBuilder.configureCalypsoSamSetSpeed115200()


@shellMethod(acti=booleanValueArgChecker("a", "b"))
def setActivation(acti="a"):
    if acti:
        return ApduBuilder.slotControlTCLActivationTypeA()
    else:
        return ApduBuilder.slotControlTCLActivationTypeB()


@shellMethod(disable=booleanValueArgChecker("next", "every"))
def setDisable(disable="next"):
    if disable:
        return ApduBuilder.slotControlDisableNextTCL()
    else:
        return ApduBuilder.slotControlDisableEveryTCL


@shellMethod(key_index=IntegerArgChecker(0, 15),
             key=keyStoreTranslatorArgChecker(6),
             is_type_a=booleanValueArgChecker("a", "b"),
             in_volatile=booleanValueArgChecker("volatile", "notvolatile"))
def mifareLoadKey(key_index, key, is_type_a="a", in_volatile="volatile"):
    return ApduBuilder.loadKey(key_index, key, is_type_a, in_volatile)


@shellMethod(block_number=IntegerArgChecker(0, 0xff),
             key_index=IntegerArgChecker(0, 15),
             is_type_a=booleanValueArgChecker("a", "b"),
             in_volatile=booleanValueArgChecker("volatile", "notvolatile"))
def mifareAuthenticate(block_number, key_index, is_type_a="a",
                       in_volatile="volatile"):
    return ApduBuilder.generalAuthenticate(
        block_number, key_index, is_type_a, in_volatile)


@shellMethod(block_number=IntegerArgChecker(0, 0xff),
             key=keyStoreTranslatorArgChecker(6))
def mifareRead(block_number=0, key=None):
    return ApduBuilder.mifareClassicRead(block_number, key)


@shellMethod(datas=listArgChecker(IntegerArgChecker(0, 255)),
             block_number=IntegerArgChecker(0, 0xff),
             key=keyStoreTranslatorArgChecker(6))
def mifareUpdate(datas, block_number=0, key=None):
    return ApduBuilder.mifareClassifWrite(block_number, key, datas)


@shellMethod(datas=listArgChecker(IntegerArgChecker(0, 255), 3))
def parseDataCardType(datas):
    # TODO a print is used inside of this method, replace with printing system
    ss, nn = ApduBuilder.parseDataCardType(datas)

    printShell("Procole : " + ss + ", Type : " + nn)

# # REGISTER # #

# MAIN #
registerDependOnAddon("pyshell.addons.pcsc")
registerSetGlobalPrefix(("proxnroll", ))
registerStopHelpTraversalAt()
registerCommand(("setlight",), pre=setLight, pro=stopAsMainProcess)
registerCommand(("setbuzzer",), pre=setBuzzer, pro=stopAsMainProcess)
registerCommand(("vendor",),
                pre=ApduBuilder.getDataVendorName,
                pro=stopAsMainProcess,
                post=printStringCharResult)
registerCommand(("test",),
                pre=test,
                pro=stopAsMainProcess,
                post=printBytesAsString)
registerCommand(("read",), pre=read, pro=stopAsMainProcess,
                post=printBytesAsString)
registerCommand(("update",), pre=update, pro=stopAsMainProcess)
registerCommand(("hardwareIdentifier",),
                pre=ApduBuilder.getDataHarwareIdentifier,
                pro=stopAsMainProcess,
                post=printBytesAsString)

# CALYPSO #
registerSetTempPrefix(("calypso",))
registerCommand(("setspeed",), pre=setSpeed, pro=stopAsMainProcess)
registerCommand(
    ("enabledigestupdate",),
    pre=ApduBuilder.configureCalypsoSamEnableInternalDigestUpdate,
    pro=stopAsMainProcess)
registerCommand(
    ("disabledigestupdate",),
    pre=ApduBuilder.configureCalypsoSamDisableInternalDigestUpdate,
    pro=stopAsMainProcess)
registerStopHelpTraversalAt()

# PRODUCT #
registerSetTempPrefix(("product",))
registerCommand(("name",), pre=ApduBuilder.getDataProductName,
                pro=stopAsMainProcess, post=printStringCharResult)
registerCommand(("serialString",
                 ),
                pre=ApduBuilder.getDataProductSerialNumber,
                pro=stopAsMainProcess,
                post=printStringCharResult)
registerCommand(("usbidentifier",
                 ),
                pre=ApduBuilder.getDataProductUSBIdentifier,
                pro=stopAsMainProcess,
                post=printStringCharResult)
registerCommand(("version",
                 ),
                pre=ApduBuilder.getDataProductVersion,
                pro=stopAsMainProcess,
                post=printStringCharResult)
registerCommand(("serial",
                 ),
                pre=ApduBuilder.getDataProductSerialNumber,
                pro=stopAsMainProcess,
                post=printStringCharResult)
registerStopHelpTraversalAt()

# CARD #
registerSetTempPrefix(("card",))
registerCommand(("serial",
                 ),
                pre=ApduBuilder.getDataCardSerialNumber,
                pro=stopAsMainProcess,
                post=printBytesAsString)
registerCommand(("ats",),
                pre=ApduBuilder.getDataCardATS,
                pro=stopAsMainProcess,
                post=printBytesAsString)
registerCommand(("completeIdentifier",),
                pre=ApduBuilder.getDataCardCompleteIdentifier,
                pro=stopAsMainProcess,
                post=printBytesAsString)
registerCommand(("type",),
                pre=ApduBuilder.getDataCardType,
                pro=stopAsMainProcess,
                post=parseDataCardType)
registerCommand(("shortSerial",),
                pre=ApduBuilder.getDataCardShortSerialNumber,
                pro=stopAsMainProcess,
                post=printBytesAsString)
registerCommand(("atr",),
                pre=ApduBuilder.getDataCardATR,
                pro=stopAsMainProcess,
                post=printATR)
registerStopHelpTraversalAt()

# TRACKING #
registerSetTempPrefix(("control", "tracking",))
registerCommand(("resume",),
                pre=ApduBuilder.slotControlResumeCardTracking,
                pro=stopAsMainProcess)
registerCommand(("suspend",),
                pre=ApduBuilder.slotControlSuspendCardTracking,
                pro=stopAsMainProcess)
registerStopHelpTraversalAt()

# RFFIELD #
registerSetTempPrefix(("control", "rffield",))
registerCommand(("stop",),
                pre=ApduBuilder.slotControlStopRFField,
                pro=stopAsMainProcess)
registerCommand(("start",),
                pre=ApduBuilder.slotControlStartRFField,
                pro=stopAsMainProcess)
registerCommand(("reset",),
                pre=ApduBuilder.slotControlResetRFField,
                pro=stopAsMainProcess)
registerStopHelpTraversalAt()

# T=CL #
registerSetTempPrefix(("control", "t=cl",))
registerCommand(("deactivation",),
                pre=ApduBuilder.slotControlTCLDeactivation,
                pro=stopAsMainProcess)
registerCommand(("activation",), pre=setActivation, pro=stopAsMainProcess)
registerCommand(("disable",), pre=setDisable, pro=stopAsMainProcess)
registerCommand(("enable",),
                pre=ApduBuilder.slotControlEnableTCLAgain,
                pro=stopAsMainProcess)
registerCommand(
    ("reset",),
    pre=ApduBuilder.slotControlResetAfterNextDisconnectAndDisableNextTCL,
    pro=stopAsMainProcess)
registerStopHelpTraversalAt()

# STROP CONTROL #
registerSetTempPrefix(("control", ))
registerStopHelpTraversalAt()
registerCommand(("stop",), pre=ApduBuilder.slotControlStop)

# ENCAPSULATE #
# TODO try to merge these three and add the last param "defaultSW"
registerSetTempPrefix(("encapsulate", ))
registerCommand(("standard",),
                pre=encapsulateStandard,
                pro=stopAsMainProcess,
                post=printBytesAsString)
registerCommand(("redirection",),
                pre=encapsulateRedirection,
                pro=stopAsMainProcess,
                post=printBytesAsString)
registerCommand(("partial",),
                pre=encapsulatePartial,
                pro=stopAsMainProcess,
                post=printBytesAsString)
registerStopHelpTraversalAt()

# MIFARE #
registerSetTempPrefix(("mifare", ))
registerCommand(("loadkey",), pre=mifareLoadKey, pro=stopAsMainProcess)
registerCommand(("authenticate",),
                pre=mifareAuthenticate,
                pro=stopAsMainProcess)
registerCommand(("read",),
                pre=mifareRead,
                pro=stopAsMainProcess,
                post=printBytesAsString)
registerCommand(("update",), pre=mifareUpdate, pro=stopAsMainProcess)
registerStopHelpTraversalAt()
