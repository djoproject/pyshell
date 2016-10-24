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

from abc import ABCMeta

from pyshell.loader.abstractloader import AbstractLoader
from pyshell.loader.exception import LoadException
from pyshell.loader.exception import RegisterException
from pyshell.loader.exception import UnloadException
from pyshell.loader.file import FileLoader
from pyshell.loader.masterloader import MasterLoader
from pyshell.loader.utils import getRootLoader
from pyshell.system.manager import isAValidStringPath
from pyshell.utils.exception import ListOfException
from pyshell.utils.exception import ParameterException
from pyshell.utils.parsing import escapeString


def _localGetAndInitCallerModule(loader_class, profile=None):
    master = getRootLoader(class_definition=MasterLoader)
    return master.getOrCreateLoader(loader_class, profile)


def setLoadPriority(value, loader_class, profile=None):
    try:
        priority = int(value)
    except ValueError:
        excmsg = ("(ParameterLoader) setLoadPriority an integer value"
                  " was expected for the argument value, got '" +
                  str(type(value))+"'")
        raise RegisterException(excmsg)

    loader = _localGetAndInitCallerModule(loader_class, profile)
    loader.load_priority = priority


def setUnloadPriority(value, loader_class, profile=None):
    try:
        priority = int(value)
    except ValueError:
        excmsg = ("(ParameterLoader) setUnloadPriority an integer value"
                  " was expected for the argument value, got '" +
                  str(type(value))+"'")
        raise RegisterException(excmsg)

    loader = _localGetAndInitCallerModule(loader_class, profile)
    loader.unload_priority = priority


def registerSet(parameter_name,
                obj,
                loader_class,
                expected_class,
                profile=None):
    # test parameter_name
    state, result = isAValidStringPath(parameter_name)
    if not state:
        raise RegisterException("(Loader) registerSetValue, "+result)

    # check typ if not None
    if not isinstance(obj, expected_class):
        # TODO try to instanciate expected_class before to raise

        excmsg = ("(Loader) registerSetValue, obj must be an instance of " +
                  str(expected_class.__name__))
        raise RegisterException(excmsg)

    loader = _localGetAndInitCallerModule(loader_class, profile)
    loader.parameter_to_set[parameter_name] = obj


