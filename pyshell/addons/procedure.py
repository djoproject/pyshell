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


from pyshell.arg.argchecker import DefaultInstanceArgChecker as DefaultArgs
from pyshell.arg.argchecker import ListArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.loader.command import registerCommand
from pyshell.loader.command import registerSetGlobalPrefix
from pyshell.loader.command import registerStopHelpTraversalAt
from pyshell.system.procedure import FileProcedure

# ## COMMAND SECTION ## #


def startNamedProcedure(name, args):
    "start a registered script file"
    # TODO create a procedure manager + update parameter addons to manage them
    # TODO retrieve a stored procedure, then call it
    pass


@shellMethod(
    file_path=DefaultArgs.getStringArgCheckerInstance(),
    args=ListArgChecker(DefaultArgs.getArgCheckerInstance()),
    parameters=DefaultArgs.getCompleteEnvironmentChecker())
def startProcedure(file_path, args, parameters):
    "start a script file"
    procedure = FileProcedure(file_path=file_path)

    # TODO this is wrong, it shouln't call the execute method
    # but each meths pre/pro/post of the procedure must be called
    procedure.execute(parameters=parameters, args=args)

# ## REGISTER SECTION ## #

registerSetGlobalPrefix(("procedure", ))
registerStopHelpTraversalAt()
registerCommand(("execute",), pro=startProcedure)
