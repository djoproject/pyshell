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

from pyshell.command.command import MultiOutput, MultiCommand, Command
from pyshell.command.exception import executionInitException, \
                                      executionException, \
                                      engineInterruptionException
from pyshell.command.stackEngine import engineStack
from pyshell.command.utils import equalPath, isAValidIndex, topPath, \
                                  raisIfInvalidMap, equalMap, \
                                  raiseIfInvalidPath
from pyshell.system.container import ParameterContainer
from pyshell.system.environment import EnvironmentParameter, ParametersLocker
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


class _emptyDataToken(object):
    pass

EMPTY_DATA_TOKEN = _emptyDataToken()
EMPTY_MAPPED_ARGS = {}


class engineV3(object):
    # ##  INIT # ##
    def __init__(self, cmdList, argsList, mappedArgsList, env=None):
        # cmd must be a not empty list
        if cmdList is None or \
           not isinstance(cmdList, list) or \
           len(cmdList) == 0:
            raise executionInitException("(engine) init, command list is not "
                                         "a valid populated list")

        if argsList is None or \
           not isinstance(argsList, list) or \
           len(argsList) != len(cmdList):
            raise executionInitException("(engine) init, arg list is not a "
                                         "valid populated list of equal size "
                                         "with the command list")

        if mappedArgsList is None or \
           not isinstance(mappedArgsList, list) or \
           len(mappedArgsList) != len(cmdList):
            raise executionInitException("(engine) init, mapped arg list is "
                                         "not a valid populated list of equal "
                                         "size with the command list")

        # reset every commands
        for i in xrange(0, len(cmdList)):
            c = cmdList[i]

            if not isinstance(c, MultiCommand):
                raise executionInitException("(engine) init, item <"+str(i) +
                                             "> in the command list is not a "
                                             "MultiCommand instance, got '" +
                                             str(type(c))+"'")

            if len(c) == 0:  # empty multi command are not allowed
                raise executionInitException("(engine) init, a command is "
                                             "empty")

            if argsList[i] is not None and not isinstance(argsList[i], list):
                raise executionInitException("(engine) init, item <"+str(i) +
                                             "> in the arg list is different "
                                             "of None or List instance")

            # reset the information stored in the command from a previous
            # execution
            c.reset()

        self.argsList = argsList
        self.cmdList = cmdList  # list of MultiCommand
        self.mappedArgsList = mappedArgsList

        # check env variable
        if env is None:
            self.env = ParameterContainer()
        elif isinstance(env, ParameterContainer):
            self.env = env
        else:
            raise executionInitException("(engine) init, env must be an "
                                         "instance of ParameterContainer or "
                                         "None, got '"+str(type(env))+"'")

        self.stack = engineStack()
        self._isInProcess = False
        self.selfkillreason = None
        self.topPreIndexOpp = None
        self.topProcessToPre = False
        self.lastResult = None

        # init stack with a None data, on the subcmd 0 of the command 0,
        # with a preprocess action

        # init data to start the engine
        self.stack.push([EMPTY_DATA_TOKEN], [0], PREPROCESS_INSTRUCTION)

    def _getTheIndexWhereToStartTheSearch(self, processType):
        # check processType, must be pre/pro/post
        if processType != PREPROCESS_INSTRUCTION and \
           processType != PROCESS_INSTRUCTION and \
           processType != POSTPROCESS_INSTRUCTION:
            raise executionException("(engine) "
                                     "_getTheIndexWhereToStartTheSearch, "
                                     "unknown process type : " +
                                     str(processType))

        # check stack size
        stackLength = self.stack.size()

        # if stack is empty, the new data can be directly inserted
        if stackLength == 0:
            return 0

        # find the place to start the lookup
        if processType != POSTPROCESS_INSTRUCTION:
            for i in range(0, stackLength):
                if (self.stack.typeOnDepth(i) == POSTPROCESS_INSTRUCTION or
                    (self.stack.typeOnDepth(i) == PROCESS_INSTRUCTION and
                     processType == PREPROCESS_INSTRUCTION)):
                    continue

                # we reach the bottomest item of the wanted type
                return stackLength - i - 1

            # we don't find this type on the stack
            return -1

        # for POSTPROCESS_INSTRUCTION only, start on the top
        return stackLength - 1

    def _findIndexToInject(self, cmdPath, processType):
        # check command path
        raiseIfInvalidPath(cmdPath, self.cmdList, "_findIndexToInject")

        # if look up for a PROCESS, the path must always be a root path
        if (processType == PROCESS_INSTRUCTION and
           len(cmdPath) != len(self.cmdList)):
            raise executionException("(engine) _findIndexToInjectProOrPost, "
                                     "can only insert data to the process of "
                                     "the last command")

        # check first index to look (this will also check
        # if processType is valid)
        index = self._getTheIndexWhereToStartTheSearch(processType)
        to_ret = None

        while index >= 0 and processType == self.stack.typeOnIndex(index):
            equals, sameLength, equalsCount, path1IsHigher = \
                equalPath(self.stack[index][1], cmdPath)

            if equals:
                if processType != PREPROCESS_INSTRUCTION:
                    return self.stack[index], index
                else:
                    if to_ret is None:
                        to_ret = []

                    to_ret.append((self.stack[index], index,))

            elif (processType == PREPROCESS_INSTRUCTION and
                  sameLength and equalsCount == len(cmdPath)-1):
                if to_ret is None:
                    to_ret = []

                to_ret.append((self.stack[index], index,))

            # A lower path has been found on the stack, no way to find
            # a better path
            elif ((path1IsHigher is not None and path1IsHigher) or
                  len(self.stack[index][1]) < len(cmdPath)):
                break

            index -= 1

        # special case for PREPROCESS_INSTRUCTION, list of result
        if to_ret is not None:
            return to_ret

        if processType == PREPROCESS_INSTRUCTION:
            return ((None, index+1,),)
        else:
            return None, index+1

    def _injectDataProOrPos(self,
                            data,
                            cmdPath,
                            processType,
                            onlyAppend=False):
        obj, index = self._findIndexToInject(cmdPath, processType)

        if obj is None:
            # can only append ?
            if onlyAppend:
                raise executionException("(engine) injectDataProOrPos, there "
                                         "is no similar item on the stack and "
                                         "the system can only append, "
                                         "not create")

            if self._isInProcess and index >= self.stack.size():
                raise executionException("(engine) _injectDataProOrPos, try "
                                         "to insert data in the future")

            # insert a new object
            self.stack.insert(index, ([data], cmdPath[:], processType, None,))

        else:
            obj[0].append(data)

    def injectDataPro(self, data, cmdPath, processType, onlyAppend=False):
        self._injectDataProOrPos(data,
                                 cmdPath,
                                 PROCESS_INSTRUCTION,
                                 onlyAppend)

    def injectDataPost(self, data, cmdPath, processType, onlyAppend=False):
        self._injectDataProOrPos(data,
                                 cmdPath,
                                 POSTPROCESS_INSTRUCTION,
                                 onlyAppend)

    def injectDataPre(self,
                      data,
                      cmdPath,
                      enablingMap=None,
                      onlyAppend=False,
                      ifNoMatchExecuteSoonerAsPossible=True):
        itemCandidateList = self._findIndexToInject(cmdPath,
                                                    PREPROCESS_INSTRUCTION)

        # check map (is a list, valid length, only boolean value)
        raisIfInvalidMap(enablingMap,
                         len(self.cmdList[len(cmdPath)-1]),
                         "injectDataPre")

        # no match
        if len(itemCandidateList) == 1 and itemCandidateList[0][0] is None:
            if onlyAppend:
                raise executionException("(engine) injectDataPre, no "
                                         "corresponding item on the stack")

            if (self._isInProcess and
               itemCandidateList[0][1] >= self.stack.size()):
                raise executionException("(engine) injectDataPre, try to "
                                         "insert data in the future")

            # need to compute first index
            newCmdPath = cmdPath[:]
            newCmdPath[-1] = 0

            self.stack.insert(itemCandidateList[0][1],
                              ([data],
                              newCmdPath,
                              PREPROCESS_INSTRUCTION,
                              enablingMap,))
        else:
            # try to find an equal map
            for item, index in itemCandidateList:
                if not equalMap(enablingMap, item[3]):
                    continue

                # append
                item[0].append(data)
                return

            # no equal map found
            if onlyAppend:
                raise executionException("(engine) injectDataPre, no "
                                         "corresponding item found on the "
                                         "stack")

            # need to compute first index
            newCmdPath = cmdPath[:]
            newCmdPath[-1] = 0

            if ifNoMatchExecuteSoonerAsPossible:
                if (self._isInProcess and
                   itemCandidateList[0][1]+1 >= self.stack.size()):
                    raise executionException("(engine) injectDataPre, try to "
                                             "insert data in the future")

                self.stack.insert(itemCandidateList[0][1]+1,
                                  ([data],
                                   newCmdPath,
                                   PREPROCESS_INSTRUCTION,
                                   enablingMap,))
            else:
                self.stack.insert(itemCandidateList[-1][1],
                                  ([data],
                                   newCmdPath,
                                   PREPROCESS_INSTRUCTION,
                                   enablingMap,))

    def insertDataToPreProcess(self, data, onlyForTheLinkedSubCmd=True):
        self.stack.raiseIfEmpty("insertDataToPreProcess")

        # the current process must be pro or pos
        if self.stack.typeOnTop() == PREPROCESS_INSTRUCTION:
            self.appendData(data)
            return

        # computer map
        enablingMap = None
        if onlyForTheLinkedSubCmd:
            enablingMap = [False] * self.stack.subCmdLengthOnTop(self.cmdList)
            enablingMap[self.stack.subCmdIndexOnTop()] = True

        # inject data
        self.injectDataPre(data,
                           self.stack.pathOnTop(),
                           enablingMap,
                           False,
                           True)

    def insertDataToProcess(self, data):
        self.stack.raiseIfEmpty("insertDataToProcess")

        # the current process must be post
        if self.stack.typeOnTop() != POSTPROCESS_INSTRUCTION:
            raise executionException("(engine) insertDataToProcess, only a "
                                     "process in postprocess state can execute"
                                     " this function")

        # the current process must be on a root path

        # TODO FIXME, this is strange, in the error message we talk about root
        # command but we check process command
        if not self.isCurrentProcessCommand():
            raise executionException("(engine) insertDataToProcess, only the "
                                     "root command can insert data to the "
                                     "process")

        # inject data
        self.injectDataPro(data,
                           self.stack.pathOnTop(),
                           self.stack.pathOnTop())

    def insertDataToNextSubCommandPreProcess(self, data):
        self.stack.raiseIfEmpty("insertDataToNextSubCommandPreProcess")

        # is there a next pre process sub command ?
        cmdLengthOnTop = self.stack.subCmdLengthOnTop(self.cmdList)-1
        if self.stack.subCmdIndexOnTop() == cmdLengthOnTop:
            raise executionException("(engine) "
                                     "insertDataToNextSubCommandPreProcess, "
                                     "there is no next pre process available "
                                     "to insert new data")

        cmdPath = self.stack.pathOnTop()[:]
        cmdPath[-1] += 1

        # create enabling map
        enablingMap = [False] * self.stack.subCmdLengthOnTop(self.cmdList)
        enablingMap[cmdPath[-1]] = True

        # inject in asLateAsPossible
        self.injectDataPre(data, cmdPath, enablingMap, False, False)

