#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2012  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.command.command import Command
from pyshell.command.command import MultiCommand
from pyshell.command.command import MultiOutput
from pyshell.command.exception import EngineInterruptionException
from pyshell.command.exception import ExecutionException
from pyshell.command.exception import ExecutionInitException
from pyshell.command.stackEngine import EngineStack
from pyshell.command.utils import equalMap
from pyshell.command.utils import equalPath
from pyshell.command.utils import isAValidIndex
from pyshell.command.utils import raisIfInvalidMap  # TODO fix grammar error
from pyshell.command.utils import raiseIfInvalidPath
from pyshell.system.container import ParameterContainer
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.environment import ParametersLocker
from pyshell.utils.synchronized import FAKELOCK

# TODO TO TEST
#   None type: create a cmd that allow to return None or not, and test
#   args has moved in engine contructor, update test and create new one
#   to test the new condition
#   test insertion of data in the future
#   action after process execution (addpath, reset index, skipcount)

DEFAULT_EXECUTION_LIMIT = 255
PREPROCESS_INSTRUCTION = 0
PROCESS_INSTRUCTION = 1
POSTPROCESS_INSTRUCTION = 2


class _EmptyDataToken(object):
    pass

EMPTY_DATA_TOKEN = _EmptyDataToken()
EMPTY_MAPPED_ARGS = {}


