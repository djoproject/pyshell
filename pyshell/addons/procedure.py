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

# TODO Brainstorming about procedure
#   Now there are two procedure object:
#       - ProcedureParameter: hold every information that can be saved
#       - ProcedureFile: hold the execution mechanism of a procedure
#
#   ProcedureParameter instances should be stored into a parameterManager
#   and ProcedureFile instances should be stored into a commandManager.
#   The commandManager does not exist yet (see issue #109)
#
#   Not a huge fan to store two different object talking about the same stuff
#   inside two separate manager.
#
#   SOLUTION 1: keep like this in both manager
#       PRBLM 1.1 had to manage if error occurs in one of the two manager and
#           the procedure is no more available in the other, really painful...
#       SOL 1.1 give tools to (re)bind a command to a procedure_parameter
#
#   SOLUTION 2: only put in CommandManager
#       PRBLM 2.1 How to update settings about the command ?
#       PRBLM 2.2 In case of possibility to update settings, how to save them?
#           CommandManager is supposed to be transient
#
#   SOLUTION 3: only put in ParameterManager
#       PRBLM 3.1 need to create a special command to run the procedure, not
#           intuitive, but easy to implement
#
#   SOLUTION 4: only put in ParameterManager + create alias to the special
#       command.
#       PRBLM 4.1 alias is not implemented
#       PRBLM 4.2 same issue as SOLUTION 1
#
#   SOLUTION 5:
#
# TODO there is no registering system for procedure, create it (?)
# TODO create an issue about all of this ?


from pyshell.arg.accessor.default import DefaultAccessor
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.command.procedure import FileProcedure
from pyshell.register.command import registerCommand
from pyshell.register.command import registerSetGlobalPrefix
from pyshell.register.command import registerStopHelpTraversalAt
from pyshell.system.parameter.procedure import ProcedureParameter

# ## COMMAND SECTION ## #


def startNamedProcedure(name, args):
    "start a registered script file"
    # TODO create a procedure manager + update parameter addons to manage them
    # TODO retrieve a stored procedure, then call it
    pass


# TODO add granularity argument
# TODO add ENABLE_ON argument
@shellMethod(file_path=DefaultChecker.getString(),
             args=ListArgChecker(DefaultChecker.getArg()),
             parameters=DefaultAccessor.getContainer())
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
