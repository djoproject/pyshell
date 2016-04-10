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

from threading import Lock

from tries import multiLevelTries

from pyshell.system.container import AbstractParameterContainer
from pyshell.system.container import DEFAULT_DUMMY_PARAMETER_CONTAINER
from pyshell.system.settings import GlobalSettings
from pyshell.system.settings import LocalSettings
from pyshell.utils.exception import ParameterException
from pyshell.utils.flushable import Flushable
from pyshell.utils.synchronized import synchronous
from pyshell.utils.valuable import Valuable


def isAValidStringPath(string_path):
    if type(string_path) != str and type(string_path) != unicode:
        return False, "invalid string_path, a string was expected, got '" + \
            str(type(string_path))+"'"

    path = string_path.split(".")
    final_path = []

    for index in range(0, len(path)):
        if len(path[index]) == 0:
            continue

        final_path.append(path[index])

    return True, tuple(final_path)


def _buildExistingPathFromError(wrong_path, advanced_result):
    path_to_return = list(advanced_result.getFoundCompletePath())
    path_to_return.extend(wrong_path[advanced_result.getTokenFoundCount():])
    return path_to_return


class ParameterTriesNode(object):
    def __init__(self):
        self.global_var = None
        self.local_var = None
        self.origin_loader = None
        self.starting_hash = None

    def hasLocalVar(self, key):
        return self.local_var is not None and key in self.local_var

    def hasGlobalVar(self):
        return self.global_var is not None

    def getLocalVar(self, key):
        return self.local_var[key]

    def getGlobalVar(self):
        return self.global_var

    def setLocalVar(self, key, value):
        if self.local_var is None:
            self.local_var = {}

        self.local_var[key] = value

    def setGlobalVar(self, value, freeze=False):
        self.global_var = value

        if self.starting_hash is not None or self.origin_loader is not None:
            self.global_var.settings.setStartingPoint(self.starting_hash)
            self.global_var.settings.setLoaderOrigin(self.origin_loader)
        else:
            self.global_var.settings.setStartingPoint(hash(self.global_var))

            if freeze:
                self.origin_loader = self.global_var.settings.loaderOrigin
                self.starting_hash = self.global_var.settings.startingHash

    def unsetGlobalVar(self):
        self.global_var = None

    def unsetLocalVar(self, key):
        if self.local_var is not None and key in self.local_var:
            del self.local_var[key]

    def isRemovable(self):
        return (self.global_var is None and
                (self.local_var is None or len(self.local_var) == 0) and
                self.starting_hash is None and self.origin_loader is None)