class EngineV3(object):
    # ##  INIT # ##
    def __init__(self, cmd_list, args_list, mapped_args_list, env=None):
        # cmd must be a not empty list
        if cmd_list is None or \
           not isinstance(cmd_list, list) or \
           len(cmd_list) == 0:
            raise ExecutionInitException("(engine) init, command list is not "
                                         "a valid populated list")

        if args_list is None or \
           not isinstance(args_list, list) or \
           len(args_list) != len(cmd_list):
            raise ExecutionInitException("(engine) init, arg list is not a "
                                         "valid populated list of equal size "
                                         "with the command list")

        if mapped_args_list is None or \
           not isinstance(mapped_args_list, list) or \
           len(mapped_args_list) != len(cmd_list):
            raise ExecutionInitException("(engine) init, mapped arg list is "
                                         "not a valid populated list of equal "
                                         "size with the command list")

        # reset every commands
        for i in range(0, len(cmd_list)):
            c = cmd_list[i]

            if not isinstance(c, MultiCommand):
                raise ExecutionInitException("(engine) init, item <"+str(i) +
                                             "> in the command list is not a "
                                             "MultiCommand instance, got '" +
                                             str(type(c))+"'")

            if len(c) == 0:  # empty multi command are not allowed
                raise ExecutionInitException("(engine) init, a command is "
                                             "empty")

            if args_list[i] is not None and not isinstance(args_list[i], list):
                raise ExecutionInitException("(engine) init, item <"+str(i) +
                                             "> in the arg list is different "
                                             "of None or List instance")

            # reset the information stored in the command from a previous
            # execution
            c.reset()

        self.args_list = args_list
        self.cmd_list = cmd_list  # list of MultiCommand
        self.mapped_args_list = mapped_args_list

        # check env variable
        if env is None:
            self.env = ParameterContainer()
        elif isinstance(env, ParameterContainer):
            self.env = env
        else:
            raise ExecutionInitException("(engine) init, env must be an "
                                         "instance of ParameterContainer or "
                                         "None, got '"+str(type(env))+"'")

        self.stack = EngineStack()
        self._isInProcess = False
        self.selfkillreason = None
        self.topPreIndexOpp = None
        self.topProcessToPre = False
        self.lastResult = None

        # init stack with a None data, on the subcmd 0 of the command 0,
        # with a preprocess action

        # init data to start the engine
        self.stack.push([EMPTY_DATA_TOKEN], [0], PREPROCESS_INSTRUCTION)

    def _getTheIndexWhereToStartTheSearch(self, process_type):
        # check process_type, must be pre/pro/post
        if process_type != PREPROCESS_INSTRUCTION and \
           process_type != PROCESS_INSTRUCTION and \
           process_type != POSTPROCESS_INSTRUCTION:
            raise ExecutionException("(engine) "
                                     "_getTheIndexWhereToStartTheSearch, "
                                     "unknown process type : " +
                                     str(process_type))

        # check stack size
        stack_length = self.stack.size()

        # if stack is empty, the new data can be directly inserted
        if stack_length == 0:
            return 0

        # find the place to start the lookup
        if process_type != POSTPROCESS_INSTRUCTION:
            for i in range(0, stack_length):
                if (self.stack.typeOnDepth(i) == POSTPROCESS_INSTRUCTION or
                    (self.stack.typeOnDepth(i) == PROCESS_INSTRUCTION and
                     process_type == PREPROCESS_INSTRUCTION)):
                    continue

                # we reach the bottomest item of the wanted type
                return stack_length - i - 1

            # we don't find this type on the stack
            return -1

        # for POSTPROCESS_INSTRUCTION only, start on the top
        return stack_length - 1

    def _findIndexToInject(self, cmd_path, process_type):
        # check command path
        raiseIfInvalidPath(cmd_path, self.cmd_list, "_findIndexToInject")

        # if look up for a PROCESS, the path must always be a root path
        if (process_type == PROCESS_INSTRUCTION and
           len(cmd_path) != len(self.cmd_list)):
            raise ExecutionException("(engine) _findIndexToInjectProOrPost, "
                                     "can only insert data to the process of "
                                     "the last command")

        # check first index to look (this will also check
        # if process_type is valid)
        index = self._getTheIndexWhereToStartTheSearch(process_type)
        to_ret = None

        while index >= 0 and process_type == self.stack.typeOnIndex(index):
            equals, same_length, equals_count, path1_is_higher = \
                equalPath(self.stack[index][1], cmd_path)

            if equals:
                if process_type != PREPROCESS_INSTRUCTION:
                    return self.stack[index], index
                else:
                    if to_ret is None:
                        to_ret = []

                    to_ret.append((self.stack[index], index,))

            elif (process_type == PREPROCESS_INSTRUCTION and
                  same_length and equals_count == len(cmd_path)-1):
                if to_ret is None:
                    to_ret = []

                to_ret.append((self.stack[index], index,))

            # A lower path has been found on the stack, no way to find
            # a better path
            elif ((path1_is_higher is not None and path1_is_higher) or
                  len(self.stack[index][1]) < len(cmd_path)):
                break

            index -= 1

        # special case for PREPROCESS_INSTRUCTION, list of result
        if to_ret is not None:
            return to_ret

        if process_type == PREPROCESS_INSTRUCTION:
            return ((None, index+1,),)
        else:
            return None, index+1

    def _injectDataProOrPos(self,
                            data,
                            cmd_path,
                            process_type,
                            only_append=False):
        obj, index = self._findIndexToInject(cmd_path, process_type)

        if obj is None:
            # can only append ?
            if only_append:
                raise ExecutionException("(engine) injectDataProOrPos, there "
                                         "is no similar item on the stack and "
                                         "the system can only append, "
                                         "not create")

            if self._isInProcess and index >= self.stack.size():
                raise ExecutionException("(engine) _injectDataProOrPos, try "
                                         "to insert data in the future")

            # insert a new object
            self.stack.insert(index,
                              ([data], cmd_path[:], process_type, None,))

        else:
            obj[0].append(data)

    def injectDataPro(self, data, cmd_path, process_type, only_append=False):
        self._injectDataProOrPos(data,
                                 cmd_path,
                                 PROCESS_INSTRUCTION,
                                 only_append)

    def injectDataPost(self, data, cmd_path, process_type, only_append=False):
        self._injectDataProOrPos(data,
                                 cmd_path,
                                 POSTPROCESS_INSTRUCTION,
                                 only_append)

    def injectDataPre(self,
                      data,
                      cmd_path,
                      enabling_map=None,
                      only_append=False,
                      if_no_match_execute_sooner_as_possible=True):
        item_candidate_list = self._findIndexToInject(cmd_path,
                                                      PREPROCESS_INSTRUCTION)

        # check map (is a list, valid length, only boolean value)
        raisIfInvalidMap(enabling_map,
                         len(self.cmd_list[len(cmd_path)-1]),
                         "injectDataPre")

        # no match
        if len(item_candidate_list) == 1 and item_candidate_list[0][0] is None:
            if only_append:
                raise ExecutionException("(engine) injectDataPre, no "
                                         "corresponding item on the stack")

            if (self._isInProcess and
               item_candidate_list[0][1] >= self.stack.size()):
                raise ExecutionException("(engine) injectDataPre, try to "
                                         "insert data in the future")

            # need to compute first index
            new_cmd_path = cmd_path[:]
            new_cmd_path[-1] = 0

            self.stack.insert(item_candidate_list[0][1],
                              ([data],
                              new_cmd_path,
                              PREPROCESS_INSTRUCTION,
                              enabling_map,))
        else:
            # try to find an equal map
            for item, index in item_candidate_list:
                if not equalMap(enabling_map, item[3]):
                    continue

                # append
                item[0].append(data)
                return

            # no equal map found
            if only_append:
                raise ExecutionException("(engine) injectDataPre, no "
                                         "corresponding item found on the "
                                         "stack")

            # need to compute first index
            new_cmd_path = cmd_path[:]
            new_cmd_path[-1] = 0

            if if_no_match_execute_sooner_as_possible:
                if (self._isInProcess and
                   item_candidate_list[0][1]+1 >= self.stack.size()):
                    raise ExecutionException("(engine) injectDataPre, try to "
                                             "insert data in the future")

                self.stack.insert(item_candidate_list[0][1]+1,
                                  ([data],
                                   new_cmd_path,
                                   PREPROCESS_INSTRUCTION,
                                   enabling_map,))
            else:
                self.stack.insert(item_candidate_list[-1][1],
                                  ([data],
                                   new_cmd_path,
                                   PREPROCESS_INSTRUCTION,
                                   enabling_map,))

    def insertDataToPreProcess(self, data, only_for_the_linked_sub_cmd=True):
        self.stack.raiseIfEmpty("insertDataToPreProcess")

        # the current process must be pro or pos
        if self.stack.typeOnTop() == PREPROCESS_INSTRUCTION:
            self.appendData(data)
            return

        # computer map
        enabling_map = None
        if only_for_the_linked_sub_cmd:
            cmd_length_on_top = self.stack.subCmdLengthOnTop(self.cmd_list)
            enabling_map = [False] * cmd_length_on_top
            enabling_map[self.stack.subCmdIndexOnTop()] = True

        # inject data
        self.injectDataPre(data,
                           self.stack.pathOnTop(),
                           enabling_map,
                           False,
                           True)

    def insertDataToProcess(self, data):
        self.stack.raiseIfEmpty("insertDataToProcess")

        # the current process must be post
        if self.stack.typeOnTop() != POSTPROCESS_INSTRUCTION:
            raise ExecutionException("(engine) insertDataToProcess, only a "
                                     "process in postprocess state can execute"
                                     " this function")

        # the current process must be on a root path

        # TODO FIXME, this is strange, in the error message we talk about root
        # command but we check process command
        if not self.isCurrentProcessCommand():
            raise ExecutionException("(engine) insertDataToProcess, only the "
                                     "root command can insert data to the "
                                     "process")

        # inject data
        self.injectDataPro(data,
                           self.stack.pathOnTop(),
                           self.stack.pathOnTop())

    def insertDataToNextSubCommandPreProcess(self, data):
        self.stack.raiseIfEmpty("insertDataToNextSubCommandPreProcess")

        # is there a next pre process sub command ?
        cmd_length_on_top = self.stack.subCmdLengthOnTop(self.cmd_list)-1
        if self.stack.subCmdIndexOnTop() == cmd_length_on_top:
            raise ExecutionException("(engine) "
                                     "insertDataToNextSubCommandPreProcess, "
                                     "there is no next pre process available "
                                     "to insert new data")

        cmd_path = self.stack.pathOnTop()[:]
        cmd_path[-1] += 1

        # create enabling map
        enabling_map = [False] * self.stack.subCmdLengthOnTop(self.cmd_list)
        enabling_map[cmd_path[-1]] = True

        # inject in asLateAsPossible
        self.injectDataPre(data, cmd_path, enabling_map, False, False)

