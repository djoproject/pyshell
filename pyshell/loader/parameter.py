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

from pyshell.loader.exception import LoadException
from pyshell.loader.utils import AbstractLoader
from pyshell.loader.utils import getAndInitCallerModule
from pyshell.system.parameter import isAValidStringPath
from pyshell.utils.exception import ListOfException
from pyshell.utils.exception import ParameterException


def _localGetAndInitCallerModule(loader_class, profile=None):
    return getAndInitCallerModule(loader_class.__module__+"." +
                                  loader_class.__name__,
                                  loader_class,
                                  profile)


def setLoaderPriority(value, loader_class, profile=None):
    try:
        priority = int(value)
    except ValueError:
        excmsg = ("(ParameterLoader) setLoaderPriority an integer value"
                  " was expected for the argument value, got '" +
                  str(type(value))+"'")
        raise LoadException(excmsg)

    loader = _localGetAndInitCallerModule(loader_class, profile)
    loader.priority = priority


def registerAddValues(key, value, loader_class, sub_loader_name=None):
    # test key
    state, result = isAValidStringPath(key)
    if not state:
        raise LoadException("(ParameterLoader) registerAddValues, "+result)

    loader = _localGetAndInitCallerModule(loader_class, sub_loader_name)
    loader.value_to_add_to.append((key, value,))


def registerSet(key,
                obj,
                loader_class,
                expected_class,
                no_error_if_key_exist=False,
                override=False,
                sub_loader_name=None):
    # #test key
    state, result = isAValidStringPath(key)
    if not state:
        raise LoadException("(Loader) registerSetValue, "+result)

    # check typ si different de None
    if not isinstance(obj, expected_class):
        # TODO try to instanciate expected_class before to raise

        excmsg = ("(Loader) registerSetValue, obj must be an instance of " +
                  str(expected_class.__name__))
        raise LoadException(excmsg)

    loader = _localGetAndInitCallerModule(loader_class, sub_loader_name)
    loader.value_to_set.append((key, obj, no_error_if_key_exist, override,))


