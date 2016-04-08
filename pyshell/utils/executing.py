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

import threading

from pyshell.arg.exception import ArgException
from pyshell.command.engine import EngineV3
from pyshell.command.exception import CommandException
from pyshell.command.exception import EngineInterruptionException
from pyshell.command.exception import ExecutionException
from pyshell.command.exception import ExecutionInitException
from pyshell.system.variable import VarParameter
from pyshell.utils.constants import CONTEXT_EXECUTION_KEY
from pyshell.utils.constants import CONTEXT_EXECUTION_SHELL
from pyshell.utils.constants import DEBUG_ENVIRONMENT_NAME
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.exception import CORE_ERROR
from pyshell.utils.exception import CORE_WARNING
from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.exception import ListOfException
from pyshell.utils.parsing import Parser
from pyshell.utils.printing import printException
from pyshell.utils.solving import Solver

# execute return engine and last_exception to the calling procedure
#   engine to retrieve any output
#   exception, to check granularity and eventually stop the execution


def execute(string, parameter_container, process_name=None, process_arg=None):
    # add external parameters at the end of the command
    if hasattr(process_arg, "__iter__"):
        string += " " + ' '.join(str(x) for x in process_arg)
    elif type(process_arg) == str or type(process_arg) == unicode:
        string += " "+process_arg
    elif process_arg is not None:
        raise DefaultPyshellException("unknown type or process args, expect a "
                                      "list or a string, got '" +
                                      type(process_arg)+"'",
                                      CORE_ERROR)

    # # parsing # #
    parser = None
    try:
        # parsing
        if isinstance(string, Parser):
            parser = string

            if not parser.isParsed():
                parser.parse()
        else:
            parser = Parser(string)
            parser.parse()

        # no command to execute
        if len(parser) == 0:
            return None, None

    except Exception as ex:
        printException(ex, "Fail to parse command: ")
        return ex, None

    if parser.isToRunInBackground():
        t = threading.Thread(None, _execute, None, (parser,
                                                    parameter_container,
                                                    process_name,))
        t.start()
        parameter_container.variable.setParameter("!",
                                                  VarParameter(str(t.ident)),
                                                  local_param=True)

        # not possible to retrieve exception or engine, it is another thread
        return None, None
    else:
        return _execute(parser, parameter_container, process_name)


def _generateSuffix(parameter_container,
                    command_name_list=None,
                    engine=None,
                    process_name=None):

    # TODO process_name then command_name_list should appear first if not None

    # print if in debug ?
    param = parameter_container.context.getParameter(DEBUG_ENVIRONMENT_NAME,
                                                     perfect_match=True)
    show_advanced_result = (param is not None and param.getSelectedValue() > 0)

    if not show_advanced_result:
        # is is a shell execution ?
        param = parameter_container.context.getParameter(CONTEXT_EXECUTION_KEY,
                                                         perfect_match=True)
        show_advanced_result = (param is None or
                                param.getSelectedValue() !=
                                CONTEXT_EXECUTION_SHELL)

    if (show_advanced_result or
       not parameter_container.isMainThread()):
        thread_id = parameter_container.getCurrentId()
        message = " (threadId="+str(thread_id)

        if process_name is not None:
            message += ", process='"+str(process_name)+"'"

        if (command_name_list is not None and
           engine is not None and
           not engine.stack.isEmpty()):
            command_index = engine.stack.cmdIndexOnTop()
            message += (", command='%s'" %
                        " ".join(command_name_list[command_index]))

        message += ")"

        return message
    return None


def _execute(parser, parameter_container, process_name=None):
    # # solving then execute # #
    ex = None
    engine = None
    command_name_list = None
    try:
        # solve command, variable, and dashed parameters
        env = parameter_container.environment
        mltries_param = env.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY)

        if mltries_param is None:
            raise DefaultPyshellException("Fail to execute the command,"
                                          " no levelTries defined",
                                          CORE_ERROR)

        mltries = mltries_param.getValue()
        rawCommandList, rawArgList, mappedArgs, command_name_list = \
            Solver().solve(parser, mltries, parameter_container.variable)
        # clone command/procedure to manage concurrency state
        new_raw_command_list = []
        for i in range(0, len(rawCommandList)):
            c = rawCommandList[i].clone()

            # check if there is at least one empty command, if yes, raise
            if len(c) == 0:
                raise DefaultPyshellException("Command '%s' is empty, not "
                                              "possible to execute" %
                                              " ".join(command_name_list[i]),
                                              CORE_WARNING)

            new_raw_command_list.append(c)

        # prepare an engine
        engine = EngineV3(new_raw_command_list,
                          rawArgList,
                          mappedArgs,
                          parameter_container)

        # execute
        engine.execute()

    except ExecutionInitException as ex:
        printException(ex,
                       prefix="Fail to init an execution object: ",
                       suffix=_generateSuffix(
                           parameter_container,
                           command_name_list=command_name_list,
                           engine=engine,
                           process_name=process_name))
    except ExecutionException as ex:
        printException(ex,
                       prefix="Fail to execute: ",
                       suffix=_generateSuffix(
                           parameter_container,
                           command_name_list=command_name_list,
                           engine=engine,
                           process_name=process_name))
    except CommandException as ex:
        printException(ex,
                       prefix="Error in command method: ",
                       suffix=_generateSuffix(
                           parameter_container,
                           command_name_list=command_name_list,
                           engine=engine,
                           process_name=process_name))
    except EngineInterruptionException as ex:
        suffix = _generateSuffix(parameter_container,
                                 command_name_list=command_name_list,
                                 engine=engine,
                                 process_name=process_name)
        if ex.abnormal:
            printException(ex,
                           prefix="Abnormal execution abort, reason: ",
                           suffix=suffix)
        else:
            printException(ex,
                           prefix="Normal execution abort, reason: ",
                           suffix=suffix)
    except ArgException as ex:
        printException(ex,
                       prefix="Error while parsing argument: ",
                       suffix=_generateSuffix(
                           parameter_container,
                           command_name_list=command_name_list,
                           engine=engine,
                           process_name=process_name))
    except ListOfException as ex:
        printException(ex,
                       prefix="List of exception(s): ",
                       suffix=_generateSuffix(
                           parameter_container,
                           command_name_list=command_name_list,
                           engine=engine,
                           process_name=process_name))
    except Exception as ex:
        printException(ex,
                       suffix=_generateSuffix(
                           parameter_container,
                           command_name_list=command_name_list,
                           engine=engine,
                           process_name=process_name))

    return ex, engine
