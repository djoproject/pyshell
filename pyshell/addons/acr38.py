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

from apdu.readers.acr38u import acr38uAPDUBuilder

from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.arg.checker.token43 import TokenValueArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.command.exception import EngineInterruptionException
from pyshell.register.command import registerCommand
from pyshell.register.command import registerSetGlobalPrefix
from pyshell.register.command import registerSetTempPrefix


@shellMethod(anything=ListArgChecker(DefaultChecker.getArg()))
def stopAsMainProcess(anything):
    # TODO in place of printing an error, print a description of the apdu
    # (class, ins, length, ...)

    excmsg = ("An acr38 command can not be directly executed, this command "
              "need to be piped into a transmit command")
    raise EngineInterruptionException(excmsg, False)


@shellMethod(card_type=TokenValueArgChecker(acr38uAPDUBuilder.SELECT_TYPE))
def selectFun(card_type="AUTO"):
    return acr38uAPDUBuilder.selectType(card_type)

"""@shellMethod(address = IntegerArgChecker(0,0x3ff),
             length  = IntegerArgChecker(0,0xff))
def readFun(address = 0, length = 0):
    return acr38uAPDUBuilder.read(address, length)

@shellMethod(datas   = ListArgChecker(IntegerArgChecker(0,255)),
             address = IntegerArgChecker(0,65535))
def writeFun(datas, address=0):
    return acr38uAPDUBuilder.write(address, datas)

@shellMethod(pin = ListArgChecker(IntegerArgChecker(0,255),2,2))
def checkPin(pin):
    return acr38uAPDUBuilder.checkPinCode(pin)"""


# # I2C # #
# TODO should be splited into 16k and 1024k ???

@shellMethod(card_type=TokenValueArgChecker(
    {"I2C_1KTO16K": acr38uAPDUBuilder.TYPE_I2C_1KTO16K,
     "I2C_32KTO1024K": acr38uAPDUBuilder.TYPE_I2C_32KTO1024K}))
def i2cSelect(card_type="I2C_1KTO16K"):
    return acr38uAPDUBuilder.selectType(card_type)


@shellMethod(size=TokenValueArgChecker(acr38uAPDUBuilder.I2C_PAGE_SIZE))
def i2cSelectPageSize(size="8BYTES"):
    return acr38uAPDUBuilder.I2C_selectPageSize(size)


@shellMethod(adress=IntegerArgChecker(0, 0x1ffff),
             length=IntegerArgChecker(0, 0xff))
def i2cRead(adress=0, length=0):
    return acr38uAPDUBuilder.read(adress, length)


@shellMethod(adress=IntegerArgChecker(0, 0x1ffff),
             datas=ListArgChecker(IntegerArgChecker(0, 255)))
def i2cWrite(datas, adress=0):
    return acr38uAPDUBuilder.write(adress, datas)

# # SLE # #

# # ATMEL # #

# ## REGISTERING PART ## #

# # MISC # #

registerSetGlobalPrefix(("acr38", ))
registerCommand(("select",), pre=selectFun, pro=stopAsMainProcess)
# registerCommand( ( "read",),  pre=readFun, pro=stopAsMainProcess)
# registerCommand( ( "write",),  pre=writeFun, pro=stopAsMainProcess)
# registerSetTempPrefix( ("pin", ) )
# registerCommand( ( "check",),  pre=checkPin, pro=stopAsMainProcess)

# # IC2 # #

registerSetTempPrefix(("ic2",))
registerCommand(("select",), pre=i2cSelect, pro=stopAsMainProcess)
registerCommand(("pagesize",), pre=i2cSelectPageSize, pro=stopAsMainProcess)
registerCommand(("read",), pre=i2cRead, pro=stopAsMainProcess)
registerCommand(("write",), pre=i2cWrite, pro=stopAsMainProcess)
