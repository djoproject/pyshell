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

from pyshell.arg.accessor.default import DefaultAccessor
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.arg.checker.token43 import TokenValueArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.command.procedure import FileProcedure
from pyshell.register.command import registerCommand
from pyshell.register.command import registerSetGlobalPrefix
from pyshell.register.command import registerStopHelpTraversalAt
from pyshell.system.setting.procedure import DEFAULT_CHECKER
from pyshell.utils.constants import ENABLE_ON_POST_PROCESS
from pyshell.utils.constants import ENABLE_ON_PRE_PROCESS
from pyshell.utils.constants import ENABLE_ON_PROCESS


_ENABLED_ON = {ENABLE_ON_PRE_PROCESS: ENABLE_ON_PRE_PROCESS,
               ENABLE_ON_PROCESS: ENABLE_ON_PROCESS,
               ENABLE_ON_POST_PROCESS: ENABLE_ON_POST_PROCESS}


# ## COMMAND SECTION ## #

@shellMethod(procedure=DefaultAccessor.getProcedure(),
             args=ListArgChecker(DefaultChecker.getArg()),
             parameters=DefaultAccessor.getContainer(),
             exchange=DefaultAccessor.getExchange())
def startNamedProcedure(procedure, args, parameters=None, exchange=None):
    "start a procedure stored into manager"
    return startProcedure(file_path=procedure.getValue(),
                          args=args,
                          granularity=procedure.settings.getErrorGranularity(),
                          enable_on=procedure.settings.getEnableOn(),
                          parameters=parameters,
                          exchange=exchange)


@shellMethod(file_path=DEFAULT_CHECKER,
             args=ListArgChecker(DefaultChecker.getArg()),
             granularity=IntegerArgChecker(minimum=-1),
             enable_on=TokenValueArgChecker(_ENABLED_ON),
             parameters=DefaultAccessor.getContainer(),
             exchange=DefaultAccessor.getExchange())
def startProcedure(file_path,
                   args,
                   granularity=-1,
                   enable_on=ENABLE_ON_PROCESS,
                   parameters=None,
                   exchange=None):
    "start a procedure stored into file"
    procedure = FileProcedure(file_path=file_path,
                              execute_on=enable_on,
                              granularity=granularity)

    exchange["procedure"] = procedure
    exchange["enable_on"] = enable_on

    if exchange["enable_on"] is ENABLE_ON_PRE_PROCESS:
        return procedure.execute(parameter_container=parameters, args=args)

    return args


@shellMethod(args=ListArgChecker(DefaultChecker.getArg()),
             parameters=DefaultAccessor.getContainer(),
             exchange=DefaultAccessor.getExchange())
def _process(args, parameters=None, exchange=None):
    if exchange["enable_on"] is ENABLE_ON_PROCESS:
        procedure = exchange["procedure"]
        return procedure.execute(parameter_container=parameters, args=args)

    return args


@shellMethod(args=ListArgChecker(DefaultChecker.getArg()),
             parameters=DefaultAccessor.getContainer(),
             exchange=DefaultAccessor.getExchange())
def _postProcess(args, parameters=None, exchange=None):
    if exchange["enable_on"] is ENABLE_ON_POST_PROCESS:
        procedure = exchange["procedure"]
        return procedure.execute(parameter_container=parameters, args=args)

    return args

# ## REGISTER SECTION ## #

registerSetGlobalPrefix(("procedure", ))
registerStopHelpTraversalAt()
registerCommand(("execute", "file",),
                pre=startProcedure,
                pro=_process,
                post=_postProcess)
registerCommand(("execute", "name",),
                pre=startNamedProcedure,
                pro=_process,
                post=_postProcess)
registerStopHelpTraversalAt(("execute",))
