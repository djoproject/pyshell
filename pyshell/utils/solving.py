#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

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

from tries import multiLevelTries
from tries.exception import triesException

from pyshell.arg.checker.boolean import BooleanValueArgChecker
from pyshell.arg.checker.default import DefaultChecker
from pyshell.command.engine import EMPTY_MAPPED_ARGS
from pyshell.system.manager.variable import VariableParameterManager
from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.exception import SYSTEM_ERROR
from pyshell.utils.exception import USER_WARNING
from pyshell.utils.parsing import Parser


class Solver(object):
    def solve(self, parser, mltries, variables_container):
        if not isinstance(parser, Parser):
            excmsg = ("("+self.__class__.__name__+") __init__, fail to init "
                      "solver, a parser object was expected, got '" +
                      str(type(parser))+"'")
            raise DefaultPyshellException(excmsg, SYSTEM_ERROR)

        if not parser.isParsed():
            excmsg = ("("+self.__class__.__name__+") __init__, fail to init "
                      "solver, parser object is not yet parsed")
            raise DefaultPyshellException(excmsg, SYSTEM_ERROR)

        if not isinstance(variables_container, VariableParameterManager):
            excmsg = ("("+self.__class__.__name__+") __init__, fail to init "
                      "solver, a VariableParameterManager object was expected,"
                      " got '"+str(type(variables_container))+"'")
            raise DefaultPyshellException(excmsg, SYSTEM_ERROR)

        if not isinstance(mltries, multiLevelTries):
            excmsg = ("("+self.__class__.__name__+") __init__, fail to init "
                      "solver, a multiLevelTries object was expected, got '" +
                      str(type(mltries)) + "'")
            raise DefaultPyshellException(excmsg, SYSTEM_ERROR)

        self.parser = parser
        self.mltries = mltries
        self.variables_container = variables_container

        command_list = []
        command_name_list = []
        arg_list = []
        mapped_args_list = []

        for token_list, arg_spotted, param_spotted in self.parser:
            if len(param_spotted) > 0:
                param_spotted = list(param_spotted)

            token_list = self._solveVariables(token_list,
                                              arg_spotted,
                                              param_spotted)
            command, remaining_token_list = self._solveCommands(token_list)

            command_token_length = len(token_list) - len(remaining_token_list)
            command_name_list.append(tuple(token_list[0:command_token_length]))

            _removeEveryIndexUnder(param_spotted, command_token_length)
            _addValueToIndex(param_spotted,
                             0,
                             len(remaining_token_list) - len(token_list))

            mapped_params, remaining_token_list = self._solveDashedParameters(
                command,
                remaining_token_list,
                param_spotted)

            command_list.append(command)
            arg_list.append(remaining_token_list)
            mapped_args_list.append(mapped_params)

        return command_list, arg_list, mapped_args_list, command_name_list

    def _solveVariables(self, token_list, arg_spotted, param_spotted):
        """
        replace argument like `$toto` into their value in parameter,
        the input must come from the output of the method parseArgument
        """

        # no arg spotted
        if len(arg_spotted) == 0:
            return token_list

        token_list = list(token_list)
        index_correction = 0

        for arg_index in arg_spotted:
            arg_index += index_correction

            # get the token and remove $
            string_token = token_list[arg_index][1:]

            # remove old key from token list
            del token_list[arg_index]

            # if not existing var, act as an empty var
            var = self.variables_container.getParameter(string_token)
            if var is None:
                var_size = 0
            else:
                # insert the var list at the correct place
                # (var is always a list)
                values = var.getValue()
                pre_list = token_list[0:arg_index]
                post_list = token_list[arg_index:]
                token_list = pre_list + values + post_list
                var_size = len(values)

            # update every spotted param index with an index bigger than
            # the var if the value of the var is different of 1
            if var_size != 1:
                index_correction += var_size-1
                _addValueToIndex(param_spotted, arg_index+1, index_correction)

        return token_list

    def _solveCommands(self, token_list):
        "indentify command name and args from output of method parseArgument"

        # search the command with advanced seach
        search_result = None
        try:
            search_result = self.mltries.advancedSearch(token_list, False)
        except triesException as te:
            excmsg = ("("+self.__class__.__name__+") _solveCommands, failed to"
                      " find the command '"+str(token_list)+"', reason: " +
                      str(te))
            raise DefaultPyshellException(excmsg, USER_WARNING)

        # ambiguity on the last token used
        if search_result.isAmbiguous():
            token_index = len(search_result.existingPath) - 1
            tries = search_result.existingPath[token_index][1].localTries
            keylist = tries.getKeyList(token_list[token_index])

            excmsg = ("("+self.__class__.__name__+") _solveCommands, ambiguity"
                      " on command '"+" ".join(token_list)+"', token '" +
                      str(token_list[token_index])+"', possible value: " +
                      ", ".join(keylist))
            raise DefaultPyshellException(excmsg, USER_WARNING)

        # no value on the last token found OR no token found
        elif not search_result.isAvalueOnTheLastTokenFound():
            if search_result.getTokenFoundCount() == len(token_list):
                excmsg = ("("+self.__class__.__name__+") _solveCommands, "
                          "uncomplete command '"+" ".join(token_list)+"', type"
                          " help "+" ".join(token_list)+"' to get the next "
                          "available parts of this command")
                raise DefaultPyshellException(excmsg, USER_WARNING)

            if len(token_list) == 1:
                excmsg = ("("+self.__class__.__name__+") _solveCommands, "
                          "unknown command '"+" ".join(token_list)+"', "
                          "type 'help' to get the list of commands")
                raise DefaultPyshellException(excmsg, USER_WARNING)

            # TODO improve the help message build here, use the found tokens
            # to suggest help command to use
            token_found = str(token_list[search_result.getTokenFoundCount()])
            excmsg = ("("+self.__class__.__name__+") _solveCommands, unknown "
                      "command '"+" ".join(token_list)+"', token '" +
                      token_found+"' is unknown, type 'help' to get the list "
                      "of commands")
            raise DefaultPyshellException(excmsg, USER_WARNING)

        # return the command found and the not found token
        return (search_result.getLastTokenFoundValue(),
                list(search_result.getNotFoundTokenList()),)

    def _solveDashedParameters(self,
                               command,
                               remaining_token_list,
                               param_spotted):
        # empty command list, nothing to map
        if len(command) == 0 or len(param_spotted) == 0:
            return (EMPTY_MAPPED_ARGS,
                    EMPTY_MAPPED_ARGS,
                    EMPTY_MAPPED_ARGS,), remaining_token_list

        # get multi-command entry command, the first command
        firstSingleCommand, useArgs, enabled = command[0]

        # extract arfeeder
        if ((not hasattr(firstSingleCommand.preProcess, "isDefault") or
             not firstSingleCommand.preProcess.isDefault) and
           hasattr(firstSingleCommand.preProcess, "checker")):
            feeder = firstSingleCommand.preProcess.checker
            index_to_set = 0
        elif ((not hasattr(firstSingleCommand.process, "isDefault") or
               not firstSingleCommand.process.isDefault) and
              hasattr(firstSingleCommand.process, "checker")):
            feeder = firstSingleCommand.process.checker
            index_to_set = 1
        elif ((not hasattr(firstSingleCommand.postProcess, "isDefault") or
               not firstSingleCommand.postProcess.isDefault) and
              hasattr(firstSingleCommand.postProcess, "checker")):
            feeder = firstSingleCommand.postProcess.checker
            index_to_set = 2
        else:
            return (EMPTY_MAPPED_ARGS,
                    EMPTY_MAPPED_ARGS,
                    EMPTY_MAPPED_ARGS,), remaining_token_list

        # compute arg mapping for this command
        local_mapped_args = [EMPTY_MAPPED_ARGS,
                             EMPTY_MAPPED_ARGS,
                             EMPTY_MAPPED_ARGS]
        param_found, remainingArgs = _mapDashedParams(remaining_token_list,
                                                      feeder.arg_type_list,
                                                      param_spotted)
        local_mapped_args[index_to_set] = param_found

        return local_mapped_args, remainingArgs