# ##  COMMAND meth # ##

    def _willThisCmdBeCompletlyDisabled(self,
                                        cmd_id,
                                        start_skip_range,
                                        range_length=1):
        for i in range(0, min(start_skip_range, len(self.cmd_list[cmd_id]))):
            if not self.cmd_list[cmd_id].isdisabledCmd(i):
                return False

        for i in range(start_skip_range+range_length,
                       len(self.cmd_list[cmd_id])):
            if not self.cmd_list[cmd_id].isdisabledCmd(i):
                return False

        return True

    def _willThisDataBunchBeCompletlyDisabled(self,
                                              data_index,
                                              start_skip_range,
                                              range_length=1):
        emap = self.stack.enablingMapOnIndex(data_index)
        cmd_id = self.stack.cmdIndexOnIndex(data_index)

        for j in range(0, min(start_skip_range, len(self.cmd_list[cmd_id]))):
            if (not self.cmd_list[cmd_id].isdisabledCmd(j) and
               (emap is None or emap[j])):
                return False

        for j in range(start_skip_range+range_length,
                       len(self.cmd_list[cmd_id])):
            if (not self.cmd_list[cmd_id].isdisabledCmd(j) and
               (emap is None or emap[j])):
                return False

        return True

    def _willThisDataBunchBeCompletlyEnabled(self,
                                             data_index,
                                             start_skip_range,
                                             range_length=1):
        emap = self.stack.enablingMapOnIndex(data_index)
        if emap is None:
            return True

        cmd_id = self.stack.cmdIndexOnIndex(data_index)

        for j in range(0, min(start_skip_range, len(emap))):
            if not emap[j]:
                return False

        for j in range(start_skip_range+range_length,
                       len(self.cmd_list[cmd_id])):
            if not emap[j]:
                return False

        return True

    def _skipOnCmd(self,
                   cmd_id,
                   sub_cmd_id,
                   skip_count=1,
                   allow_to_disable_data_bunch=False):
        if skip_count < 1:
            raise ExecutionException("(engine) _skipOnCmd, skip count must be "
                                     "equal or bigger than 1")

        isAValidIndex(self.cmd_list, cmd_id, "_skipOnCmd", "command list")
        isAValidIndex(self.cmd_list[cmd_id],
                      sub_cmd_id,
                      "_skipOnCmd",
                      "sub command list")

        # is the cmd will be compltly disabled with this skip range?
        if self._willThisCmdBeCompletlyDisabled(cmd_id,
                                                sub_cmd_id,
                                                skip_count):
            raise ExecutionException("(engine) _skipOnCmd, the skip range will"
                                     " completly disable the cmd")

        # make a list of the path involved in the disabling
        cmd_to_update = []

        for i in range(0, len(self.cmd_list)):
            if self.cmd_list[i] == self.cmd_list[cmd_id]:
                cmd_to_update.append(i)

        # explore the stack looking after these paths
        for i in range(0, self.stack.size()):
            if self.stack.typeOnIndex(i) != PREPROCESS_INSTRUCTION:
                break

            if self.stack.cmdIndexOnIndex(i) not in cmd_to_update:
                continue

            if (not allow_to_disable_data_bunch and
               self._willThisDataBunchBeCompletlyDisabled(i,
                                                          sub_cmd_id,
                                                          skip_count)):
                raise ExecutionException("(engine) _skipOnCmd, the skip range"
                                         " will completly disable a databunch "
                                         "on the stack")

        # no prblm found, the disabling can occur
        how_many_to_skip = min(len(self.cmd_list[cmd_id]),
                               sub_cmd_id+skip_count)
        for i in range(sub_cmd_id, how_many_to_skip):
            self.cmd_list[cmd_id].disableCmd(i)

    def _enableOnCmd(self, cmd_id, sub_cmd_id, enable_count=1):
        if enable_count < 1:
            raise ExecutionException("(engine) _enableOnCmd, enable count must"
                                     " be equal or bigger than 1")

        isAValidIndex(self.cmd_list, cmd_id, "_enableOnCmd", "command list")
        isAValidIndex(self.cmd_list[cmd_id],
                      sub_cmd_id,
                      "_enableOnCmd",
                      "sub command list")

        # no prblm found, the disabling can occur
        how_many_to_enable = min(len(self.cmd_list[cmd_id]),
                                 sub_cmd_id+enable_count)
        for i in range(sub_cmd_id, how_many_to_enable):
            self.cmd_list[cmd_id].enableCmd(i)

    def _skipOnDataBunch(self, data_bunch_index, sub_cmd_id, skip_count=1):
        if skip_count < 1:
            raise ExecutionException("(engine) _skipOnDataBunch, skip count "
                                     "must be equal or bigger than 1")

        self.stack.raiseIfEmpty("_skipOnDataBunch")

        # check valid index
        isAValidIndex(self.stack,
                      data_bunch_index,
                      "_skipOnDataBunch",
                      "stack")
        isAValidIndex(self.stack.getCmd(data_bunch_index, self.cmd_list),
                      sub_cmd_id,
                      "_skipOnDataBunch",
                      "sub command list")

        #  can only skip the next command if the state is pre_process
        if self.stack.typeOnIndex(data_bunch_index) != PREPROCESS_INSTRUCTION:
            raise ExecutionException("(engine) _skipOnDataBunch, can only skip"
                                     " method on PREPROCESS item")

        # if still not found, raise
        if self._willThisDataBunchBeCompletlyDisabled(data_bunch_index,
                                                      sub_cmd_id,
                                                      skip_count):
            raise ExecutionException("(engine) _skipOnDataBunch, every sub cmd"
                                     " in this databunch will be disabled with"
                                     " this skip range")

        enabling_map = self.stack.enablingMapOnIndex(data_bunch_index)

        if enabling_map is None:
            cmd_length = self.stack.subCmdLengthOnIndex(data_bunch_index,
                                                        self.cmd_list)
            enabling_map = [True] * cmd_length

        for i in range(sub_cmd_id,
                       min(sub_cmd_id+skip_count, len(enabling_map))):
            if not enabling_map[i]:
                continue

            enabling_map[i] = False

        self.stack.setEnableMapOnIndex(data_bunch_index, enabling_map)

    def _enableOnDataBunch(self, data_bunch_index, sub_cmd_id, enable_count=1):
        if enable_count < 1:
            raise ExecutionException("(engine) _skipOnDataBunch, skip count "
                                     "must be equal or bigger than 1")

        self.stack.raiseIfEmpty("_skipOnDataBunch")

        # check valid index
        isAValidIndex(self.stack,
                      data_bunch_index,
                      "_skipOnDataBunch",
                      "stack")
        isAValidIndex(self.stack.getCmd(data_bunch_index, self.cmd_list),
                      sub_cmd_id,
                      "_skipOnDataBunch",
                      "sub command list")

        #  can only skip the next command if the state is pre_process
        if self.stack.typeOnIndex(data_bunch_index) != PREPROCESS_INSTRUCTION:
            raise ExecutionException("(engine) _skipOnDataBunch, can only "
                                     "skip method on PREPROCESS item")

        if self._willThisDataBunchBeCompletlyEnabled(data_bunch_index,
                                                     sub_cmd_id,
                                                     enable_count):
            enabling_map = None
        else:
            enabling_map = self.stack.enablingMapOnIndex(data_bunch_index)

            enable_until = min(sub_cmd_id+enable_count, len(enabling_map))
            for i in range(sub_cmd_id, enable_until):
                if enabling_map[i]:
                    continue

                enabling_map[i] = True

        self.stack.setEnableMapOnIndex(data_bunch_index, enabling_map)

    def skipNextSubCommandOnTheCurrentData(self, skip_count=1):
        if skip_count < 1:
            raise ExecutionException("(engine) "
                                     "skipNextSubCommandOnTheCurrentData, skip"
                                     " count must be equal or bigger than 1")

        self.stack.raiseIfEmpty("skipNextSubCommandOnTheCurrentData")
        #  can only skip the next command if the state is pre_process
        if self.stack.typeOnTop() != PREPROCESS_INSTRUCTION:
            raise ExecutionException("(engine) "
                                     "skipNextSubCommandOnTheCurrentData, can"
                                     " only skip method on PREPROCESS item")

        if self._isInProcess:
            if self.topPreIndexOpp is None or self.topPreIndexOpp >= 0:
                self.topPreIndexOpp += skip_count
            else:
                raise ExecutionException("(engine) "
                                         "skipNextSubCommandOnTheCurrentData, "
                                         "a pending operation is already "
                                         "present on this databunch, can not "
                                         "skip the next sub command")
        else:
            self.stack[-1][1][-1] += skip_count

    def skipNextSubCommandForTheEntireDataBunch(self, skip_count=1):
        self.stack.raiseIfEmpty("skipNextSubCommandForTheEntireDataBunch")
        self._skipOnDataBunch(-1, self.stack.subCmdIndexOnTop()+1, skip_count)

    def skipNextSubCommandForTheEntireExecution(self, skip_count=1):
        self.stack.raiseIfEmpty("skipNextSubCommandForTheEntireExecution")
        self._skipOnCmd(self.stack.cmdIndexOnTop(),
                        self.stack.subCmdIndexOnTop(),
                        skip_count)

    def disableEnablingMapOnDataBunch(self, index=-1):
        isAValidIndex(self.stack,
                      index,
                      "disableEnablingMapOnDataBunch",
                      "stack")

        #  can only skip the next command if the state is pre_process
        if self.stack.typeOnIndex(index) != PREPROCESS_INSTRUCTION:
            raise ExecutionException("(engine) disableEnablingMapOnDataBunch, "
                                     "can only skip method on PREPROCESS item")

        mapping = self.stack.enablingMapOnIndex(index)

        if mapping is not None:
            self.stack.setEnableMapOnIndex(index, None)

    def enableSubCommandInCurrentDataBunchMap(self, index_sub_cmd):
        self._enableOnDataBunch(-1, index_sub_cmd, 1)

    def enableSubCommandInCommandMap(self, index_cmd, index_sub_cmd):
        self._enableOnCmd(index_cmd, index_sub_cmd, 1)

    def disableSubCommandInCurrentDataBunchMap(self, index_sub_cmd):
        self._skipOnDataBunch(-1, index_sub_cmd, 1)

    def disableSubCommandInCommandMap(self, index_cmd, index_sub_cmd):
        self._skipOnCmd(index_cmd, index_sub_cmd, 1)

    def flushArgs(self, index=None):  # None index means current command
        if index is None:
            self.stack.raiseIfEmpty("flushArgs")
            cmd_id = self.stack.cmdIndexOnTop()
        else:
            cmd_id = index

        isAValidIndex(self.args_list, cmd_id, "flushArgs", "arg list")
        self.args_list[cmd_id] = None
        self.mapped_args_list[cmd_id] = (EMPTY_MAPPED_ARGS,
                                         EMPTY_MAPPED_ARGS,
                                         EMPTY_MAPPED_ARGS,)

    def addSubCommand(self,
                      cmd,
                      cmd_id=None,
                      only_add_once=True,
                      use_args=True):
        # is a valid cmd ?
        # only the Command are allowed in the list
        if not isinstance(cmd, Command):
            raise ExecutionException("(engine) addSubCommand, cmd is not a "
                                     "Command instance, got '"+str(type(cmd)) +
                                     "'")

        # compute the current command index where the sub command will be
        # insert, check the cmd path on the stack
        if cmd_id is None:
            self.stack.raiseIfEmpty("addSubCommand")
            cmd_id = self.stack.cmdIndexOnTop()

        isAValidIndex(self.cmd_list, cmd_id, "addSubCommand", "command list")

        # add the sub command
        self.cmd_list[cmd_id].addDynamicCommand(cmd, only_add_once, use_args)

        # build a list with the index in cmd_list with the equivalent cmd as
        # the cmd at cmd_id
        cmd_to_update = []
        for i in range(0, len(self.cmd_list)):
            if self.cmd_list[i] == self.cmd_list[cmd_id]:
                cmd_to_update.append(i)

        for i in range(0, self.stack.size()):
            if self.stack.typeOnIndex(i) != PREPROCESS_INSTRUCTION:
                break

            # is it a wrong path ?
            if self.stack.cmdIndexOnIndex(i) not in cmd_to_update:
                continue

            # is there an enabled mapping ?
            enabling_map = self.stack.enablingMapOnIndex(i)
            if enabling_map is None:
                continue

            enabling_map.append(True)

    def addCommand(self, cmd, convert_process_to_pre_process=False):
        # only the MultiCommand are allowed in the list
        if not isinstance(cmd, MultiCommand):
            raise ExecutionException("(engine) addCommand, cmd is not a "
                                     "MultiCommand instance, got '" +
                                     str(type(cmd))+"'")

        # The process (!= pre and != post), must always be the process
        # of the last command in the list
        # if we add a new command, the existing process on the stack
        # became invalid
        stack_size = self.stack.size()
        for i in range(0, len(self.stack)):
            # if we reach a preprocess, we never reach again a process
            if self.stack.typeOnIndex(i) == PREPROCESS_INSTRUCTION:
                continue

            if self.stack.typeOnIndex(i) == POSTPROCESS_INSTRUCTION:
                break

            # so, here we only have PROCESS_INSTRUCTION

            # if it is the process at the top, it must have its current data
            # and the next
            #   the current data of a top process is currently consumed by a
            #   process, so on the next iteration it will not be a problem
            #   anymore.  But if a next data exist, it is a problem.
            if i == stack_size-1 and len(self.stack.dataOnTop()) == 1:
                continue

            if not convert_process_to_pre_process:
                raise ExecutionException("(engine) addCommand, some process "
                                         "are waiting on the stack, can not "
                                         "add a command")

            # convert the existing process on the stack into preprocess of
            # the new command
            if self._isInProcess and i == (self.stack.size()-1):
                self.topProcessToPre = True
            else:
                new_path = self.stack.pathOnIndex(i)[:]
                # no need to compute the index, the cmd will be reset,
                # so the first available sub cmd will be at the index 0
                new_path.append(0)
                self.stack.setPathOnIndex(i, new_path)

            self.stack.setTypeOnIndex(i, PREPROCESS_INSTRUCTION)

        cmd.reset()
        self.cmd_list.append(cmd)

    def isCurrentRootCommand(self):
        self.stack.raiseIfEmpty("isCurrentRootCommand")
        return self.stack.cmdIndexOnTop() == 0

    def isCurrentProcessCommand(self):
        self.stack.raiseIfEmpty("isCurrentProcessCommand")
        return self.stack.cmdIndexOnTop() == len(self.cmd_list)-1

    def getCurrentCommand(self):
        self.stack.raiseIfEmpty("getCurrentCommand")
        return self.cmd_list[self.stack.cmdIndexOnTop()]

    def hasPreviousCommand(self):
        self.stack.raiseIfEmpty("hasPreviousCommand")
        return self.stack.cmdIndexOnTop() > 0

    def getPreviousCommand(self):
        self.stack.raiseIfEmpty("getPreviousCommand")
        if self.stack.cmdIndexOnTop() == 0:
            raise ExecutionException("(engine) getPreviousCommand, there is no"
                                     " previous command")

        return self.cmd_list[self.stack.cmdIndexOnTop()-1]

