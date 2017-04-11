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

from pyshell.register.exception import LoaderException
from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.loader.exception import LoadException
from pyshell.register.loader.exception import UnloadException
from pyshell.register.result.command import CommandResult
from pyshell.utils.constants import SETTING_PROPERTY_READONLY
from pyshell.utils.constants import SETTING_PROPERTY_REMOVABLE
from pyshell.utils.exception import ListOfException
from pyshell.utils.exception import ParameterException
from pyshell.utils.string65 import escapeString


def _createParameter(parameter_type, parameter_name, parameter_object):
    if isinstance(parameter_object.getValue(), list):
        values = parameter_object.getValue()
        value = " ".join(escapeString(str(x)) for x in values)
    else:
        value = escapeString(str(parameter_object.getValue()))

    ins = "%s create %s %s -local_param False"
    return ins % (parameter_type, parameter_name, value)


def _removeParameter(parameter_type, parameter_name):
    ins = "%s unset %s -start_with_local False -explore_other_scope False"
    return ins % (parameter_type, parameter_name)


def _setValues(parameter_type, parameter_name, parameter_object, values):
    if isinstance(values, list):
        value = " ".join(escapeString(str(x)) for x in values)
    else:
        value = escapeString(str(values))

    return "%s set %s %s" % (parameter_type, parameter_name, value)


def _removeValues(parameter_type, parameter_name, values):
    value = " ".join(escapeString(str(x)) for x in values)
    return "%s subtract %s %s" % (parameter_type, parameter_name, value)


def _addValues(parameter_type, parameter_name, values):
    value = " ".join(escapeString(str(x)) for x in values)
    return "%s add %s %s" % (parameter_type, parameter_name, value)


def _setProperty(parameter_type, parameter_name, property_key, property_value):
    return "%s properties set %s %s %s" % (parameter_type,
                                           parameter_name,
                                           property_key,
                                           property_value)


def _computeUpdateAction(parameter_a, parameter_b):
    values_a = parameter_a.getValue()
    values_b = parameter_b.getValue()
    list_value_a = isinstance(parameter_a.getValue(), list)
    list_value_b = isinstance(parameter_b.getValue(), list)

    # compute hash
    if list_value_a:
        value_a_hash = hash(tuple(values_a))
    else:
        value_a_hash = hash(values_a)

    if list_value_b:
        value_b_hash = hash(tuple(values_b))
    else:
        value_b_hash = hash(values_b)

    # if equal, nothing to do
    if value_a_hash == value_b_hash:
        return None, None, None

    # if at least one is not a list param, use set command
    if not list_value_a or not list_value_b:
        return values_b, None, None

    # determine the common prefix values
    for common_prefix in range(0, min(len(values_a), len(values_b))):
        if values_a[common_prefix] != values_b[common_prefix]:
            common_prefix -= 1
            break

    common_prefix += 1

    # no common prefix, use set command
    if common_prefix == 0:
        return values_b, None, None

    remove_count = len(values_a) - common_prefix
    add_count = len(values_b) - common_prefix

    # use the set command if it is shorter than the combination of remove/add
    if remove_count + add_count > len(values_b):
        return values_b, None, None

    value_to_remove = None
    if remove_count > 0:
        value_to_remove = values_a[remove_count * -1:]

    value_to_add = None
    if add_count > 0:
        value_to_add = values_b[add_count * -1:]

    # remove+add commands are the most efficient methods to use
    return None, value_to_remove, value_to_add