class ParameterAbstractLoader(AbstractLoader):
    __metaclass__ = ABCMeta
    
    def __init__(self, parent, manager_name):
        AbstractLoader.__init__(self, parent)

        self.parameter_to_set = {}
        self.parameter_to_unset = []
        self.instruction_list = None

        self.manager_name = manager_name

    def load(self, parameter_container=None, profile=None):
        del self.parameter_to_unset[:]
        AbstractLoader.load(self, parameter_container, profile)

        if parameter_container is None:
            # TODO how this case is managed in the other loader?
            # container should make the check et container should
            # never be None at this point.
            return  # TODO shouldn't raise ?

        if not hasattr(parameter_container, self.manager_name):
            # TODO question: create the manager ?
            excmsg = ("(ParamaterLoader) load, parameter container does not"
                      " have the attribute '"+str(self.manager_name)+"'")
            raise LoadException(excmsg)

        parameter_manager = getattr(parameter_container, self.manager_name)
        exceptions = ListOfException()

        # set value
        for parameter_name, parameter_object in self.parameter_to_set.items():
            ex = self._setValueTo(parameter_manager,
                                  parameter_name,
                                  parameter_object)

            if ex is not None:
                exceptions.append(ex)

        # raise error list
        if exceptions.isThrowable():
            raise exceptions

    def _setValueTo(self, parameter_manager, parameter_name, parameter_object):
        exist = parameter_manager.hasParameter(parameter_name,
                                               perfect_match=True,
                                               local_param=False,
                                               explore_other_scope=False)

        if exist:
            excmsg = ("(ParamaterLoader) setValueTo, fail to set value"
                      " with key '"+str(parameter_name)+"': key already "
                      "exists")
            # TODO get foreign addon for this param and add it on error msg
            # and also give the name of the current addon if possible
            return LoadException(excmsg)

        try:
            parameter_manager.setParameter(parameter_name,
                                           parameter_object.clone(),
                                           local_param=False,
                                           addon_loader=None,  # TODO set addon origin
                                           freeze=True)
            self.parameter_to_unset.append(parameter_name)
        except ParameterException as pe:
            excmsg = ("(ParamaterLoader) setValueTo, fail to set value with "
                      "key '"+str(parameter_name)+"': "+str(pe))
            return LoadException(excmsg)

    def unload(self, parameter_container=None, profile=None):
        AbstractLoader.unload(self, parameter_container, profile)

        if parameter_container is None:
            # TODO see the same question in load method
            return  # TODO shouldn't raise ?

        if not hasattr(parameter_container, self.manager_name):
            excmsg = ("(ParamaterLoader) unload, parameter container does "
                      "not have the attribute '"+str(self.manager_name)+"'")
            raise UnloadException(excmsg)

        parameter_manager = getattr(parameter_container, self.manager_name)
        exceptions = ListOfException()

        # remove object set
        for parameter_name in self.parameter_to_unset:
            original_parameter = self.parameter_to_set[parameter_name]
            ex = self._unsetParameterFromManager(parameter_manager,
                                                 parameter_name,
                                                 original_parameter)

            if ex is not None:
                exceptions.append(ex)

        if self.parent is not None:
            parameter_list = parameter_manager.getLoaderNodes(
                self.parent.addon_name)
            for parameter_name in parameter_list:
                try:
                    param = parameter_manager.unsetParameter(
                        parameter_name,
                        local_param=False,
                        explore_other_scope=False)
                except ParameterException as pe:
                    excmsg = ("(ParamaterLoader) unsetValueTo, fail to unset value"
                              " with key '"+str(parameter_name)+"': "+str(pe))
                    exceptions.append(UnloadException(excmsg))
                    continue

                self._createParameter(parameter_name, param)

            parameter_manager.clearFrozenNode(self.parent.addon_name)

            self.saveCommands(section_name="parameter %s" % self.manager_name,
                              command_list=self.instruction_list,
                              addons_set=set(["pyshell.addon.parameter"]))

        # raise error list
        if exceptions.isThrowable():
            raise exceptions

    def _unsetParameterFromManager(self,
                                   parameter_manager,
                                   parameter_name,
                                   original_parameter_object):
        # still exist ?
        exist = parameter_manager.hasParameter(parameter_name,
                                               perfect_match=True,
                                               local_param=False,
                                               explore_other_scope=False)
        if not exist:
            self._deleteParameter(parameter_name, original_parameter_object)
            return

        param = None
        try:
            updated_parameter_object = parameter_manager.unsetParameter(
                parameter_name,
                local_param=False,
                explore_other_scope=False)
        except ParameterException as pe:
            excmsg = ("(ParamaterLoader) unsetValueTo, fail to unset value"
                      " with key '"+str(parameter_name)+"': "+str(pe))
            return UnloadException(excmsg)

        if hash(original_parameter_object) != hash(param):
            self._updateParameter(parameter_name,
                                  original_parameter_object,
                                  updated_parameter_object)

    def _deleteParameter(self, parameter_name, original_parameter_object):
        if not original_parameter_object.settings.isRemovable():
            if not original_parameter_object.settings.isReadOnly():
                self._addSetPropertyInstruction(parameter_name, "readOnly", "false")
            self._addSetPropertyInstruction(parameter_name, "removable", "true")

        ins = "%s unset %s -start_with_local false -explore_other_scope false"
        ins = ins % (self.manager_name, parameter_name)
        self.instruction_list.append(ins)

    def _updateParameter(self,
                         parameter_name,
                         original_parameter_object,
                         updated_parameter_object):
        # disable readonly if needed
        if updated_parameter.settings.isReadOnly():
            self._addSetPropertyInstruction(parameter_name, "readOnly", "false")

        # only the settings have been updated?
        #   only update the settings and that's all
        #
        # if the updated_object is not list, don't care if original is a list
        # or not
        #   use set commands (be careful with empty parameter)
        #   check the properties
        #
        # is it possible to produce the same result with (SEE ALGO)
        #   a remove then an add command
        #   OR a remove command only
        #   OR an add command only
        # if yes (be careful with the empty parameter on this one)
        #   save the command sequences
        #   check the properties
        #        
        # if it is not possible to create the same value list with remove/add
        # commands, then
        #   use set command
        #   check properties
        # 
        # XXX PRBLM 1: this solution need to have the remove from the end implemented (issue #106)
        #           Because if a value is common in the prefix and in the suffix, this value
        #           will be removed in the prefix and not in the suffix

        #   ALGO:
        #       * compute the common prefix between old and new values
        #       * remove every values after the common prefix
        #       * add every value after the prefix of new values
        #   Note:
        #       * if common prefix size is 0, use setValue

        # IDEA 3:

        read_only_value = self._saveProperties(
            parameter_name,
            original_parameter_object.settings,
            updated_parameter_object.settings)

        # read only was already set to False at the beginning of this method
        # only need to set it if its value is True
        if read_only_value is not None and read_only_value:
            self._addSetPropertyInstruction(parameter_name, "readOnly", read_only_value)

    def _createParameter(self, parameter_name, parameter_object):
        """
            generate the instruction string to create a new parameter
        """

        if parameter_object.isAListType():
            values = parameter_object.getValue()
            value = " ".join(escapeString(str(x)) for x in values)
            ins = ("%s create %s %s %s -no_creation_if_exist true "
                   "-local_var false")
        else:
            value = escapeString(str(parameter_object.getValue()))
            ins = ("%s create %s %s %s -is_list false "
                   "-no_creation_if_exist true -local_var false")
        type_name = parameter_object.typ.checker.getTypeName()
        ins = ins % (self.manager_name, type_name, parameter_name, value)
        self.instruction_list.append(ins)

        # save only properties with a state different from the initial state
        properties = parameter_object.settings.getProperties()
        initial_properties = type(parameter_object.settings)().getProperties()
        read_only_value = self._saveProperties(parameter_name,
                                               initial_properties,
                                               properties)

        if read_only_value is not None:
            self._addSetPropertyInstruction(parameter_name,
                                            "readOnly",
                                            read_only_value)

    def _addSetPropertyInstruction(self,
                                     parameter_name,
                                     property_key,
                                     property_value):
        """
            generate the instruction string to save the state of a specific
            property for a specific parameter
        """
        self.instruction_list.append("%s properties set %s %s %s" %
                                     (self.manager_name,
                                      parameter_name,
                                      property_key,
                                      property_value))

    def _saveProperties(self, 
                        parameter_name,
                        initial_properties,
                        current_properties):
        """
            save the properties except readOnly and the properties with an
            initial state.
            
            return: readOnly value if it has been updated.
        """
    
        properties_to_save = set(current_properties) - set(initial_properties)

        read_only_value = None
        for property_name, property_value in properties_to_save:
            if property_name.lower() == "readonly":
                read_only_value = property_value
                continue

            self._addSetPropertyInstruction(parameter_name,
                                              property_name,
                                              property_value)

        return read_only_value