# ##  SPLIT/MERGE meth # ##

    def mergeDataAndSetEnablingMap(self,
                                   toppest_item_to_merge=-1,
                                   new_map=None,
                                   count=2):
        self.stack.raiseIfEmpty("mergeDataAndSetEnablingMap")
        isAValidIndex(self.stack,
                      toppest_item_to_merge,
                      "mergeDataAndSetEnablingMap",
                      "stack")
        raisIfInvalidMap(new_map,
                         self.stack.subCmdLengthOnIndex(toppest_item_to_merge,
                                                        self.cmd_list),
                         "mergeDataAndSetEnablingMap")

        # current index must be enabled in map
        if new_map is not None:
            subindex = self.stack.subCmdIndexOnIndex(toppest_item_to_merge)
            if not new_map[subindex]:
                raise ExecutionException("(engine) mergeDataAndSetEnablingMap,"
                                         " the current sub command is disabled"
                                         " in the new map")

        # convert toppest_item_to_merge into positive value
        if toppest_item_to_merge < 0:
            toppest_item_to_merge = len(self.stack) + toppest_item_to_merge

        # merge items on stack
        self.mergeData(toppest_item_to_merge, count, None)

        # set the new map
        self.stack.setEnableMapOnIndex(toppest_item_to_merge-count+1, new_map)

    def mergeData(self,
                  toppest_item_to_merge=-1,
                  count=2,
                  index_of_the_map_to_keep=None):
        # need at least two item to merge
        if count < 2:
            return False  # no need to merge

        # check and manage index
        isAValidIndex(self.stack, toppest_item_to_merge, "mergeData", "stack")
        if toppest_item_to_merge < 0:
            toppest_item_to_merge = len(self.stack) + toppest_item_to_merge

        # the stack need to hold at least count
        if toppest_item_to_merge+1 < count:
            raise ExecutionException("(engine) mergeDataOnStack, no enough of "
                                     "data on stack to merge from this index")

        # can only merge on PREPROCESS
        if (self.stack.typeOnIndex(toppest_item_to_merge) !=
           PREPROCESS_INSTRUCTION):
            raise ExecutionException("(engine) mergeDataOnStack, try to merge "
                                     "a not preprocess action")

        # check dept and get map
        if index_of_the_map_to_keep is not None:
            if (index_of_the_map_to_keep < 0 or
               index_of_the_map_to_keep > toppest_item_to_merge):
                raise ExecutionException("(engine) mergeDataOnStack, the "
                                         "selected map to apply is not one the"
                                         " map of the selected items")

            # get the valid map
            enabling_map = self.stack.enablingMapOnIndex(
                index_of_the_map_to_keep)

            if enabling_map is not None:
                # the current index must be enabled in the new map
                subindex = self.stack.subCmdIndexOnIndex(toppest_item_to_merge)
                if not enabling_map[subindex]:
                    raise ExecutionException("(engine) "
                                             "mergeDataAndSetEnablingMap, the "
                                             "current sub command is disabled "
                                             "in the selected map")

        else:
            # does not keep any map
            enabling_map = None

        # extract information from first item
        path = self.stack.pathOnIndex(toppest_item_to_merge)

        for i in range(1, count):
            current_stack_item = self.stack.itemOnIndex(
                toppest_item_to_merge-i)
            equals, same_length, equals_count, path1_is_higher = \
                equalPath(path, current_stack_item[1])

            # the path must be the same for each item to merge
            #   execpt for the last command, the items not at the top of the
            #   stack must have 0 or the cmdStartLimit
            if not same_length:
                raise ExecutionException("(engine) mergeDataOnStack, the "
                                         "command path is different for the "
                                         "item at index <"+str(i)+">")

            if not equals:
                raise ExecutionException("(engine) mergeDataOnStack, a "
                                         "subcommand index is different for "
                                         "the item at sub index <" +
                                         str(equals_count)+">")

            # the action must be the same type
            if current_stack_item[2] != PREPROCESS_INSTRUCTION:
                raise ExecutionException("(engine) mergeDataOnStack, the "
                                         "action of the item at index <" +
                                         str(i)+"> is different of the action"
                                         " ot the first item")

        # merge data and keep start/end command
        data_bunch = []
        for i in range(0, count):
            data_bunch.extend(self.stack.dataOnIndex(toppest_item_to_merge-i))
            del self.stack[toppest_item_to_merge - i]

        self.stack.insert(toppest_item_to_merge-count+1,
                          (data_bunch,
                           path,
                           PREPROCESS_INSTRUCTION,
                           enabling_map,))
        return True

    def splitDataAndSetEnablingMap(self,
                                   item_to_split=-1,
                                   split_at_data_index=0,
                                   map1=None,
                                   map2=None):
        self.stack.raiseIfEmpty("splitDataAndSetEnablingMap")
        isAValidIndex(self.stack,
                      item_to_split,
                      "splitDataAndSetEnablingMap",
                      "stack")
        expected_map_length = self.stack.subCmdLengthOnIndex(item_to_split,
                                                             self.cmd_list)
        raisIfInvalidMap(map1,
                         expected_map_length,
                         "splitDataAndSetEnablingMap")
        raisIfInvalidMap(map2,
                         expected_map_length,
                         "splitDataAndSetEnablingMap")

        # get a positive index
        if item_to_split < 0:
            item_to_split = len(self.stack) + item_to_split

        # current index must be enabled in new map1 (really ?)
        if (map1 is not None and
           not map1[self.stack.subCmdIndexOnIndex(item_to_split)]):
            raise ExecutionException("(engine) mergeDataAndSetEnablingMap, the"
                                     " current sub command can not be disabled"
                                     " in the map1")

        # compute first available in map2
        new_map_to_index = 0

        # split
        state = self.splitData(item_to_split, split_at_data_index, True)

        # set new map
        if state:  # is a split occured ?
            self.stack.setEnableMapOnIndex(item_to_split, map2)
            self.stack.pathOnIndex(item_to_split)[-1] = new_map_to_index
            self.stack.setEnableMapOnIndex(item_to_split+1, map1)
        else:
            self.stack.setEnableMapOnIndex(item_to_split, map1)

        return state

    # split the data into two separate stack item at the index, but will not
    # change anything in the process order
    def splitData(self,
                  item_to_split=-1,
                  split_at_data_index=0,
                  reset_enabling_map=False):
        # is empty stack ?
        self.stack.raiseIfEmpty("splitData")
        isAValidIndex(self.stack, item_to_split, "splitData", "stack")

        # is it a pre ? (?)
        if self.stack.typeOnIndex(item_to_split) != PREPROCESS_INSTRUCTION:
            raise ExecutionException("(engine) splitData, can't split the "
                                     "data of a PRO/POST process because it "
                                     "will not change anything on the "
                                     "execution")

        # split point exist ?
        topdata = self.stack.dataOnIndex(item_to_split)
        isAValidIndex(topdata,
                      split_at_data_index,
                      "splitData",
                      "data to split")

        # has enought data to split ?
        if len(topdata) < 2 or split_at_data_index == 0:
            return False

        # recompute item_to_split if needed
        if item_to_split < 0:
            item_to_split = len(self.stack) + item_to_split

        # pop
        top = self.stack[item_to_split]
        del self.stack[item_to_split]

        path = top[1][:]
        if reset_enabling_map:
            enable_map = None
            path[-1] = 0
        else:
            enable_map = top[3]
            path[-1] = 0

        # push the two new items
        self.stack.insert(item_to_split, (top[0][0:split_at_data_index],
                                          top[1],
                                          top[2],
                                          enable_map,))
        self.stack.insert(item_to_split, (top[0][split_at_data_index:],
                                          path,
                                          top[2],
                                          enable_map,))

        return True