# ##  COMMAND meth # ##

    def _willThisCmdBeCompletlyDisabled(self,
                                        cmdID,
                                        startSkipRange,
                                        rangeLength=1):
        for i in xrange(0, min(startSkipRange, len(self.cmdList[cmdID]))):
            if not self.cmdList[cmdID].isdisabledCmd(i):
                return False

        for i in xrange(startSkipRange+rangeLength, len(self.cmdList[cmdID])):
            if not self.cmdList[cmdID].isdisabledCmd(i):
                return False

        return True

    def _willThisDataBunchBeCompletlyDisabled(self,
                                              dataIndex,
                                              startSkipRange,
                                              rangeLength=1):
        emap = self.stack.enablingMapOnIndex(dataIndex)
        cmdID = self.stack.cmdIndexOnIndex(dataIndex)

        for j in xrange(0, min(startSkipRange, len(self.cmdList[cmdID]))):
            if (not self.cmdList[cmdID].isdisabledCmd(j) and
               (emap is None or emap[j])):
                return False

        for j in xrange(startSkipRange+rangeLength, len(self.cmdList[cmdID])):
            if (not self.cmdList[cmdID].isdisabledCmd(j) and
               (emap is None or emap[j])):
                return False

        return True

    def _willThisDataBunchBeCompletlyEnabled(self,
                                             dataIndex,
                                             startSkipRange,
                                             rangeLength=1):
        emap = self.stack.enablingMapOnIndex(dataIndex)
        if emap is None:
            return True

        cmdID = self.stack.cmdIndexOnIndex(dataIndex)

        for j in xrange(0, min(startSkipRange, len(emap))):
            if not emap[j]:
                return False

        for j in xrange(startSkipRange+rangeLength, len(self.cmdList[cmdID])):
            if not emap[j]:
                return False

        return True

    def _skipOnCmd(self,
                   cmdID,
                   subCmdID,
                   skipCount=1,
                   allowToDisableDataBunch=False):
        if skipCount < 1:
            raise executionException("(engine) _skipOnCmd, skip count must be "
                                     "equal or bigger than 1")

        isAValidIndex(self.cmdList, cmdID, "_skipOnCmd", "command list")
        isAValidIndex(self.cmdList[cmdID],
                      subCmdID,
                      "_skipOnCmd",
                      "sub command list")

        # is the cmd will be compltly disabled with this skip range?
        if self._willThisCmdBeCompletlyDisabled(cmdID, subCmdID, skipCount):
            raise executionException("(engine) _skipOnCmd, the skip range will"
                                     " completly disable the cmd")

        # make a list of the path involved in the disabling
        cmdToUpdate = []

        for i in range(0, len(self.cmdList)):
            if self.cmdList[i] == self.cmdList[cmdID]:
                cmdToUpdate.append(i)

        # explore the stack looking after these paths
        for i in xrange(0, self.stack.size()):
            if self.stack.typeOnIndex(i) != PREPROCESS_INSTRUCTION:
                break

            if self.stack.cmdIndexOnIndex(i) not in cmdToUpdate:
                continue

            if (not allowToDisableDataBunch and
               self._willThisDataBunchBeCompletlyDisabled(i,
                                                          subCmdID,
                                                          skipCount)):
                raise executionException("(engine) _skipOnCmd, the skip range"
                                         " will completly disable a databunch "
                                         "on the stack")

        # no prblm found, the disabling can occur
        howManyToSkip = min(len(self.cmdList[cmdID]), subCmdID+skipCount)
        for i in xrange(subCmdID, howManyToSkip):
            self.cmdList[cmdID].disableCmd(i)

    def _enableOnCmd(self, cmdID, subCmdID, enableCount=1):
        if enableCount < 1:
            raise executionException("(engine) _enableOnCmd, enable count must"
                                     " be equal or bigger than 1")

        isAValidIndex(self.cmdList, cmdID, "_enableOnCmd", "command list")
        isAValidIndex(self.cmdList[cmdID],
                      subCmdID,
                      "_enableOnCmd",
                      "sub command list")

        # no prblm found, the disabling can occur
        howManyToEnable = min(len(self.cmdList[cmdID]), subCmdID+enableCount)
        for i in xrange(subCmdID, howManyToEnable):
            self.cmdList[cmdID].enableCmd(i)

    def _skipOnDataBunch(self, dataBunchIndex, subCmdID, skipCount=1):
        if skipCount < 1:
            raise executionException("(engine) _skipOnDataBunch, skip count "
                                     "must be equal or bigger than 1")

        self.stack.raiseIfEmpty("_skipOnDataBunch")

        # check valid index
        isAValidIndex(self.stack, dataBunchIndex, "_skipOnDataBunch", "stack")
        isAValidIndex(self.stack.getCmd(dataBunchIndex, self.cmdList),
                      subCmdID,
                      "_skipOnDataBunch",
                      "sub command list")

        #  can only skip the next command if the state is pre_process
        if self.stack.typeOnIndex(dataBunchIndex) != PREPROCESS_INSTRUCTION:
            raise executionException("(engine) _skipOnDataBunch, can only skip"
                                     " method on PREPROCESS item")

        # if still not found, raise
        if self._willThisDataBunchBeCompletlyDisabled(dataBunchIndex,
                                                      subCmdID,
                                                      skipCount):
            raise executionException("(engine) _skipOnDataBunch, every sub cmd"
                                     " in this databunch will be disabled with"
                                     " this skip range")

        enablingMap = self.stack.enablingMapOnIndex(dataBunchIndex)

        if enablingMap is None:
            cmdLength = self.stack.subCmdLengthOnIndex(dataBunchIndex,
                                                       self.cmdList)
            enablingMap = [True] * cmdLength

        for i in xrange(subCmdID, min(subCmdID+skipCount, len(enablingMap))):
            if not enablingMap[i]:
                continue

            enablingMap[i] = False

        self.stack.setEnableMapOnIndex(dataBunchIndex, enablingMap)

    def _enableOnDataBunch(self, dataBunchIndex, subCmdID, enableCount=1):
        if enableCount < 1:
            raise executionException("(engine) _skipOnDataBunch, skip count "
                                     "must be equal or bigger than 1")

        self.stack.raiseIfEmpty("_skipOnDataBunch")

        # check valid index
        isAValidIndex(self.stack, dataBunchIndex, "_skipOnDataBunch", "stack")
        isAValidIndex(self.stack.getCmd(dataBunchIndex, self.cmdList),
                      subCmdID,
                      "_skipOnDataBunch",
                      "sub command list")

        #  can only skip the next command if the state is pre_process
        if self.stack.typeOnIndex(dataBunchIndex) != PREPROCESS_INSTRUCTION:
            raise executionException("(engine) _skipOnDataBunch, can only "
                                     "skip method on PREPROCESS item")

        if self._willThisDataBunchBeCompletlyEnabled(dataBunchIndex,
                                                     subCmdID,
                                                     enableCount):
            enablingMap = None
        else:
            enablingMap = self.stack.enablingMapOnIndex(dataBunchIndex)

            enableUntil = min(subCmdID+enableCount, len(enablingMap))
            for i in xrange(subCmdID, enableUntil):
                if enablingMap[i]:
                    continue

                enablingMap[i] = True

        self.stack.setEnableMapOnIndex(dataBunchIndex, enablingMap)

    def skipNextSubCommandOnTheCurrentData(self, skipCount=1):
        if skipCount < 1:
            raise executionException("(engine) "
                                     "skipNextSubCommandOnTheCurrentData, skip"
                                     " count must be equal or bigger than 1")

        self.stack.raiseIfEmpty("skipNextSubCommandOnTheCurrentData")
        #  can only skip the next command if the state is pre_process
        if self.stack.typeOnTop() != PREPROCESS_INSTRUCTION:
            raise executionException("(engine) "
                                     "skipNextSubCommandOnTheCurrentData, can"
                                     " only skip method on PREPROCESS item")

        if self._isInProcess:
            if self.topPreIndexOpp is None or self.topPreIndexOpp >= 0:
                self.topPreIndexOpp += skipCount
            else:
                raise executionException("(engine) "
                                         "skipNextSubCommandOnTheCurrentData, "
                                         "a pending operation is already "
                                         "present on this databunch, can not "
                                         "skip the next sub command")
        else:
            self.stack[-1][1][-1] += skipCount

    def skipNextSubCommandForTheEntireDataBunch(self, skipCount=1):
        self.stack.raiseIfEmpty("skipNextSubCommandForTheEntireDataBunch")
        self._skipOnDataBunch(-1, self.stack.subCmdIndexOnTop()+1, skipCount)

    def skipNextSubCommandForTheEntireExecution(self, skipCount=1):
        self.stack.raiseIfEmpty("skipNextSubCommandForTheEntireExecution")
        self._skipOnCmd(self.stack.cmdIndexOnTop(),
                        self.stack.subCmdIndexOnTop(),
                        skipCount)

    def disableEnablingMapOnDataBunch(self, index=-1):
        isAValidIndex(self.stack,
                      index,
                      "disableEnablingMapOnDataBunch",
                      "stack")

        #  can only skip the next command if the state is pre_process
        if self.stack.typeOnIndex(index) != PREPROCESS_INSTRUCTION:
            raise executionException("(engine) disableEnablingMapOnDataBunch, "
                                     "can only skip method on PREPROCESS item")

        mapping = self.stack.enablingMapOnIndex(index)

        if mapping is not None:
            self.stack.setEnableMapOnIndex(index, None)

    def enableSubCommandInCurrentDataBunchMap(self, indexSubCmd):
        self._enableOnDataBunch(-1, indexSubCmd, 1)

    def enableSubCommandInCommandMap(self, indexCmd, indexSubCmd):
        self._enableOnCmd(indexCmd, indexSubCmd, 1)

    def disableSubCommandInCurrentDataBunchMap(self, indexSubCmd):
        self._skipOnDataBunch(-1, indexSubCmd, 1)

    def disableSubCommandInCommandMap(self, indexCmd, indexSubCmd):
        self._skipOnCmd(indexCmd, indexSubCmd, 1)

    def flushArgs(self, index=None):  # None index means current command
        if index is None:
            self.stack.raiseIfEmpty("flushArgs")
            cmdID = self.stack.cmdIndexOnTop()
        else:
            cmdID = index

        isAValidIndex(self.argsList, cmdID, "flushArgs", "arg list")
        self.argsList[cmdID] = None
        self.mappedArgsList[cmdID] = (EMPTY_MAPPED_ARGS,
                                      EMPTY_MAPPED_ARGS,
                                      EMPTY_MAPPED_ARGS,)

    def addSubCommand(self, cmd, cmdID=None, onlyAddOnce=True, useArgs=True):
        # is a valid cmd ?
        # only the Command are allowed in the list
        if not isinstance(cmd, Command):
            raise executionException("(engine) addSubCommand, cmd is not a "
                                     "Command instance, got '"+str(type(cmd)) +
                                     "'")

        # compute the current command index where the sub command will be
        # insert, check the cmd path on the stack
        if cmdID is None:
            self.stack.raiseIfEmpty("addSubCommand")
            cmdID = self.stack.cmdIndexOnTop()

        isAValidIndex(self.cmdList, cmdID, "addSubCommand", "command list")

        # add the sub command
        self.cmdList[cmdID].addDynamicCommand(cmd, onlyAddOnce, useArgs)

        # build a list with the index in cmdList with the equivalent cmd as
        # the cmd at cmdID
        cmdToUpdate = []
        for i in range(0, len(self.cmdList)):
            if self.cmdList[i] == self.cmdList[cmdID]:
                cmdToUpdate.append(i)

        for i in range(0, self.stack.size()):
            if self.stack.typeOnIndex(i) != PREPROCESS_INSTRUCTION:
                break

            # is it a wrong path ?
            if self.stack.cmdIndexOnIndex(i) not in cmdToUpdate:
                continue

            # is there an enabled mapping ?
            enablingMap = self.stack.enablingMapOnIndex(i)
            if enablingMap is None:
                continue

            enablingMap.append(True)

    def addCommand(self, cmd, convertProcessToPreProcess=False):
        # only the MultiCommand are allowed in the list
        if not isinstance(cmd, MultiCommand):
            raise executionException("(engine) addCommand, cmd is not a "
                                     "MultiCommand instance, got '" +
                                     str(type(cmd))+"'")

        # The process (!= pre and != post), must always be the process
        # of the last command in the list
        # if we add a new command, the existing process on the stack
        # became invalid
        stackSize = self.stack.size()
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
            if i == stackSize-1 and len(self.stack.dataOnTop()) == 1:
                continue

            if not convertProcessToPreProcess:
                raise executionException("(engine) addCommand, some process "
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
        self.cmdList.append(cmd)

    def isCurrentRootCommand(self):
        self.stack.raiseIfEmpty("isCurrentRootCommand")
        return self.stack.cmdIndexOnTop() == 0

    def isCurrentProcessCommand(self):
        self.stack.raiseIfEmpty("isCurrentProcessCommand")
        return self.stack.cmdIndexOnTop() == len(self.cmdList)-1

    def getCurrentCommand(self):
        self.stack.raiseIfEmpty("getCurrentCommand")
        return self.cmdList[self.stack.cmdIndexOnTop()]

    def hasPreviousCommand(self):
        self.stack.raiseIfEmpty("hasPreviousCommand")
        return self.stack.cmdIndexOnTop() > 0

    def getPreviousCommand(self):
        self.stack.raiseIfEmpty("getPreviousCommand")
        if self.stack.cmdIndexOnTop() == 0:
            raise executionException("(engine) getPreviousCommand, there is no"
                                     " previous command")

        return self.cmdList[self.stack.cmdIndexOnTop()-1]

# ##  SPLIT/MERGE meth # ##

    def mergeDataAndSetEnablingMap(self,
                                   toppestItemToMerge=-1,
                                   newMap=None,
                                   count=2):
        self.stack.raiseIfEmpty("mergeDataAndSetEnablingMap")
        isAValidIndex(self.stack,
                      toppestItemToMerge,
                      "mergeDataAndSetEnablingMap",
                      "stack")
        raisIfInvalidMap(newMap,
                         self.stack.subCmdLengthOnIndex(toppestItemToMerge,
                                                        self.cmdList),
                         "mergeDataAndSetEnablingMap")

        # current index must be enabled in map
        if newMap is not None:
            subindex = self.stack.subCmdIndexOnIndex(toppestItemToMerge)
            if not newMap[subindex]:
                raise executionException("(engine) mergeDataAndSetEnablingMap,"
                                         " the current sub command is disabled"
                                         " in the new map")

        # convert toppestItemToMerge into positive value
        if toppestItemToMerge < 0:
            toppestItemToMerge = len(self.stack) + toppestItemToMerge

        # merge items on stack
        self.mergeData(toppestItemToMerge, count, None)

        # set the new map
        self.stack.setEnableMapOnIndex(toppestItemToMerge - count + 1, newMap)

    def mergeData(self,
                  toppestItemToMerge=-1,
                  count=2,
                  indexOfTheMapToKeep=None):
        # need at least two item to merge
        if count < 2:
            return False  # no need to merge

        # check and manage index
        isAValidIndex(self.stack, toppestItemToMerge, "mergeData", "stack")
        if toppestItemToMerge < 0:
            toppestItemToMerge = len(self.stack) + toppestItemToMerge

        # the stack need to hold at least count
        if toppestItemToMerge+1 < count:
            raise executionException("(engine) mergeDataOnStack, no enough of "
                                     "data on stack to merge from this index")

        # can only merge on PREPROCESS
        if (self.stack.typeOnIndex(toppestItemToMerge) !=
           PREPROCESS_INSTRUCTION):
            raise executionException("(engine) mergeDataOnStack, try to merge "
                                     "a not preprocess action")

        # check dept and get map
        if indexOfTheMapToKeep is not None:
            if (indexOfTheMapToKeep < 0 or
               indexOfTheMapToKeep > toppestItemToMerge):
                raise executionException("(engine) mergeDataOnStack, the "
                                         "selected map to apply is not one the"
                                         " map of the selected items")

            # get the valid map
            enablingMap = self.stack.enablingMapOnIndex(indexOfTheMapToKeep)

            if enablingMap is not None:
                # the current index must be enabled in the new map
                subindex = self.stack.subCmdIndexOnIndex(toppestItemToMerge)
                if not enablingMap[subindex]:
                    raise executionException("(engine) "
                                             "mergeDataAndSetEnablingMap, the "
                                             "current sub command is disabled "
                                             "in the selected map")

        else:
            # does not keep any map
            enablingMap = None

        # extract information from first item
        path = self.stack.pathOnIndex(toppestItemToMerge)

        for i in range(1, count):
            currentStackItem = self.stack.itemOnIndex(toppestItemToMerge-i)
            equals, sameLength, equalsCount, path1IsHigher = \
                equalPath(path, currentStackItem[1])

            # the path must be the same for each item to merge
            #   execpt for the last command, the items not at the top of the
            #   stack must have 0 or the cmdStartLimit
            if not sameLength:
                raise executionException("(engine) mergeDataOnStack, the "
                                         "command path is different for the "
                                         "item at index <"+str(i)+">")

            if not equals:
                raise executionException("(engine) mergeDataOnStack, a "
                                         "subcommand index is different for "
                                         "the item at sub index <" +
                                         str(equalsCount)+">")

            # the action must be the same type
            if currentStackItem[2] != PREPROCESS_INSTRUCTION:
                raise executionException("(engine) mergeDataOnStack, the "
                                         "action of the item at index <" +
                                         str(i)+"> is different of the action"
                                         " ot the first item")

        # merge data and keep start/end command
        dataBunch = []
        for i in range(0, count):
            dataBunch.extend(self.stack.dataOnIndex(toppestItemToMerge - i))
            del self.stack[toppestItemToMerge - i]

        self.stack.insert(toppestItemToMerge-count+1,
                          (dataBunch,
                           path,
                           PREPROCESS_INSTRUCTION,
                           enablingMap,))
        return True

    def splitDataAndSetEnablingMap(self,
                                   itemToSplit=-1,
                                   splitAtDataIndex=0,
                                   map1=None,
                                   map2=None):
        self.stack.raiseIfEmpty("splitDataAndSetEnablingMap")
        isAValidIndex(self.stack,
                      itemToSplit,
                      "splitDataAndSetEnablingMap",
                      "stack")
        expectedMapLength = self.stack.subCmdLengthOnIndex(itemToSplit,
                                                           self.cmdList)
        raisIfInvalidMap(map1, expectedMapLength, "splitDataAndSetEnablingMap")
        raisIfInvalidMap(map2, expectedMapLength, "splitDataAndSetEnablingMap")

        # get a positive index
        if itemToSplit < 0:
            itemToSplit = len(self.stack) + itemToSplit

        # current index must be enabled in new map1 (really ?)
        if (map1 is not None and
           not map1[self.stack.subCmdIndexOnIndex(itemToSplit)]):
            raise executionException("(engine) mergeDataAndSetEnablingMap, the"
                                     " current sub command can not be disabled"
                                     " in the map1")

        # compute first available in map2
        newMap2Index = 0

        # split
        state = self.splitData(itemToSplit, splitAtDataIndex, True)

        # set new map
        if state:  # is a split occured ?
            self.stack.setEnableMapOnIndex(itemToSplit, map2)
            self.stack.pathOnIndex(itemToSplit)[-1] = newMap2Index
            self.stack.setEnableMapOnIndex(itemToSplit+1, map1)
        else:
            self.stack.setEnableMapOnIndex(itemToSplit, map1)

        return state

    # split the data into two separate stack item at the index, but will not
    # change anything in the process order
    def splitData(self,
                  itemToSplit=-1,
                  splitAtDataIndex=0,
                  resetEnablingMap=False):
        # is empty stack ?
        self.stack.raiseIfEmpty("splitData")
        isAValidIndex(self.stack, itemToSplit, "splitData", "stack")

        # is it a pre ? (?)
        if self.stack.typeOnIndex(itemToSplit) != PREPROCESS_INSTRUCTION:
            raise executionException("(engine) splitData, can't split the "
                                     "data of a PRO/POST process because it "
                                     "will not change anything on the "
                                     "execution")

        # split point exist ?
        topdata = self.stack.dataOnIndex(itemToSplit)
        isAValidIndex(topdata, splitAtDataIndex, "splitData", "data to split")

        # has enought data to split ?
        if len(topdata) < 2 or splitAtDataIndex == 0:
            return False

        # recompute itemToSplit if needed
        if itemToSplit < 0:
            itemToSplit = len(self.stack) + itemToSplit

        # pop
        top = self.stack[itemToSplit]
        del self.stack[itemToSplit]

        path = top[1][:]
        if resetEnablingMap:
            enableMap = None
            path[-1] = 0
        else:
            enableMap = top[3]
            path[-1] = 0

        # push the two new items
        self.stack.insert(itemToSplit, (top[0][0:splitAtDataIndex],
                                        top[1],
                                        top[2],
                                        enableMap,))
        self.stack.insert(itemToSplit, (top[0][splitAtDataIndex:],
                                        path,
                                        top[2],
                                        enableMap,))

        return True

# ##  DATA meth (data of the top item on the stack) # ##

    def flushData(self):
        self.stack.raiseIfEmpty("flushData")
        # remove everything, the engine is able to manage an empty data bunch
        del self.stack.dataOnTop()[:]

    def appendData(self, newdata):
        self.stack.raiseIfEmpty("addData")
        self.stack.dataOnTop().append(newdata)

    def addData(self, newdata, offset=-1, forbideInsertionAtZero=True):
        self.stack.raiseIfEmpty("addData")
        data = self.stack.dataOnTop()

        if forbideInsertionAtZero and offset == 0:
            raise executionException("(engine) addData, can't insert a data at"
                                     " offset 0, it could create infinite "
                                     "loop. it is possible to override this "
                                     "check with the boolean "
                                     "forbideInsertionAtZero, set it to False")

        data.insert(offset, newdata)

    def removeData(self, offset=0, resetSubCmdIndexIfOffsetZero=True):
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
        if resetSubCmdIndexIfOffsetZero and (offset == 0 or len(data) == 0):
            # the engine will compute the first enabled cmd, if there is no
            # more data, let the engine compute the cmd index too
            if self._isInProcess:
                if self.topPreIndexOpp is None or self.topPreIndexOpp == -1:
                    self.topPreIndexOpp = -1
                else:
                    raise executionException("(engine) removeData, a pending "
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
            cmd = self.stack.getCmdOnTop(self.cmdList)
            subCmdIndex = self.stack.subCmdIndexOnTop() % len(cmd)
            enablingMap = self.stack.enablingMapOnTop()
            data = self.stack.dataOnTop()

            # ##  COMPUTE THE FIRST AVAILABLE INDEX # ##
            subCmdIndex %= len(cmd)
            beforeCurrentIndex = (subCmdIndex + len(cmd) - 1) % len(cmd)
            while len(data) > 0:
                if ((enablingMap is not None and
                   not enablingMap[subCmdIndex]) or
                   cmd.isdisabledCmd(subCmdIndex)):
                    # we test every cmd available in this databunch,
                    # they are all disabled
                    if subCmdIndex == beforeCurrentIndex:
                        data = ()
                        # will go to the else statement of the current loop
                        continue

                    subCmdIndex += 1

                    # do we reach the end of the available index for this
                    # data ?
                    if subCmdIndex >= len(cmd):
                        del data[0]
                        subCmdIndex = 0

                    continue  # need to test the next index
                break  # we have an enabled index with at least one data

            # len(self.stack.dataOnTop()) == 0: # if empty data, this
            # databunch is out, no more thing to do
            else:
                self.stack.pop()
                continue

            # ##  EXTRACT DATA FROM STACK # ##
            top = self.stack.top()
            subcmd, useArgs, enabled = cmd[subCmdIndex]
            insType = self.stack.typeOnTop()
            top[1][-1] = subCmdIndex  # set current index in databunch

            # ##  EXECUTE command # ##
            # prepare the var to push on the stack, if the var keep the
            # none value, nothing will be stacked
            to_stack = None

            if useArgs:
                indexOnTop = self.stack.cmdIndexOnTop()
                args = self.argsList[indexOnTop]
                mappedArgs = self.mappedArgsList[indexOnTop]
            else:
                args = None
                mappedArgs = EMPTY_MAPPED_ARGS

            # #  PRE PROCESS
            if insType == PREPROCESS_INSTRUCTION:  # pre
                r = self._executeMethod(cmd,
                                        subcmd.preProcess,
                                        top,
                                        args,
                                        mappedArgs[0])
                subcmd.preCount += 1

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
                if len(top[1]) == len(self.cmdList):
                    to_stack = (r, new_path, PROCESS_INSTRUCTION, )
                else:
                    # there are some child, next step will be another
                    # preprocess
                    # build first index to execute, it's not always 0
                    # new_cmd = self.cmdList[len(top[1])]  # the -1 is not
                    # missing, we want the next cmd, not the current
                    # nextData, newIndex =
                    # self._computeTheNextChildToExecute(new_cmd,
                    # len(new_cmd)-1, None)

                    # the first cmd has no subcmd enabled, impossible to
                    # start the engine
                    # if newIndex == -1:
                    #     raise executionException("(engine) execute, no
                    #       enabled subcmd on the cmd "+str(len(top[1])))

                    # then add the first index of the next command
                    new_path.append(0)
                    to_stack = (r, new_path, PREPROCESS_INSTRUCTION, )

            # #  PROCESS # #
            elif insType == PROCESS_INSTRUCTION:  # pro
                r = self._executeMethod(cmd,
                                        subcmd.process,
                                        top,
                                        None,
                                        mappedArgs[1])
                subcmd.proCount += 1
                # manage result
                to_stack = (r, top[1][:], POSTPROCESS_INSTRUCTION,)

                if self.topProcessToPre:
                    self.topProcessToPre = False
                    top[1].append(0)

            # #  POST PROCESS # #
            elif insType == POSTPROCESS_INSTRUCTION:  # post
                r = self._executeMethod(cmd,
                                        subcmd.postProcess,
                                        top,
                                        None,
                                        mappedArgs[2])
                subcmd.postCount += 1

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
                raise executionException("(engine) execute, unknwon process "
                                         "command '"+str(insType)+"'")

            if self.selfkillreason is not None:
                reason, abnormal = self.selfkillreason
                raise engineInterruptionException("(engine) stopExecution, "
                                                  "execution stop, reason: " +
                                                  reason,
                                                  abnormal)

            if subcmd.preCount > DEFAULT_EXECUTION_LIMIT:
                raise executionException("(engine) execute, this subcommand "
                                         "reach the execution limit count for "
                                         "preprocess")
            elif subcmd.proCount > DEFAULT_EXECUTION_LIMIT:
                raise executionException("(engine) execute, this subcommand "
                                         "reach the execution limit count for "
                                         "process")
            elif subcmd.postCount > DEFAULT_EXECUTION_LIMIT:
                raise executionException("(engine) execute, this subcommand "
                                         "reach the execution limit count for "
                                         "postprocess")

            # ##  MANAGE STACK, need to repush the current item ? # ##
            self.stack.pop()

            # process or postprocess ?
            if (insType == PROCESS_INSTRUCTION or
               insType == POSTPROCESS_INSTRUCTION):
                if len(top[0]) > 1:  # still data to execute ?
                    # remove the last used data and push on the stack
                    self.stack.push(top[0][1:], top[1], top[2])
            # insType == 0 # preprocess, can't be anything else, a test has
            # already occured sooner in the engine function
            else:
                nextData, newIndex = \
                    self._computeTheNextChildToExecute(cmd, top[1][-1], top[3])
                # something to do ? (if newIndex == -1, there is no
                # more enabled cmd for this data bunch)
                if (((not nextData and len(top[0]) > 0) or len(top[0]) > 1) and
                   newIndex >= 0):
                    # if we need to use the next data,
                    # we need to remove the old one
                    if nextData:
                        del top[0][0]  # remove the used data

                    # select the next child id
                    top[1][-1] = newIndex

                    # push on the stack again
                    self.stack.push(top[0], top[1], top[2], top[3])

            # ##  STACK THE RESULT of the current process if needed # ##
            if to_stack is not None:
                self.stack.push(*to_stack)

    def _computeTheNextChildToExecute(self,
                                      cmd,
                                      currentSubCmdIndex,
                                      enablingMap):
        currentSubCmdIndex = min(currentSubCmdIndex, len(cmd) - 1)
        startingIndex = currentSubCmdIndex
        executeOnNextData = False
        while True:
            # increment
            startingIndex = (startingIndex+1) % len(cmd)

            # did it reach the next data ?
            if startingIndex == 0:
                executeOnNextData = True

            # is it a valid command to execute ?
            if (cmd[startingIndex][2] and
               (enablingMap is None or enablingMap[startingIndex])):
                return executeOnNextData, startingIndex

            # stop condition
            if startingIndex == currentSubCmdIndex:
                return executeOnNextData, -1

    def _executeMethod(self,
                       cmd,
                       subcmd,
                       stackState,
                       args=None,
                       mappedArgs=EMPTY_MAPPED_ARGS):
        nextData = stackState[0][0]

        # prepare data
        if args is not None:
            args = args[:]
            if nextData != EMPTY_DATA_TOKEN:
                # case where the previous process return a list of element
                if hasattr(nextData, "__iter__"):
                    args.extend(nextData)
                else:  # case where the previous process return only one args
                    args.append(nextData)

        elif nextData != EMPTY_DATA_TOKEN:
            args = nextData
        else:
            args = ()

        # execute checker
        if hasattr(subcmd, "checker"):
            # TODO use mappedArgs in checker

            data = subcmd.checker.checkArgs(args, mappedArgs, self)

            # find lockable object
            lockableList = []
            for k, v in data.items():
                if not isinstance(v, EnvironmentParameter):
                    continue

                if not v.isLockEnable():
                    continue

                lockableList.append(v)

            lock = ParametersLocker(lockableList)

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
                      afterThisProcess=True,
                      abnormal=False):
        if not self._isInProcess:
            raise executionException("(engine) stopExecution, can not "
                                     "execute this method outside of a "
                                     "process")

        if reason is None:
            reason = "unknown"

        if not afterThisProcess:
            raise engineInterruptionException("(engine) stopExecution, "
                                              "execution stop, reason: " +
                                              reason,
                                              abnormal)
        else:
            self.selfkillreason = (reason, abnormal,)

    def raiseIfInMethodExecution(self, methName=None):
        if methName is None:
            methName = ""
        else:
            methName += ", "

        if self._isInProcess:
            raise executionException("(engine) "+methName+", not allowed to "
                                     "execute this method inside a process")

    def raiseIfNotInMethodExecution(self, methName=None):
        if methName is None:
            methName = ""
        else:
            methName += ", "

        if not self._isInProcess:
            raise executionException("(engine) "+methName+", not allowed to "
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
            info["processType"] = -1
        else:
            top = self.stack.top()

            # the index of the current command in execution
            info["cmdIndex"] = self.stack.cmdIndexOnTop()

            # the object instance of the current command in execution
            info["cmd"] = self.stack.getCmdOnTop(self.cmdList)

            # the index of the current sub command in execution
            info["subCmdIndex"] = self.stack.subCmdIndexOnTop()

            # the object instance of the current sub command in execution
            info["subCmd"] = self.cmdList[len(top[1])-1][top[1][-1]]

            # the data of the current execution
            info["data"] = self.stack.dataOnTop()

            # the process type of the current execution
            info["processType"] = self.stack.typeOnTop()

        return info

    def printStack(self):
        if self.stack.size() == 0:
            print("empty stack")

        for i in range(self.stack.size()-1, -1, -1):
            cmdEnabled = self.stack[i][3]
            if cmdEnabled is None:
                cmdEnabled = "(no mapping)"

            print("# ["+str(i)+"] data="+str(self.stack[i][0])+", path=" +
                  str(self.stack[i][1])+", action="+str(self.stack[i][2]) +
                  ", cmd enabled="+str(cmdEnabled))

    def printCmdList(self):
        if len(self.cmdList) == 0:
            print("no command in the engine")
            return

        for i in range(0, len(self.cmdList)):
            print("Command <"+str(i)+">")
            for j in range(0, len(self.cmdList[i])):
                c, a, e = self.cmdList[i][j]
                print("    SubCommand <"+str(j)+"> (useArgs="+str(a) +
                      ", enabled="+str(e)+")")

    def printCmdPath(self, path=None):
        if len(self.cmdList) == 0:
            print("no command in the engine")
            return

        if path is None:
            if self.stack.isEmpty():
                print("no item on the stack, and so no path available")

            path = self.stack.pathOnTop()

        for i in range(0, len(topPath)):
            if i >= len(self.cmdList):
                print("# ["+str(i)+"] out of bound index")
                continue

            if topPath[i] < 0 or topPath[i] >= len(self.cmdList[i]):
                print("# ["+str(i)+"] out of bound index in the command")
                continue

            if len(self.cmdList[i]) == 1:
                print("# ["+str(i)+"]")
                continue

            print("# ["+str(i)+"]"+" (sub="+str(topPath[i])+")")