class ParameterAbstractLoader(AbstractLoader):
    __metaclass__ = ABCMeta

    @staticmethod
    def getManagerName():
        # this raise an exception as in the old time because ABC class does not
        # seem able to manage abstract static method in a right way.
        excmsg = "(ParameterAbstractLoader) getManagerName, not implemented"
        raise LoaderException(excmsg)

    @staticmethod
    def getManager(container):
        # this raise an exception as in the old time because ABC class does not
        # seem able to manage abstract static method in a right way.
        excmsg = "(ParameterAbstractLoader) getManager, not implemented"
        raise LoaderException(excmsg)

    @classmethod
    def load(cls, profile_object, parameter_container):
        if parameter_container is None:
            excmsg = ("(%s) load, parameter container is not defined.  It is"
                      " needed to load the parameters")
            excmsg %= cls.__name__
            raise LoadException(excmsg)

        parameter_manager = cls.getManager(parameter_container)
        exceptions = ListOfException()

        # set value
        parameters = profile_object.parameter_to_set.items()
        del profile_object.parameter_to_unset[:]
        for parameter_name, parameter_object in parameters:
            ex = cls._setParameterIntoManager(parameter_manager,
                                              parameter_name,
                                              parameter_object,
                                              profile_object)

            if ex is not None:
                exceptions.addException(ex)

        # raise error list
        if exceptions.isThrowable():
            raise exceptions

    @classmethod
    def _setParameterIntoManager(cls,
                                 parameter_manager,
                                 parameter_name,
                                 parameter_object,
                                 profile_object):
        """
            this method load a parameter attached to this addon into the
            corresponding manager
        """
        exist = parameter_manager.hasParameter(parameter_name,
                                               perfect_match=True,
                                               local_param=False,
                                               explore_other_scope=False)

        if exist:
            other_addon = parameter_manager.getLoaderName()
            excmsg = ("(%s) setValueTo, fail to set value with key '%s': key "
                      "already exists in addon '%s'")
            excmsg %= (cls.__name__, str(parameter_name), str(other_addon),)
            return LoadException(excmsg)

        try:
            root_profile = profile_object.getRootProfile()
            addon_name = root_profile.getAddonInformations().getName()
            parameter_manager.setParameter(parameter_name,
                                           parameter_object.clone(),
                                           local_param=False,
                                           origin_group=addon_name,
                                           freeze=True)
            profile_object.parameter_to_unset.append(parameter_name)
        except ParameterException as pe:
            excmsg = ("(" + cls.__name__ + ") setValueTo, fail to set "
                      "value with key '" + str(parameter_name) + "': " +
                      str(pe))
            return LoadException(excmsg)

    @classmethod
    def unload(cls, profile_object, parameter_container):
        if parameter_container is None:
            excmsg = ("(%s) unload, parameter container is not defined.  It "
                      "is needed to unload the parameters")
            excmsg %= cls.__name__
            raise UnloadException(excmsg)

        parameter_manager = cls.getManager(parameter_container)
        exceptions = ListOfException()

        # get addon name
        root_profile = profile_object.getRootProfile()
        addon_name = root_profile.getAddonInformations().getName()
        parameter_list = parameter_manager.getGroupNodes(addon_name)

        instruction_list = []
        # remove object set
        for parameter_name in profile_object.parameter_to_unset:
            original_parameter = profile_object.parameter_to_set[
                parameter_name]
            ex = cls._unsetParameterFromManager(parameter_manager,
                                                parameter_name,
                                                original_parameter,
                                                addon_name,
                                                instruction_list)

            if ex is not None:
                exceptions.addException(ex)

        for parameter_node in parameter_list:
            if not parameter_node.hasGlobalVar():
                # nothing we can do, there is no other copy of what was
                # stored in this node.
                continue
            try:
                param = parameter_manager.unsetParameter(
                    parameter_node.string_key,
                    local_param=False,
                    explore_other_scope=False,
                    force=True,
                    origin_group=addon_name,
                    unfreeze=True)  # try to unfreeze if frozen
            except ParameterException as pe:
                excmsg = ("(%s) unsetValueTo, fail to unset value with key "
                          "'%s': %s")
                excmsg %= (cls.__name__,
                           str(parameter_node.string_key),
                           str(pe),)
                exceptions.addException(UnloadException(excmsg))
                continue

            if not param.settings.isTransient():
                cls._createParameter(parameter_node.string_key,
                                     param,
                                     instruction_list)

        parameter_manager.clearFrozenNode(addon_name)

        # remove empty trailer if any
        while len(instruction_list) > 0 and instruction_list[-1] == "":
            del instruction_list[-1]

        if len(instruction_list) > 0:
            result = CommandResult(
                command_list=instruction_list,
                section_name="SECTION ABOUT %s" % cls.getManagerName(),
                addons_set=set(["pyshell.addons.parameter"]))
            root_profile.postResult(cls, result)

        # raise error list
        if exceptions.isThrowable():
            raise exceptions

    @classmethod
    def _unsetParameterFromManager(cls,
                                   parameter_manager,
                                   parameter_name,
                                   original_parameter_object,
                                   addon_name,
                                   instruction_list):
        """
            this method remove a parameter attached to the current
            addon from its corresponding manager, then decide to
            generate the instruction to delete, update it or
            create it at next load.
        """
        # still exist ?
        exist = parameter_manager.hasParameter(parameter_name,
                                               perfect_match=True,
                                               local_param=False,
                                               explore_other_scope=False)
        if not exist:
            if not original_parameter_object.settings.isTransient():
                cls._deleteParameter(parameter_name,
                                     original_parameter_object,
                                     instruction_list)
            return

        try:
            updated_parameter_object = parameter_manager.unsetParameter(
                parameter_name,
                local_param=False,
                explore_other_scope=False,
                force=True,
                origin_group=addon_name,
                unfreeze=True)
        except ParameterException as pe:
            excmsg = "(%s) unsetValueTo, fail to unset value with key '%s': %s"
            excmsg %= (cls.__name__, str(parameter_name), str(pe),)
            return UnloadException(excmsg)

        if hash(original_parameter_object) != hash(updated_parameter_object):
            if not updated_parameter_object.settings.isTransient():
                cls._updateParameter(parameter_name,
                                     original_parameter_object,
                                     updated_parameter_object,
                                     instruction_list)

    @classmethod
    def _deleteParameter(cls,
                         parameter_name,
                         original_parameter_object,
                         instruction_list):
        """
            this method generates the instructions needed to delete a
            parameter from its corresponding manager.
        """

        manager_name = cls.getManagerName()
        if not original_parameter_object.settings.isRemovable():
            if original_parameter_object.settings.isReadOnly():
                ins = _setProperty(manager_name,
                                   parameter_name,
                                   SETTING_PROPERTY_READONLY,
                                   "False")
                instruction_list.append(ins)

            ins = _setProperty(manager_name,
                               parameter_name,
                               SETTING_PROPERTY_REMOVABLE,
                               "True")
            instruction_list.append(ins)

        ins = _removeParameter(manager_name, parameter_name)
        instruction_list.append(ins)
        instruction_list.append("")

    @classmethod
    def _updateParameter(cls,
                         parameter_name,
                         original_parameter_object,
                         updated_parameter_object,
                         instruction_list):
        """
            this method generates the instructions needed to update
            the content and the properties of a parameter
        """

        # disable readonly if needed
        manager_name = cls.getManagerName()
        original_read_only = original_parameter_object.settings.isReadOnly()
        if original_read_only:
            ins = _setProperty(manager_name,
                               parameter_name,
                               SETTING_PROPERTY_READONLY,
                               "False")
            instruction_list.append(ins)

        # update properties
        updated_read_only = cls._saveProperties(
            parameter_name,
            original_parameter_object.settings.getProperties(),
            updated_parameter_object.settings.getProperties(),
            instruction_list)

        # compute value to set, remove or add
        value_to_set, value_to_remove, value_to_add = \
            _computeUpdateAction(original_parameter_object,
                                 updated_parameter_object)

        # produce commands string
        if value_to_set is not None:
            ins = _setValues(manager_name,
                             parameter_name,
                             updated_parameter_object,
                             value_to_set)
            instruction_list.append(ins)

        if value_to_remove is not None:
            ins = _removeValues(manager_name,
                                parameter_name,
                                value_to_remove)
            instruction_list.append(ins)

        if value_to_add is not None:
            ins = _addValues(manager_name, parameter_name, value_to_add)
            instruction_list.append(ins)

        # restore readonly if needed
        # read only was already set to False at the beginning of this method
        # only need to set it if its value is True
        if ((updated_read_only is not None and updated_read_only) or
                (updated_read_only is None and original_read_only)):
            ins = _setProperty(manager_name,
                               parameter_name,
                               SETTING_PROPERTY_READONLY,
                               "True")

            instruction_list.append(ins)
        instruction_list.append("")

    @classmethod
    def _createParameter(cls,
                         parameter_name,
                         parameter_object,
                         instruction_list):
        """
            this method generates the instructions needed to create a
            parameter, its content and its properties
        """

        manager_name = cls.getManagerName()
        ins = _createParameter(manager_name,
                               parameter_name,
                               parameter_object)
        instruction_list.append(ins)

        # save only properties with a state different from the initial state
        properties = parameter_object.settings.getProperties()
        original_settings = type(parameter_object.settings)()
        original_settings.getGlobalFromLocal()
        initial_properties = original_settings.getProperties()
        read_only_value = cls._saveProperties(parameter_name,
                                              initial_properties,
                                              properties,
                                              instruction_list)

        if read_only_value is not None and read_only_value:
            ins = _setProperty(manager_name,
                               parameter_name,
                               SETTING_PROPERTY_READONLY,
                               "True")

            instruction_list.append(ins)
        instruction_list.append("")

    @classmethod
    def _saveProperties(cls,
                        parameter_name,
                        initial_properties,
                        current_properties,
                        instruction_list):
        """
            save the properties except readOnly and the properties with an
            initial state.

            return: readOnly value if it has been updated.
        """
        current_pairs = set(current_properties.items())
        initial_pairs = set(initial_properties.items())
        properties_to_save = current_pairs - initial_pairs

        manager_name = cls.getManagerName()
        read_only_value = None
        for property_key, property_value in properties_to_save:
            if property_key == SETTING_PROPERTY_READONLY:
                read_only_value = property_value
                continue

            ins = _setProperty(manager_name,
                               parameter_name,
                               property_key,
                               property_value)

            instruction_list.append(ins)

        return read_only_value