# ##  DATA meth (data of the top item on the stack) # ##

    def flushData(self):
        self.stack.raiseIfEmpty("flushData")
        # remove everything, the engine is able to manage an empty data bunch
        del self.stack.dataOnTop()[:]

    def appendData(self, newdata):
        self.stack.raiseIfEmpty("addData")
        self.stack.dataOnTop().append(newdata)

    def addData(self, newdata, offset=-1, forbide_insertion_at_zero=True):
        self.stack.raiseIfEmpty("addData")
        data = self.stack.dataOnTop()

        if forbide_insertion_at_zero and offset == 0:
            raise ExecutionException("(engine) addData, can't insert a data at"
                                     " offset 0, it could create infinite "
                                     "loop. it is possible to override this "
                                     "check with the boolean "
                                     "forbide_insertion_at_zero, set it to "
                                     "False")

        data.insert(offset, newdata)

    def removeData(self, offset=0, reset_sub_cmd_index_if_offset_zero=True):
        self.stack.raiseIfEmpty("removeData")
        data = self.stack.dataOnTop()
        isAValidIndex(data, offset, "removeData", "data on top")

        # remove the data
        del data[offset]

        # set the current cmd index to startIndex -1 (the minus 1 is because
        # the engine will make a plus 1 to execute the next command)
        #
        # len(data) == 0 is to manage the removal of the last item with -1
        # index on a data bunch of size 1
        if (reset_sub_cmd_index_if_offset_zero and
           (offset == 0 or len(data) == 0)):
            # the engine will compute the first enabled cmd, if there is no
            # more data, let the engine compute the cmd index too
            if self._isInProcess:
                if self.topPreIndexOpp is None or self.topPreIndexOpp == -1:
                    self.topPreIndexOpp = -1
                else:
                    raise ExecutionException("(engine) removeData, a pending "
                                             "operation is already present on "
                                             "this databunch, can not remove "
                                             "the data at zero index")
            else:
                self.stack[-1][1][-1] = 0

    def setData(self, newdata, offset=0):
        self.stack.raiseIfEmpty("setData")
        data = self.stack.dataOnTop()
        isAValidIndex(data, offset, "removeData", "data on top")
        data[offset] = newdata

    def getData(self, offset=0):
        self.stack.raiseIfEmpty("getData")
        data = self.stack.dataOnTop()
        isAValidIndex(data, offset, "getData", "data on top")
        return data[offset]

    def hasNextData(self):
        self.stack.raiseIfEmpty("hasNextData")
        # 1 and not zero, because there are the current data and the next one
        return len(self.stack.dataOnTop()) > 1

    def getRemainingDataCount(self):
        self.stack.raiseIfEmpty("getRemainingDataCount")
        # -1 because we don't care about the current data
        return len(self.stack.dataOnTop())-1

    def getDataCount(self):
        self.stack.raiseIfEmpty("getDataCount")
        return len(self.stack.dataOnTop())

