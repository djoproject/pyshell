#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2016  Jonathan Delvaux <pyshell@djoproject.net>

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

from abc import ABCMeta, abstractmethod
from threading import Lock

from tries import multiLevelTries

from pyshell.system.parameter.abstract import Parameter
from pyshell.utils.abstract.flushable import Flushable
from pyshell.utils.exception import ParameterException
from pyshell.utils.string65 import isString
from pyshell.utils.synchronized import synchronous


class AbstractParentManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getCurrentId(self):
        pass

    @abstractmethod
    def getDefaultGroupName(self):
        pass

    @abstractmethod
    def checkForSetGlobalParameter(self, group_name, loader_name):
        pass

    @abstractmethod
    def checkForUnsetGlobalParameter(self, group_name, loader_name):
        pass


def isAValidStringPath(string_path):
    if not isString(string_path):
        return False, "invalid string_path, a string was expected, got '" + \
            str(type(string_path)) + "'"

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
    def __init__(self, string_key):
        self.global_var = None
        self.local_var = None
        self.origin_group = None
        self.starting_hash = None
        self.string_key = string_key
        self.mltries_key = string_key.split(".")

    def hasLocalVar(self, key):
        return self.local_var is not None and key in self.local_var

    def hasGlobalVar(self):
        return self.global_var is not None

    def getLocalVar(self, key):
        if self.local_var is None:
            raise KeyError(key)

        return self.local_var[key]

    def getGlobalVar(self):
        if self.global_var is None:
            excmsg = "(%s) getGlobalVar, no global var defined"
            excmsg %= self.__class__.__name__
            raise ParameterException(excmsg)

        return self.global_var

    def setLocalVar(self, key, param):
        param.enableLocal()

        if self.local_var is None:
            self.local_var = {}
        elif key in self.local_var:
            local_var = self.local_var[key]
            if local_var.settings.isReadOnly():
                excmsg = ("(%s) setLocalVar, can not set the parameter '%s' "
                          "because a parameter with this name already exist "
                          "and is not editable")
                excmsg %= (self.__class__.__name__, self.string_key,)
                raise ParameterException(excmsg)

        self.local_var[key] = param

    def setGlobalVar(self, param, origin_group, freeze=False):
        # global var is set AND readonly
        if (self.global_var is not None and
           self.global_var.settings.isReadOnly()):
            excmsg = ("(%s) setGlobalVar, can not set the parameter '%s' "
                      "because a parameter with this name already exist "
                      "and is not editable")
            excmsg %= (self.__class__.__name__, self.string_key,)
            raise ParameterException(excmsg)

        # global var is already frozen AND ask for freezing again
        if self.isFrozen() and freeze:
            excmsg = ("(%s) setGlobalVar, can not freeze starting point "
                      "on parameter '%s' , it is already frozen.")
            excmsg %= (self.__class__.__name__, self.string_key,)
            raise ParameterException(excmsg)

        # a global var must always be associated to a not None group name
        if origin_group is None:
            excmsg = ("(%s) setGlobalVar, can not use parameter '%s' as "
                      "global parameter, group origin is not defined")
            excmsg %= (self.__class__.__name__, self.string_key,)
            raise ParameterException(excmsg)

        # if an group name is already associated (frozen or global var set),
        # another group name can not steal the global var
        # steal the group
        if self.origin_group is not None and self.origin_group != origin_group:
            excmsg = ("(%s) setGlobalVar, the origin group '%s' is already "
                      "associated to the parameter '%s', can not associate the"
                      " group name '%s'")
            excmsg %= (self.__class__.__name__,
                       self.origin_group,
                       self.string_key,
                       origin_group)
            raise ParameterException(excmsg)

        param.enableGlobal()

        if self.isFrozen():
            param.settings.setStartingPoint(self.starting_hash)
        else:
            param.settings.setStartingPoint(hash(param))
            self.origin_group = origin_group
            if freeze:
                self.starting_hash = param.settings.startingHash

        self.global_var = param

    def unsetGlobalVar(self, force=False):
        if self.global_var is not None and not force:
            if not self.global_var.settings.isRemovable():
                excmsg = "(%s) unsetParameter, parameter '%s' is not removable"
                excmsg %= (self.__class__.__name__, self.string_key,)
                raise ParameterException(excmsg)

        if not self.isFrozen():
            self.origin_group = None

        self.global_var = None

    def unsetLocalVar(self, key, force=False):
        if self.local_var is not None and key in self.local_var:
            local_var = self.local_var[key]
            if not local_var.settings.isRemovable() and not force:
                excmsg = ("(%s) unsetParameter, local parameter '%s' is not "
                          "removable")
                excmsg %= (self.__class__.__name__, self.string_key,)
                raise ParameterException(excmsg)

            del self.local_var[key]

    def isRemovable(self):
        return (self.global_var is None and
                (self.local_var is None or len(self.local_var) == 0) and
                self.starting_hash is None)

    def isFrozen(self):
        return self.starting_hash is not None

    def unfreeze(self, origin_group):
        if not self.isFrozen():
            return

        if self.origin_group != origin_group:
            excmsg = ("(%s) unfreeze, try to unfreeze with an incorrect key: "
                      "'%s'")
            excmsg %= (self.__class__.__name__, origin_group,)
            raise ParameterException(excmsg)

        if self.global_var is None:
            self.origin_group = None

        self.starting_hash = None

    def getGroupOrigin(self):
        return self.origin_group