class ParameterManager(Flushable):
    def __init__(self, parent=None):
        self._internalLock = Lock()
        self.mltries = multiLevelTries()

        # hold the paths for the current level of the current thread
        self.threadLocalVar = {}

        if parent is None:
            self.parentContainer = DEFAULT_DUMMY_PARAMETER_CONTAINER
        else:
            if not isinstance(parent, AbstractParameterContainer):
                excmsg = ("(ParameterManager) __init__, expect an instance of "
                          "AbstractParameterContainer, got '" +
                          str(type(parent))+"'")
                raise ParameterException(excmsg)

            self.parentContainer = parent

    def _getAdvanceResult(self,
                          meth_name,
                          string_path,
                          raise_if_not_found=True,
                          raise_if_ambiguous=True,
                          perfect_match=False):

        # prepare and check path
        state, result = isAValidStringPath(string_path)

        if not state:
            excmsg = "(ParameterManager) "+str(meth_name)+", "+result
            raise ParameterException(excmsg)

        path = result

        # explore mltries
        advanced_result = self.mltries.advancedSearch(path, perfect_match)

        if raise_if_ambiguous and advanced_result.isAmbiguous():
            index_of_ambiguous_key = advanced_result.getTokenFoundCount()
            possible_path = \
                self.mltries.buildDictionnary(path[:index_of_ambiguous_key],
                                              ignoreStopTraversal=True,
                                              addPrexix=True,
                                              onlyPerfectMatch=False)
            possible_value = []
            for k, v in possible_path.items():
                possible_value.append(k[index_of_ambiguous_key])

            existing_path = ".".join(
                _buildExistingPathFromError(path, advanced_result))
            excmsg = ("(ParameterManager) "+str(meth_name)+", key '" +
                      str(path[index_of_ambiguous_key])+"' is ambiguous for"
                      " path '"+existing_path+"', possible value are: '" +
                      ",".join(possible_value)+"'")
            raise ParameterException(excmsg)

        if raise_if_not_found and not advanced_result.isValueFound():
            index_not_found = advanced_result.getTokenFoundCount()
            existing_path = ".".join(
                _buildExistingPathFromError(path, advanced_result))
            excmsg = ("(ParameterManager) "+str(meth_name)+", key '" +
                      str(path[index_not_found])+"' is unknown for path '" +
                      existing_path+"'")
            raise ParameterException(excmsg)

        return advanced_result

    def getAllowedType(self):  # XXX to override if needed
        return Parameter

    def isAnAllowedType(self, value):  # XXX to override if needed
        return isinstance(value, self.getAllowedType()) and \
            value.__class__.__name__ == self.getAllowedType().__name__
        # second condition is to forbidde child class

    def extractParameter(self, value):
        if self.isAnAllowedType(value):
            return value

        if isinstance(value, Parameter):
            excmsg = ("(ParameterManager) extractParameter, can not use an "
                      "object of type '"+str(type(value))+"' in this manager")
            raise ParameterException(excmsg)

        # try to instanciate parameter, may raise if invalid type
        return self.getAllowedType()(value)

    # TODO test the frozen cases
    @synchronous()
    def setParameter(self,
                     string_path,
                     param,
                     local_param=True,
                     freeze_starting_point=False):
        param = self.extractParameter(param)

        if freeze_starting_point and local_param:
            excmsg = ("(ParameterManager) setParameter, can not "
                      "freeze starting point with a local parameter")
            raise ParameterException(excmsg)

        # check safety and existing
        advanced_result = self._getAdvanceResult("setParameter",
                                                 string_path,
                                                 False,
                                                 False,
                                                 True)
        if advanced_result.isValueFound():
            parameter_node = advanced_result.getValue()

            if local_param:
                key = self.parentContainer.getCurrentId()

                if parameter_node.hasLocalVar(key):
                    local_var = parameter_node.getLocalVar(key)
                    if local_var.settings.isReadOnly():
                        complete_path = " ".join(
                            advanced_result.getFoundCompletePath())
                        excmsg = ("(ParameterManager) setParameter, can not "
                                  "set the parameter '"+complete_path+"' "
                                  "because a parameter with this name already"
                                  " exist and is not editable")
                        raise ParameterException(excmsg)
                else:
                    if key not in self.threadLocalVar:
                        self.threadLocalVar[key] = set()

                    complete_path = advanced_result.getFoundCompletePath()
                    self.threadLocalVar[key].add(
                        '.'.join(str(x) for x in complete_path))

                param.enableLocal()
                parameter_node.setLocalVar(key, param)
            else:
                if parameter_node.hasGlobalVar():
                    global_var = parameter_node.getGlobalVar()
                    if global_var.settings.isReadOnly():
                        complete_path = " ".join(
                            advanced_result.getFoundCompletePath())
                        excmsg = ("(ParameterManager) setParameter, can not "
                                  "set the parameter '"+complete_path+"' "
                                  "because a parameter with this name already"
                                  " exist and is not editable")
                        raise ParameterException(excmsg)

                    if (freeze_starting_point and
                       (parameter_node.starting_hash is not None or
                            parameter_node.origin_loader is not None)):
                        excmsg = ("(ParameterManager) setParameter, can not "
                                  "freeze starting point, it is already "
                                  "frozen.")
                        raise ParameterException(excmsg)

                param.enableGlobal()

                if (freeze_starting_point and
                   param.settings.loaderOrigin is None):
                    excmsg = ("(ParameterManager) setParameter, can not "
                              "freeze starting point, loader origin "
                              "is not defined.")
                    raise ParameterException(excmsg)

                parameter_node.setGlobalVar(param,
                                            freeze=freeze_starting_point)
        else:
            parameter_node = ParameterTriesNode()
            if local_param:
                global_var = None
                key = self.parentContainer.getCurrentId()
                parameter_node.setLocalVar(key, param)
                param.enableLocal()

                if key not in self.threadLocalVar:
                    self.threadLocalVar[key] = set()

                self.threadLocalVar[key].add(string_path)

            else:
                param.enableGlobal()

                if (freeze_starting_point and
                   param.settings.loaderOrigin is None):
                    excmsg = ("(ParameterManager) setParameter, can not "
                              "freeze starting point, loader origin "
                              "is not defined.")
                    raise ParameterException(excmsg)

                parameter_node.setGlobalVar(param,
                                            freeze=freeze_starting_point)

            self.mltries.insert(string_path.split("."), parameter_node)

        return param

    @synchronous()
    def getParameter(self,
                     string_path,
                     perfect_match=False,
                     local_param=True,
                     explore_other_level=True):

        # this call will raise if value not found or ambiguous
        advanced_result = self._getAdvanceResult("getParameter",
                                                 string_path,
                                                 perfect_match=perfect_match,
                                                 raise_if_not_found=False)

        if advanced_result.isValueFound():
            parameter_node = advanced_result.getValue()

            # simple loop to explore the both statment of this condition
            # if needed, without ordering
            for case in range(0, 2):
                if local_param:
                    key = self.parentContainer.getCurrentId()
                    if parameter_node.hasLocalVar(key):
                        return parameter_node.getLocalVar(key)

                    if not explore_other_level:
                        break
                else:
                    if parameter_node.hasGlobalVar():
                        return parameter_node.getGlobalVar()

                    if not explore_other_level:
                        break

                local_param = not local_param

        return None

    @synchronous()
    def hasParameter(self,
                     string_path,
                     raise_if_ambiguous=True,
                     perfect_match=False,
                     local_param=True,
                     explore_other_level=True):

        # this call will raise if ambiguous
        advanced_result = self._getAdvanceResult("hasParameter",
                                                 string_path,
                                                 False,
                                                 raise_if_ambiguous,
                                                 perfect_match)

        if advanced_result.isValueFound():
            parameter_node = advanced_result.getValue()

            # simple loop to explore the both statment of this condition if
            # needed, without any order
            for case in range(0, 2):
                if local_param:
                    key = self.parentContainer.getCurrentId()

                    if parameter_node.hasLocalVar(key):
                        return True

                    if not explore_other_level:
                        return False
                else:
                    if parameter_node.hasGlobalVar():
                        return True

                    if not explore_other_level:
                        return False

                local_param = not local_param

        return False

    @synchronous()
    def unsetParameter(self,
                       string_path,
                       local_param=True,
                       explore_other_level=True,
                       force=False):

        # this call will raise if value not found or ambiguous
        advanced_result = self._getAdvanceResult("unsetParameter",
                                                 string_path,
                                                 perfect_match=True)

        if advanced_result.isValueFound():
            parameter_node = advanced_result.getValue()

            # simple loop to explore the both statment of this condition if
            # needed, without any order
            for case in range(0, 2):
                if local_param:
                    key = self.parentContainer.getCurrentId()

                    if not parameter_node.hasLocalVar(key):
                        if not explore_other_level:
                            complete_path = " ".join(
                                advanced_result.getFoundCompletePath())
                            excmsg = ("(ParameterManager) unsetParameter, "
                                      "unknown local parameter '" +
                                      complete_path+"'")
                            raise ParameterException(excmsg)

                        local_param = not local_param
                        continue

                    if not force:
                        local_var = parameter_node.getLocalVar(key)
                        if not local_var.settings.isRemovable():
                            complete_path = " ".join(
                                advanced_result.getFoundCompletePath())
                            excmsg = ("(ParameterManager) unsetParameter, "
                                      "local parameter '"+complete_path+"' is"
                                      " not removable")
                            raise ParameterException(excmsg)

                    # remove from thread local list
                    complete_path = advanced_result.getFoundCompletePath()
                    self.threadLocalVar[key].remove(
                        '.'.join(str(x) for x in complete_path))
                    if len(self.threadLocalVar[key]) == 0:
                        del self.threadLocalVar[key]

                    # remove from mltries
                    parameter_node.unsetLocalVar(key)
                    if parameter_node.isRemovable():
                        path = advanced_result.getFoundCompletePath()
                        self.mltries.remove(path)

                    return

                else:
                    if not parameter_node.hasGlobalVar():
                        if not explore_other_level:
                            complete_path = " ".join(
                                advanced_result.getFoundCompletePath())
                            excmsg = ("(ParameterManager) unsetParameter, "
                                      "unknown global parameter '" +
                                      complete_path+"'")
                            raise ParameterException(excmsg)

                        local_param = not local_param
                        continue

                    if not force:
                        global_var = parameter_node.getGlobalVar()
                        if not global_var.settings.isRemovable():
                            complete_path = " ".join(
                                advanced_result.getFoundCompletePath())
                            excmsg = ("(ParameterManager) unsetParameter, "
                                      "parameter '"+complete_path+"' is not "
                                      "removable")
                            raise ParameterException(excmsg)

                    parameter_node.unsetGlobalVar()

                    if parameter_node.isRemovable():
                        path = advanced_result.getFoundCompletePath()
                        self.mltries.remove(path)

                    return

    @synchronous()
    def flush(self):  # flush the Variable at this Level For This Thread
        key = self.parentContainer.getCurrentId()

        # clean level
        # do we have recorded some variables for this thread at this level ?
        if key in self.threadLocalVar:

            # no error possible, missing value or invalid type is possible
            # here, because of the process in set/unset
            for path in self.threadLocalVar[key]:
                advanced_result = self._getAdvanceResult("flush",
                                                         path,
                                                         False,
                                                         False)
                parameter_node = advanced_result.getValue()
                parameter_node.unsetLocalVar(key)

                if parameter_node.isRemovable():
                    # can not raise, because every path exist
                    self.mltries.remove(path.split("."))

            del self.threadLocalVar[key]

    @synchronous()
    def buildDictionnary(self,
                         string_path,
                         local_param=True,
                         explore_other_level=True):
        state, result = isAValidStringPath(string_path)

        if not state:
            excmsg = "(ParameterManager) buildDictionnary, "+result
            raise ParameterException(excmsg)

        result = self.mltries.buildDictionnary(result, True, True, False)

        to_ret = {}
        key = None

        for var_key, parameter_node in result.items():
            local_param_tmp = local_param

            # simple loop to explore the both statment of this condition if
            # needed, without any order
            for case in range(0, 2):
                if local_param_tmp:
                    if key is None:
                        key = self.parentContainer.getCurrentId()

                    if parameter_node.hasLocalVar(key):
                        local_var = parameter_node.getLocalVar(key)
                        to_ret[".".join(var_key)] = local_var
                        break

                    if not explore_other_level:
                        break
                else:
                    if parameter_node.hasGlobalVar():
                        global_var = parameter_node.getGlobalVar()
                        to_ret[".".join(var_key)] = global_var
                        break

                    if not explore_other_level:
                        break

                local_param_tmp = not local_param_tmp

        return to_ret


