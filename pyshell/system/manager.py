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

from threading import Lock

from tries import multiLevelTries

from pyshell.system.container import AbstractParameterContainer
from pyshell.system.container import DEFAULT_DUMMY_PARAMETER_CONTAINER
from pyshell.system.parameter import Parameter
from pyshell.utils.abstract.flushable import Flushable
from pyshell.utils.exception import ParameterException
from pyshell.utils.string import isString
from pyshell.utils.synchronized import synchronous


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
        self.origin_addon = None
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
            excmsg = "(ParameterTriesNode) getGlobalVar, no global var defined"
            raise ParameterException(excmsg)

        return self.global_var

    def setLocalVar(self, key, param):
        param.enableLocal()

        if self.local_var is None:
            self.local_var = {}
        elif key in self.local_var:
            local_var = self.local_var[key]
            if local_var.settings.isReadOnly():
                excmsg = ("(ParameterTriesNode) setLocalVar, can not set the "
                          "parameter '%s' because a parameter with this name "
                          "already exist and is not "
                          "editable" % self.string_key)
                raise ParameterException(excmsg)

        self.local_var[key] = param

    def setGlobalVar(self, param, origin_addon=None, freeze=False):
        if (self.global_var is not None and
                self.global_var.settings.isReadOnly()):
            excmsg = ("(ParameterTriesNode) setGlobalVar, can not set the "
                      "parameter '%s' because a parameter with this name "
                      "already exist and is not editable" % self.string_key)
            raise ParameterException(excmsg)

        param.enableGlobal()

        if self.isFrozen():
            if freeze:
                excmsg = ("(ParameterTriesNode) setGlobalVar, can not freeze "
                          "starting point on parameter '%s' , it is already "
                          "frozen." % self.string_key)
                raise ParameterException(excmsg)

            if self.origin_addon != origin_addon:
                excmsg = ("(ParameterTriesNode) setGlobalVar, parameter '%s' "
                          "is frozen and the new origin addon is different "
                          "from the frozen one" % self.string_key)
                raise ParameterException(excmsg)

            param.settings.setStartingPoint(self.starting_hash)
        else:
            if origin_addon is None:
                excmsg = ("(ParameterTriesNode) setGlobalVar, can not use "
                          "parameter '%s' as global parameter, no addon "
                          "origin is set" % self.string_key)
                raise ParameterException(excmsg)

            param.settings.setStartingPoint(hash(param))
            self.origin_addon = origin_addon
            if freeze:
                self.starting_hash = param.settings.startingHash

        self.global_var = param

    def unsetGlobalVar(self, force=False):
        if self.global_var is not None and not force:
            if not self.global_var.settings.isRemovable():
                excmsg = ("(ParameterTriesNode) unsetParameter, parameter '%s'"
                          " is not removable" % self.string_key)
                raise ParameterException(excmsg)

        if not self.isFrozen():
            self.origin_addon = None

        self.global_var = None

    def unsetLocalVar(self, key, force=False):
        if self.local_var is not None and key in self.local_var:
            local_var = self.local_var[key]
            if not local_var.settings.isRemovable() and not force:
                excmsg = ("(ParameterTriesNode) unsetParameter, local "
                          "parameter '%s' is not removable" % self.string_key)
                raise ParameterException(excmsg)

            del self.local_var[key]

    def isRemovable(self):
        return (self.global_var is None and
                (self.local_var is None or len(self.local_var) == 0) and
                self.starting_hash is None)

    def isFrozen(self):
        return self.starting_hash is not None

    def unfreeze(self, origin_addon):
        if not self.isFrozen():
            return

        if self.origin_addon != origin_addon:
            excmsg = ("(ParameterTriesNode) unfreeze, try to unfreeze with "
                      "the wrong key: '%s'" % origin_addon)
            raise ParameterException(excmsg)

        self.starting_hash = None

    def getAddonOrigin(self):
        return self.origin_addon