def _removeEveryIndexUnder(index_list, end_index):
    for i in range(0, len(index_list)):
        if index_list[i] < end_index:
            continue

        del index_list[:i]
        return

    if len(index_list) > 0:
        del index_list[:]


def _addValueToIndex(index_list, starting_index, value_to_add=1):
    for i in range(0, len(index_list)):
        if index_list[i] < starting_index:
            continue

        index_list[i] += value_to_add


def _mapDashedParams(input_args, arg_type_map, param_spotted):
    if len(param_spotted) == 0:
        return {}, input_args

    not_used_args = []
    param_found = {}

    current_name = None
    current_param = None
    current_index = 0

    for index in param_spotted:
        param_name = input_args[index][1:]

        # remove false param
        if param_name not in arg_type_map:
            continue

        # manage last met param
        if current_param is not None:
            _mapDashedParamsManageParam(input_args,
                                        current_name,
                                        current_param,
                                        current_index,
                                        param_found,
                                        not_used_args,
                                        index)
        else:
            # base case, process the first param index, need to flush
            # available arg before this index
            not_used_args.extend(input_args[0:index])

        current_name = param_name
        current_param = arg_type_map[param_name]
        current_index = index

    # never found any valid and existing param
    if current_param is None:
        return {}, input_args

    # manage last param
    _mapDashedParamsManageParam(input_args,
                                current_name,
                                current_param,
                                current_index,
                                param_found,
                                not_used_args,
                                len(input_args))

    return param_found, not_used_args


def _mapDashedParamsManageParam(input_args,
                                current_name,
                                current_param,
                                current_index,
                                param_found,
                                not_used_args,
                                last_index):
    arg_available_count = last_index - current_index - 1

    # special case for boolean, parameter alone is equivalent to true
    if isinstance(current_param, BooleanValueArgChecker):
        if arg_available_count == 0:
            param_found[current_name] = ("true",)
        elif _isValidBooleanValueForChecker(input_args[current_index+1]):
            param_found[current_name] = (input_args[current_index+1],)
            not_used_args.extend(input_args[current_index+2:last_index])
        else:
            param_found[current_name] = ("true",)
            not_used_args.extend(input_args[current_index+1:last_index])
    else:
        # did we reach max size ?
        # don't care about minimum size, it will be check during
        # execution phase
        if (current_param.getMaximumSize() is not None and
           current_param.getMaximumSize() < arg_available_count):
            pivot = current_index+1+current_param.getMaximumSize()
            param_found[current_name] = tuple(
                input_args[current_index+1:pivot])
            not_used_args.extend(input_args[pivot:last_index])
        else:
            params = tuple(input_args[current_index+1:last_index])
            param_found[current_name] = params


def _isValidBooleanValueForChecker(value):
    try:
        DefaultChecker.getBoolean().getValue(value)
        return True
    except Exception:
        return False