class Parameter(Valuable):  # abstract
    @staticmethod
    def getInitSettings():
        return LocalSettings()

    def __init__(self, value, settings=None):
        if settings is not None:
            if not isinstance(settings, LocalSettings):
                excmsg = ("(EnvironmentParameter) __init__, a LocalSettings "
                          "was expected for settings, got '" +
                          str(type(settings))+"'")
                raise ParameterException(excmsg)

            self.settings = settings
        else:
            self.settings = self.getInitSettings()

        read_only = self.settings.isReadOnly()
        self.settings.setReadOnly(False)

        self.setValue(value)

        if read_only:
            self.settings.setReadOnly(True)

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.settings._raiseIfReadOnly(self.__class__.__name__, "setValue")
        self.value = value

    def __str__(self):
        return str(self.getValue())

    def __repr__(self):
        return "Parameter: "+str(self.getValue())

    def enableGlobal(self):
        if isinstance(self.settings, GlobalSettings):
            return

        self.settings = GlobalSettings(read_only=self.settings.isReadOnly(),
                                       removable=self.settings.isRemovable())

    def enableLocal(self):
        if isinstance(self.settings, LocalSettings):
            return

        self.settings = LocalSettings(read_only=self.settings.isReadOnly(),
                                      removable=self.settings.isRemovable())

    def __hash__(self):
        value = self.getValue()
        if hasattr(value, "__iter__"):
            return hash(str(hash(tuple(value))) + str(hash(self.settings)))
        else:
            return hash(str(hash(value)) + str(hash(self.settings)))
