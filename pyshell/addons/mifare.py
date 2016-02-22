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

from apdu.tag.mifareUltralight import MifareUltralightAPDUBuilder

from pyshell.arg.argchecker import IntegerArgChecker
from pyshell.arg.argchecker import ListArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.loader.command import registerCommand
from pyshell.loader.command import registerSetGlobalPrefix
from pyshell.loader.command import registerSetTempPrefix
from pyshell.loader.command import registerStopHelpTraversalAt

# TODO
#   ultralight c authentication is missing
#       also register default key

#   map all the mifare card (classic, desfire, plus, ...)

#   add a process like proxnroll to say that a command should be used with
#   pipe only


@shellMethod(sector=IntegerArgChecker(0))
def mifareUltraLightRead(sector=0):
    return MifareUltralightAPDUBuilder.readSector(sector)


# TODO retry with LimitedInteger
@shellMethod(sector=IntegerArgChecker(0),
             data=ListArgChecker(IntegerArgChecker(0, 255), 1))
def mifareUltraLightWrite(sector, data, compatibility=False):
    if compatibility:
        return MifareUltralightAPDUBuilder.CompatibilityWrite(data, sector)
    else:
        return MifareUltralightAPDUBuilder.writeSector(data, sector)


registerSetGlobalPrefix(("mifare",))
registerStopHelpTraversalAt()


registerSetTempPrefix(("ultralight",))
registerCommand(("read",), pre=mifareUltraLightRead)
registerCommand(("write",), pre=mifareUltraLightWrite)
registerStopHelpTraversalAt()