# ##  VARIOUS meth # ##

    def getEnv(self):
        return self.env

    def getLastResult(self):
        return self.lastResult

# ##  ENGINE core meth # ##

    def execute(self):
        self.raiseIfInMethodExecution("execute")

        # consume stack
        while self.stack.size() > 0:  # while there is some item into the stack
            cmd = self.stack.getCmdOnTop(self.cmd_list)
            sub_cmd_index = self.stack.subCmdIndexOnTop() % len(cmd)
            enabling_map = self.stack.enablingMapOnTop()
            data = self.stack.dataOnTop()

            # ##  COMPUTE THE FIRST AVAILABLE INDEX # ##
            sub_cmd_index %= len(cmd)
            before_current_index = (sub_cmd_index + len(cmd) - 1) % len(cmd)
            while len(data) > 0:
                if ((enabling_map is not None and
                   not enabling_map[sub_cmd_index]) or
                   cmd.isdisabledCmd(sub_cmd_index)):
                    # we test every cmd available in this databunch,
                    # they are all disabled
                    if sub_cmd_index == before_current_index:
                        data = ()
                        # will go to the else statement of the current loop
                        continue

                    sub_cmd_index += 1

                    # do we reach the end of the available index for this
                    # data ?
                    if sub_cmd_index >= len(cmd):
                        del data[0]
                        sub_cmd_index = 0

                    continue  # need to test the next index
                break  # we have an enabled index with at least one data

            # len(self.stack.dataOnTop()) == 0: # if empty data, this
            # databunch is out, no more thing to do
            else:
                self.stack.pop()
                continue

            # ##  EXTRACT DATA FROM STACK # ##
            top = self.stack.top()
            subcmd, use_args, enabled = cmd[sub_cmd_index]
            ins_type = self.stack.typeOnTop()
            top[1][-1] = sub_cmd_index  # set current index in databunch

            # ##  EXECUTE command # ##
            # prepare the var to push on the stack, if the var keep the
            # none value, nothing will be stacked
            to_stack = None

            if use_args:
                index_on_top = self.stack.cmdIndexOnTop()
                args = self.args_list[index_on_top]
                mapped_args = self.mapped_args_list[index_on_top]
            else:
                args = None
                mapped_args = EMPTY_MAPPED_ARGS

            # #  PRE PROCESS
            if ins_type == PREPROCESS_INSTRUCTION:  # pre
                r = self._executeMethod(cmd,
                                        subcmd.preProcess,
                                        top,
                                        args,
                                        mapped_args[0])
                subcmd.pre_count += 1

                new_path = top[1][:]  # copy the path
                if self.topPreIndexOpp is not None:
                    if self.topPreIndexOpp < 0:
                        # little hack to get the index 0 on the current data
                        # on the next execution
                        top[1][-1] = len(cmd) - 1
                        top[0].insert(0, None)
                    else:
                        top[1][-1] += self.topPreIndexOpp

                    self.topPreIndexOpp = None

                # manage result
                # no child, next step will be a process
                if len(top[1]) == len(self.cmd_list):
                    to_stack = (r, new_path, PROCESS_INSTRUCTION, )
                else:
                    # there are some child, next step will be another
                    # preprocess
                    # build first index to execute, it's not always 0
                    # new_cmd = self.cmd_list[len(top[1])]  # the -1 is not
                    # missing, we want the next cmd, not the current
                    # next_data, new_index =
                    # self._computeTheNextChildToExecute(new_cmd,
                    # len(new_cmd)-1, None)

                    # the first cmd has no subcmd enabled, impossible to
                    # start the engine
                    # if new_index == -1:
                    #     raise ExecutionException("(engine) execute, no
                    #       enabled subcmd on the cmd "+str(len(top[1])))

                    # then add the first index of the next command
                    new_path.append(0)
                    to_stack = (r, new_path, PREPROCESS_INSTRUCTION, )

            # #  PROCESS # #
            elif ins_type == PROCESS_INSTRUCTION:  # pro
                r = self._executeMethod(cmd,
                                        subcmd.process,
                                        top,
                                        None,
                                        mapped_args[1])
                subcmd.pro_count += 1
                # manage result
                to_stack = (r, top[1][:], POSTPROCESS_INSTRUCTION,)

                if self.topProcessToPre:
                    self.topProcessToPre = False
                    top[1].append(0)

            # #  POST PROCESS # #
            elif ins_type == POSTPROCESS_INSTRUCTION:  # post
                r = self._executeMethod(cmd,
                                        subcmd.postProcess,
                                        top,
                                        None,
                                        mapped_args[2])
                subcmd.post_count += 1

                # manage result
                if len(top[1]) > 1:  # not on the root node
                    # just remove one item in the path to get the next
                    # postprocess to execute
                    to_stack = (r, top[1][:-1], POSTPROCESS_INSTRUCTION,)
                # so this is the last post for this data
                else:
                    # and there is no more data to process
                    if self.stack.size() == 1:
                        if isinstance(r, MultiOutput):
                            self.lastResult = r
                        else:
                            if len(r) > 0 and r[0] is EMPTY_DATA_TOKEN:
                                self.lastResult = ()
                            else:
                                self.lastResult = r
            else:
                raise ExecutionException("(engine) execute, unknwon process "
                                         "command '"+str(ins_type)+"'")

            if self.selfkillreason is not None:
                reason, abnormal = self.selfkillreason
                raise EngineInterruptionException("(engine) stopExecution, "
                                                  "execution stop, reason: " +
                                                  reason,
                                                  abnormal)

            if subcmd.pre_count > DEFAULT_EXECUTION_LIMIT:
                raise ExecutionException("(engine) execute, this subcommand "
                                         "reach the execution limit count for "
                                         "preprocess")
            elif subcmd.pro_count > DEFAULT_EXECUTION_LIMIT:
                raise ExecutionException("(engine) execute, this subcommand "
                                         "reach the execution limit count for "
                                         "process")
            elif subcmd.post_count > DEFAULT_EXECUTION_LIMIT:
                raise ExecutionException("(engine) execute, this subcommand "
                                         "reach the execution limit count for "
                                         "postprocess")

            # ##  MANAGE STACK, need to repush the current item ? # ##
            self.stack.pop()

            # process or postprocess ?
            if (ins_type == PROCESS_INSTRUCTION or
               ins_type == POSTPROCESS_INSTRUCTION):
                if len(top[0]) > 1:  # still data to execute ?
                    # remove the last used data and push on the stack
                    self.stack.push(top[0][1:], top[1], top[2])
            # ins_type == 0 # preprocess, can't be anything else, a test has
            # already occured sooner in the engine function
            else:
                next_data, new_index = \
                    self._computeTheNextChildToExecute(cmd, top[1][-1], top[3])
                # something to do ? (if new_index == -1, there is no
                # more enabled cmd for this data bunch)
                if (((not next_data and len(top[0]) > 0) or
                    len(top[0]) > 1) and
                   new_index >= 0):
                    # if we need to use the next data,
                    # we need to remove the old one
                    if next_data:
                        del top[0][0]  # remove the used data

                    # select the next child id
                    top[1][-1] = new_index

                    # push on the stack again
                    self.stack.push(top[0], top[1], top[2], top[3])

            # ##  STACK THE RESULT of the current process if needed # ##
            if to_stack is not None:
                self.stack.push(*to_stack)

    def _computeTheNextChildToExecute(self,
                                      cmd,
                                      current_sub_cmd_index,
                                      enabling_map):
        current_sub_cmd_index = min(current_sub_cmd_index, len(cmd) - 1)
        starting_index = current_sub_cmd_index
        execute_on_next_data = False
        while True:
            # increment
            starting_index = (starting_index+1) % len(cmd)

            # did it reach the next data ?
            if starting_index == 0:
                execute_on_next_data = True

            # is it a valid command to execute ?
            if (cmd[starting_index][2] and
               (enabling_map is None or enabling_map[starting_index])):
                return execute_on_next_data, starting_index

            # stop condition
            if starting_index == current_sub_cmd_index:
                return execute_on_next_data, -1

    def _executeMethod(self,
                       cmd,
                       subcmd,
                       stack_state,
                       args=None,
                       mapped_args=EMPTY_MAPPED_ARGS):
        next_data = stack_state[0][0]

        # prepare data
        if args is not None:
            args = args[:]
            if next_data != EMPTY_DATA_TOKEN:
                # case where the previous process return a list of element
                if hasattr(next_data, "__iter__"):
                    args.extend(next_data)
                else:  # case where the previous process return only one args
                    args.append(next_data)

        elif next_data != EMPTY_DATA_TOKEN:
            args = next_data
        else:
            args = ()

        # execute checker
        if hasattr(subcmd, "checker"):
            # TODO use mapped_args in checker

            data = subcmd.checker.checkArgs(args, mapped_args, self)

            # find lockable object
            lockable_list = []
            for k, v in data.items():
                if not isinstance(v, EnvironmentParameter):
                    continue

                if not v.isLockEnable():
                    continue

                lockable_list.append(v)

            lock = ParametersLocker(lockable_list)

        else:
            data = {}
            lock = FAKELOCK

        # execute Xprocess (X for pre/pro/post)
        with lock:
            self._isInProcess = True
            try:
                r = subcmd(**data)
            finally:
                self._isInProcess = False

        # manage None output
        if r is None:
            if (hasattr(subcmd, "allowToReturnNone") and
               subcmd.allowToReturnNone):
                return [[None]]
            else:
                return [EMPTY_DATA_TOKEN]

        # r must be a multi output
        if isinstance(r, MultiOutput):
            return r

        return [r]

    def stopExecution(self,
                      reason=None,
                      after_this_process=True,
                      abnormal=False):
        if not self._isInProcess:
            raise ExecutionException("(engine) stopExecution, can not "
                                     "execute this method outside of a "
                                     "process")

        if reason is None:
            reason = "unknown"

        if not after_this_process:
            raise EngineInterruptionException("(engine) stopExecution, "
                                              "execution stop, reason: " +
                                              reason,
                                              abnormal)
        else:
            self.selfkillreason = (reason, abnormal,)

    def raiseIfInMethodExecution(self, meth_name=None):
        if meth_name is None:
            meth_name = ""
        else:
            meth_name += ", "

        if self._isInProcess:
            raise ExecutionException("(engine) "+meth_name+", not allowed to "
                                     "execute this method inside a process")

    def raiseIfNotInMethodExecution(self, meth_name=None):
        if meth_name is None:
            meth_name = ""
        else:
            meth_name += ", "

        if not self._isInProcess:
            raise ExecutionException("(engine) "+meth_name+", not allowed to "
                                     "execute this method outside a process")