class ParameterManager(Flushable):
    # TODO for the class name in the exception use self.__class__.__name__
    # TODO should this class be abstract ?

    def __init__(self, parent=None):
        self._internalLock = Lock()
        self.mltries = multiLevelTries()

        # hold the nodes for the current thread
        self.threadLocalVar = {}

        # hold the nodes for each addons
        self.addonGlobalVar = {}

        if parent is None:
            self.parentContainer = DEFAULT_DUMMY_PARAMETER_CONTAINER
        else:
            if not isinstance(parent, AbstractParameterContainer):
                excmsg = ("(ParameterManager) __init__, expect an instance of "
                          "AbstractParameterContainer, got '" +
                          str(type(parent)) + "'")
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
            excmsg = "(ParameterManager) " + str(meth_name) + ", " + result
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
            excmsg = ("(ParameterManager) " + str(meth_name) + ", key '" +
                      str(path[index_of_ambiguous_key]) + "' is ambiguous for"
                      " path '" + existing_path + "', possible value are: '" +
                      ",".join(possible_value) + "'")
            raise ParameterException(excmsg)

        if raise_if_not_found and not advanced_result.isValueFound():
            index_not_found = advanced_result.getTokenFoundCount()
            existing_path = ".".join(
                _buildExistingPathFromError(path, advanced_result))
            excmsg = ("(ParameterManager) " + str(meth_name) + ", key '" +
                      str(path[index_not_found]) + "' is unknown for path '" +
                      existing_path + "'")
            raise ParameterException(excmsg)

        return advanced_result

    def getAllowedType(self):  # XXX to override if needed
        return Parameter

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
            excmsg = ("(ParameterManager) _extractParameter, can not use an "
                      "object of type '" + str(type(value)) + "' in this "
                      "manager")
            raise ParameterException(excmsg)

        # try to instanciate parameter, may raise if invalid type
        return self.getAllowedType()(value)

    @synchronous()
    def setParameter(self,
                     string_path,
                     param,
                     local_param=True,
                     origin_addon=None,
                     freeze=False):
        param = self._extractParameter(param)

        if local_param and freeze:
            excmsg = ("(ParameterManager) setParameter, freezing paramer '%s'"
                      " is not allowed for local parameter" % string_path)
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
            key = self.parentContainer.getCurrentId()
            parameter_node.setLocalVar(key, param)

            if key not in self.threadLocalVar:
                self.threadLocalVar[key] = set()

            self.threadLocalVar[key].add(parameter_node)
        else:
            if origin_addon is None:
                # TODO should be in constant
                origin_addon = "pyshell.addons.system"

            old_addon_origin = parameter_node.getAddonOrigin()
            parameter_node.setGlobalVar(param,
                                        origin_addon=origin_addon,
                                        freeze=freeze)

            # TODO (issue #83) an addon should not be able to steal a parameter
            # because of the new politic, this is now forbidden
            if (old_addon_origin is not None and
                    old_addon_origin != origin_addon):
                self.addonGlobalVar[old_addon_origin].remove(parameter_node)

                if len(self.addonGlobalVar[old_addon_origin]) == 0:
                    del self.addonGlobalVar[old_addon_origin]

            if origin_addon not in self.addonGlobalVar:
                self.addonGlobalVar[origin_addon] = set()

            self.addonGlobalVar[origin_addon].add(parameter_node)

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
                    key = self.parentContainer.getCurrentId()
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
                    key = self.parentContainer.getCurrentId()

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
                       origin_addon=None,
                       unfreeze=False):

        if local_param and not explore_other_scope and unfreeze:
            excmsg = ("(ParameterManager) setParameter, unfreezing paramer "
                      "'%s' is not allowed for local parameter" % string_path)
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
                    key = self.parentContainer.getCurrentId()

                    if not parameter_node.hasLocalVar(key):
                        if not explore_other_scope:
                            excmsg = ("(ParameterManager) unsetParameter, "
                                      "unknown local parameter '" +
                                      parameter_node.string_key + "'")
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
                            excmsg = ("(ParameterManager) unsetParameter, "
                                      "unknown global parameter '" +
                                      parameter_node.string_key + "'")
                            raise ParameterException(excmsg)

                        local_param = not local_param
                        continue

                    if origin_addon is None:
                        # TODO should be in constant
                        origin_addon = "pyshell.addons.system"

                    # TODO check origin_addon provided
                    #   if uncheck is True

                    actual_origin_addon = parameter_node.getAddonOrigin()
                    param = parameter_node.getGlobalVar()
                    parameter_node.unsetGlobalVar(force)

                    if unfreeze:
                        parameter_node.unfreeze(origin_addon)

                    if not parameter_node.isFrozen():
                        self.addonGlobalVar[actual_origin_addon].remove(
                            parameter_node)

                        if len(self.addonGlobalVar[actual_origin_addon]) == 0:
                            del self.addonGlobalVar[actual_origin_addon]

                    if parameter_node.isRemovable():
                        self.mltries.remove(parameter_node.mltries_key)

                    return param

            excmsg = ("(ParameterManager) unsetParameter, unknown parameter "
                      " '%s'" % string_path)
            raise ParameterException(excmsg)

    @synchronous()
    def flush(self):
        # flush the Variable For This Thread
        key = self.parentContainer.getCurrentId()
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
            excmsg = "(ParameterManager) buildDictionnary, " + result
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
    def getAssociatedAddon(self, string_path):
        advanced_result = self._getAdvanceResult("hasParameter",
                                                 string_path,
                                                 False,
                                                 True,
                                                 True)

        if not advanced_result.isValueFound():
            return None

        parameter_node = advanced_result.getValue()
        return parameter_node.getAddonOrigin()

    @synchronous()
    def getAddonNodes(self, origin_addon):
        if origin_addon in self.addonGlobalVar:
            return tuple(self.addonGlobalVar[origin_addon])

        return ()

    @synchronous()
    def clearFrozenNode(self, origin_addon):
        if origin_addon not in self.addonGlobalVar:
            return

        addon_node_set = self.addonGlobalVar[origin_addon]
        node_list = list(addon_node_set)

        for node in node_list:
            node.unfreeze(origin_addon)

            if not node.hasGlobalVar():
                addon_node_set.remove(node)

            if node.isRemovable():
                self.mltries.remove(node.mltries_key)

        if len(addon_node_set) == 0:
            del self.addonGlobalVar[origin_addon]