class ParameterAbstractLoader(AbstractLoader):
    def __init__(self, container_name):
        AbstractLoader.__init__(self, priority=50)
        self.value_to_add_to = []
        self.value_to_set = []

        self.value_to_unset = None
        self.value_to_remove = None  # TODO not used...

        self.container_name = container_name

    def _removeValueTo(self,
                       container,
                       key_name,
                       value_to_remove,
                       attribute_name,
                       list_of_exceptions):
        env_object = container.getParameter(key_name,
                                            perfect_match=True,
                                            local_param=False,
                                            explore_other_level=False)
        if env_object is None:
            excmsg = ("(ParamaterLoader) addValueTo, fail to add value '" +
                      str(value_to_remove)+"' to '"+str(key_name)+"': unknow "
                      "key name")
            le = LoadException(excmsg)
            list_of_exceptions.addException(le)
            return

        try:
            env_object.removeValues(value_to_remove)
        except Exception as ex:
            list_of_exceptions.addException(ex)

    def _addValueTo(self,
                    container,
                    key_name,
                    value_to_add,
                    attribute_name,
                    list_of_exceptions):
        env_object = container.getParameter(key_name,
                                            perfect_match=True,
                                            local_param=False,
                                            explore_other_level=False)
        if env_object is None:
            excmsg = ("(ParamaterLoader) addValueTo, fail to add value '" +
                      str(value_to_add)+"' to '"+str(key_name)+"': unknow key"
                      " name")
            le = LoadException(excmsg)
            list_of_exceptions.addException(le)
            return

        try:
            env_object.addValues(value_to_add)
            self.value_to_remove.append((key_name,
                                         value_to_add,
                                         attribute_name))
        except Exception as ex:
            list_of_exceptions.addException(ex)

    def _unsetValueTo(self,
                      container,
                      exist,
                      old_value,
                      key_name,
                      attribute_name,
                      value,
                      list_of_exceptions):
        # still exist ?
        env_item = container.getParameter(key_name,
                                          perfect_match=True,
                                          local_param=False,
                                          explore_other_level=False)
        if env_item is None:
            excmsg = ("(ParamaterLoader) unsetValueTo, fail to unset value "
                      "with key '"+str(key_name)+"': key does not exist")
            le = LoadException(excmsg)
            list_of_exceptions.addException(le)

        if exist:  # TODO could try to use env_item even if it is None, no ?
            # if current value is still the value loaded with this addon,
            # restore the old value
            if env_item.getValue() == value:
                env_item.setValue(old_value)
            # otherwise, the value has been updated and the item already
            # exist before the loading of this module, so do nothing
        else:
            try:
                container.unsetParameter(key_name,
                                         local_param=False,
                                         explore_other_level=False)
            except ParameterException as pe:
                excmsg = ("(ParamaterLoader) unsetValueTo, fail to unset value"
                          " with key '"+str(key_name)+"': "+str(pe))
                le = LoadException(excmsg)
                list_of_exceptions.addException(le)

    def _setValueTo(self,
                    container,
                    key_name,
                    value,
                    no_error_if_key_exist,
                    override,
                    attribute_name,
                    list_of_exceptions):
        param = container.getParameter(key_name,
                                       perfect_match=True,
                                       local_param=False,
                                       explore_other_level=False)
        exist = param is not None
        old_value = None
        if exist:
            old_value = param.getValue()
            if not override:
                if not no_error_if_key_exist:
                    excmsg = ("(ParamaterLoader) setValueTo, fail to set value"
                              " with key '"+str(key_name)+"': key already "
                              "exists")
                    le = LoadException(excmsg)
                    list_of_exceptions.addException(le)

                return
        try:
            container.setParameter(key_name, value, local_param=False)
            self.value_to_unset.append((exist,
                                        old_value,
                                        key_name,
                                        attribute_name,
                                        value,))
        except ParameterException as pe:
            excmsg = ("(ParamaterLoader) setValueTo, fail to set value with "
                      "key '"+str(key_name)+"': "+str(pe))
            le = LoadException(excmsg)
            list_of_exceptions.addException(le)

    def load(self, parameter_manager=None, sub_loader_name=None):
        self.value_to_unset = []
        self.value_to_remove = []
        AbstractLoader.load(self, parameter_manager, sub_loader_name)

        if parameter_manager is None:
            return  # TODO shouldn't raise ?

        if not hasattr(parameter_manager, self.container_name):
            excmsg = ("(ParamaterLoader) load, environment container does not"
                      " have the attribute '"+str(self.container_name)+"'")
            raise LoadException(excmsg)

        container = getattr(parameter_manager, self.container_name)

        exceptions = ListOfException()

        # add value
        for context_key, value, parent in self.value_to_add_to:
            self._addValueTo(container, context_key, value, parent, exceptions)

        # set value
        for value in self.value_to_set:
            key, instance, no_error_if_key_exist, override, parent = value
            self._setValueTo(container,
                             key,
                             instance,
                             no_error_if_key_exist,
                             override,
                             parent,
                             exceptions)

        # raise error list
        if exceptions.isThrowable():
            raise exceptions

    def unload(self, parameter_manager=None, sub_loader_name=None):
        AbstractLoader.unload(self, parameter_manager, sub_loader_name)

        if parameter_manager is None:
            return  # TODO shouldn't raise ?

        if not hasattr(parameter_manager, self.container_name):
            excmsg = ("(ParamaterLoader) unload, environment container does "
                      "not have the attribute '"+str(self.container_name)+"'")
            raise LoadException(excmsg)

        container = getattr(parameter_manager, self.container_name)

        exceptions = ListOfException()

        # remove values added
        for context_key, value, parent in self.value_to_remove:
            self._removeValueTo(container,
                                context_key,
                                value,
                                parent,
                                exceptions)

        # remove object set
        for packed_value in self.value_to_unset:
            exist, old_value, key_name, parentName, value = packed_value
            self._unsetValueTo(container,
                               exist,
                               old_value,
                               key_name,
                               parentName,
                               value,
                               exceptions)

        # raise error list
        if exceptions.isThrowable():
            raise exceptions