# ##  DEBUG meth # ##

    def getExecutionSnapshot(self):
        info = {}

        if self.stack.isEmpty():
            info["cmdIndex"] = -1
            info["cmd"] = None
            info["subCmdIndex"] = -1
            info["subCmd"] = None
            info["data"] = None
            info["process_type"] = -1
        else:
            top = self.stack.top()

            # the index of the current command in execution
            info["cmdIndex"] = self.stack.cmdIndexOnTop()

            # the object instance of the current command in execution
            info["cmd"] = self.stack.getCmdOnTop(self.cmd_list)

            # the index of the current sub command in execution
            info["subCmdIndex"] = self.stack.subCmdIndexOnTop()

            # the object instance of the current sub command in execution
            info["subCmd"] = self.cmd_list[len(top[1])-1][top[1][-1]]

            # the data of the current execution
            info["data"] = self.stack.dataOnTop()

            # the process type of the current execution
            info["process_type"] = self.stack.typeOnTop()

        return info

    def printStack(self):
        if self.stack.size() == 0:
            print("empty stack")  # noqa

        for i in range(self.stack.size()-1, -1, -1):
            cmd_enabled = self.stack[i][3]
            if cmd_enabled is None:
                cmd_enabled = "(no mapping)"

            print("# ["+str(i)+"] data="+str(self.stack[i][0])+", path=" +  # noqa
                  str(self.stack[i][1])+", action="+str(self.stack[i][2]) +
                  ", cmd enabled="+str(cmd_enabled))

    def printCmdList(self):
        if len(self.cmd_list) == 0:
            print("no command in the engine")  # noqa
            return

        for i in range(0, len(self.cmd_list)):
            print("Command <"+str(i)+">")  # noqa
            for j in range(0, len(self.cmd_list[i])):
                c, a, e = self.cmd_list[i][j]
                print("    SubCommand <"+str(j)+"> (use_args="+str(a) +  # noqa
                      ", enabled="+str(e)+")")

    def printCmdPath(self, path=None):
        if len(self.cmd_list) == 0:
            print("no command in the engine")  # noqa
            return

        if path is None:
            if self.stack.isEmpty():
                print("no item on the stack, and so no path available")  # noqa

            path = self.stack.pathOnTop()

        for i in range(0, len(path)):
            if i >= len(self.cmd_list):
                print("# ["+str(i)+"] out of bound index")  # noqa
                continue

            if path[i] < 0 or path[i] >= len(self.cmd_list[i]):
                print("# ["+str(i)+"] out of bound index in the command")  # noqa
                continue

            if len(self.cmd_list[i]) == 1:
                print("# ["+str(i)+"]")  # noqa
                continue

            print("# ["+str(i)+"]"+" (sub="+str(path[i])+")")  # noqa