class AbstractParameterManager(Flushable):
    __metaclass__ = ABCMeta

    def __init__(self, parent=None):
        self._internalLock = Lock()
        self.mltries = multiLevelTries()

        # hold the nodes for the current thread
        self.threadLocalVar = {}

        # hold the nodes for each groups
        self.groupGlobalVar = {}

        if not isinstance(parent, AbstractParentManager):
            excmsg = ("(%s) __init__, expect an instance of "
                      "AbstractParentManager, got '%s'")
            excmsg %= (self.__class__.__name__, str(type(parent)),)
            raise ParameterException(excmsg)

        self.parent = parent

    @staticmethod
    def getLoaderName():
        # this raise an exception as in the old time because ABC class does not
        # seem able to manage abstract static method in a right way.
        excmsg = "(ParameterManager) getLoaderName, not implemented"
        raise ParameterException(excmsg)

    def _getAdvanceResult(self,
                          meth_name,
                          string_path,
                          raise_if_not_found=True,
                          raise_if_ambiguous=True,
                          perfect_match=False):

        # prepare and check path
        state, result = isAValidStringPath(string_path)

        if not state:
            excmsg = "(%s) %s, %s"
            excmsg %= (self.__class__.__name__, str(meth_name), result,)
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

            existing_path = _buildExistingPathFromError(path, advanced_result)
            existing_path = ".".join(existing_path)

            excmsg = ("(%s) %s, key '%s' is ambiguous for path '%s', possible "
                      "value are: '%s'")
            excmsg %= (self.__class__.__name__,
                       str(meth_name),
                       str(path[index_of_ambiguous_key]),
                       existing_path,
                       ",".join(possible_value),)

            raise ParameterException(excmsg)

        if raise_if_not_found and not advanced_result.isValueFound():
            index_not_found = advanced_result.getTokenFoundCount()
            existing_path = _buildExistingPathFromError(path, advanced_result)
            existing_path = ".".join(existing_path)
            excmsg = "(%s) %s, key '%s' is unknown for path '%s'"
            excmsg %= (self.__class__.__name__,
                       str(meth_name),
                       str(path[index_not_found]),
                       existing_path,)

            raise ParameterException(excmsg)

        return advanced_result

    @abstractmethod
    def getAllowedType(self):
        pass

    def isAnAllowedType(self, value):  # XXX to override if needed
        # why not using isinstance ? because children class are not allowed.
        # WARNING: autopep8 seems to replace the line with isinstance...
        # valid: return type(value) is self.getAllowedType()
        # invalid: return isinstance(value, self.getAllowedType())
        return type(value) is self.getAllowedType()

    def _extractParameter(self, value):
        if self.isAnAllowedType(value):
            return value

        if isinstance(value, Parameter):
            excmsg = ("(%s) _extractParameter, can not use an object of type "
                      "'%s' in this manager")
            excmsg %= (self.__class__.__name__, str(type(value)),)
            raise ParameterException(excmsg)

        # try to instanciate parameter, may raise if invalid type
        return self.getAllowedType()(value)

    @synchronous()
    def setParameter(self,
                     string_path,
                     param,
                     local_param=True,
                     origin_group=None,
                     freeze=False):
        param = self._extractParameter(param)

        if local_param and freeze:
            excmsg = ("(%s) setParameter, freezing paramer '%s' is not allowed"
                      " for local parameter")
            excmsg %= (self.__class__.__name__, string_path,)
            raise ParameterException(excmsg)

        # check safety and existing
        advanced_result = self._getAdvanceResult("setParameter",
                                                 string_path,
                                                 False,
                                                 False,
                                                 True)
        creation_mode = not advanced_result.isValueFound()

        if creation_mode:
            parameter_node = ParameterTriesNode(string_path)
        else:
            parameter_node = advanced_result.getValue()

        if local_param:
            key = self.parent.getCurrentId()
            parameter_node.setLocalVar(key, param)

            if key not in self.threadLocalVar:
                self.threadLocalVar[key] = set()

            self.threadLocalVar[key].add(parameter_node)
        else:
            if origin_group is None:
                origin_group = self.parent.getDefaultGroupName()

            old_group_origin = parameter_node.getGroupOrigin()

            if (old_group_origin is not None and
               old_group_origin != origin_group):
                pass  # TODO (issue #83) raise, stealing is forbidden

            self.parent.checkForSetGlobalParameter(origin_group,
                                                   self.getLoaderName())

            parameter_node.setGlobalVar(param,
                                        origin_group=origin_group,
                                        freeze=freeze)

            if origin_group not in self.groupGlobalVar:
                self.groupGlobalVar[origin_group] = set()

            self.groupGlobalVar[origin_group].add(parameter_node)

        if creation_mode:
            self.mltries.insert(parameter_node.mltries_key, parameter_node)

        return param

    @synchronous()
    def getParameter(self,
                     string_path,
                     perfect_match=False,
                     local_param=True,
                     explore_other_scope=True):

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
                    key = self.parent.getCurrentId()
                    if parameter_node.hasLocalVar(key):
                        return parameter_node.getLocalVar(key)

                    if not explore_other_scope:
                        break
                else:
                    if parameter_node.hasGlobalVar():
                        return parameter_node.getGlobalVar()

                    if not explore_other_scope:
                        break

                local_param = not local_param

        return None

    @synchronous()
    def hasParameter(self,
                     string_path,
                     raise_if_ambiguous=True,
                     perfect_match=False,
                     local_param=True,
                     explore_other_scope=True):

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
                    key = self.parent.getCurrentId()

                    if parameter_node.hasLocalVar(key):
                        return True

                    if not explore_other_scope:
                        return False
                else:
                    if parameter_node.hasGlobalVar():
                        return True

                    if not explore_other_scope:
                        return False

                local_param = not local_param

        return False

    @synchronous()
    def unsetParameter(self,
                       string_path,
                       local_param=True,
                       explore_other_scope=True,
                       force=False,
                       origin_group=None,
                       unfreeze=False):

        if local_param and not explore_other_scope and unfreeze:
            excmsg = ("(%s) setParameter, unfreezing paramer '%s' is not "
                      "allowed for local parameter")
            excmsg %= (self.__class__.__name__, string_path,)
            raise ParameterException(excmsg)

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
                    key = self.parent.getCurrentId()

                    if not parameter_node.hasLocalVar(key):
                        if not explore_other_scope:
                            excmsg = ("(%s) unsetParameter, unknown local "
                                      "parameter '%s'")
                            excmsg %= (self.__class__.__name__,
                                       parameter_node.string_key,)
                            raise ParameterException(excmsg)

                        local_param = not local_param
                        continue

                    param = parameter_node.getLocalVar(key)
                    parameter_node.unsetLocalVar(key, force)

                    # remove from thread local list
                    self.threadLocalVar[key].remove(parameter_node)
                    if len(self.threadLocalVar[key]) == 0:
                        del self.threadLocalVar[key]

                    # remove from mltries
                    if parameter_node.isRemovable():
                        self.mltries.remove(parameter_node.mltries_key)

                    return param
                else:
                    if not parameter_node.hasGlobalVar():
                        if not explore_other_scope:
                            excmsg = ("(%s) unsetParameter, unknown global "
                                      "parameter '%s'")
                            excmsg %= (self.__class__.__name__,
                                       parameter_node.string_key,)
                            raise ParameterException(excmsg)

                        local_param = not local_param
                        continue

                    if origin_group is None:
                        origin_group = self.parent.getDefaultGroupName()

                    self.parent.checkForUnsetGlobalParameter(
                        origin_group,
                        self.getLoaderName())
                    actual_origin_group = parameter_node.getGroupOrigin()

                    if unfreeze and origin_group != actual_origin_group:
                        excmsg = ("(%s) unsetParameter, incorrect origin_group"
                                  " provided to unfreeze the global parameter "
                                  "'%s', got '%s', expected '%s'")
                        excmsg %= (self.__class__.__name__,
                                   parameter_node.string_key,
                                   origin_group,
                                   actual_origin_group)
                        raise ParameterException(excmsg)

                    param = parameter_node.getGlobalVar()
                    parameter_node.unsetGlobalVar(force)

                    if unfreeze:
                        parameter_node.unfreeze(origin_group)

                    if not parameter_node.isFrozen():
                        self.groupGlobalVar[actual_origin_group].remove(
                            parameter_node)

                        if len(self.groupGlobalVar[actual_origin_group]) == 0:
                            del self.groupGlobalVar[actual_origin_group]

                    if parameter_node.isRemovable():
                        self.mltries.remove(parameter_node.mltries_key)

                    return param

            excmsg = "(%s) unsetParameter, unknown parameter  '%s'"
            excmsg %= (self.__class__.__name__, string_path,)
            raise ParameterException(excmsg)

    @synchronous()
    def flush(self):
        # flush the Variable For This Thread
        key = self.parent.getCurrentId()
        # do we have recorded some variables for this thread ?
        if key in self.threadLocalVar:
            # no error possible, missing value or invalid type is possible
            # here, because of the process in set/unset
            for parameter_node in self.threadLocalVar[key]:
                parameter_node.unsetLocalVar(key)

                if parameter_node.isRemovable():
                    # can not raise, because every path exist
                    self.mltries.remove(parameter_node.mltries_key)

            del self.threadLocalVar[key]

    @synchronous()
    def buildDictionnary(self,
                         string_path,
                         local_param=True,
                         explore_other_scope=True):
        state, result = isAValidStringPath(string_path)

        if not state:
            excmsg = "(%s) buildDictionnary, %s"
            excmsg %= (self.__class__.__name__, result,)
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
                        key = self.parent.getCurrentId()

                    if parameter_node.hasLocalVar(key):
                        local_var = parameter_node.getLocalVar(key)
                        to_ret[parameter_node.string_key] = local_var
                        break

                    if not explore_other_scope:
                        break
                else:
                    if parameter_node.hasGlobalVar():
                        global_var = parameter_node.getGlobalVar()
                        to_ret[parameter_node.string_key] = global_var
                        break

                    if not explore_other_scope:
                        break

                local_param_tmp = not local_param_tmp

        return to_ret

    @synchronous()
    def getAssociatedGroup(self, string_path):
        advanced_result = self._getAdvanceResult("hasParameter",
                                                 string_path,
                                                 False,
                                                 True,
                                                 True)

        if not advanced_result.isValueFound():
            return None

        parameter_node = advanced_result.getValue()
        return parameter_node.getGroupOrigin()

    @synchronous()
    def getGroupNodes(self, origin_group):
        if origin_group in self.groupGlobalVar:
            return tuple(self.groupGlobalVar[origin_group])

        return ()

    @synchronous()
    def clearFrozenNode(self, origin_group):
        if origin_group not in self.groupGlobalVar:
            return

        group_node_set = self.groupGlobalVar[origin_group]
        node_list = list(group_node_set)

        for node in node_list:
            node.unfreeze(origin_group)

            if not node.hasGlobalVar():
                group_node_set.remove(node)

            if node.isRemovable():
                self.mltries.remove(node.mltries_key)

        if len(group_node_set) == 0:
            del self.groupGlobalVar[origin_group]
