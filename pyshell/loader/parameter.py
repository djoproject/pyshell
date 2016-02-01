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
from pyshell.loader.utils import getAndInitCallerModule, AbstractLoader
from pyshell.system.parameter import isAValidStringPath
from pyshell.utils.exception import ListOfException, ParameterException


def _local_getAndInitCallerModule(loaderClass, profile=None):
    return getAndInitCallerModule(loaderClass.__module__+"." +
                                  loaderClass.__name__,
                                  loaderClass,
                                  profile)


def registerAddValues(key, value, loaderClass, subLoaderName=None):
    # test key
    state, result = isAValidStringPath(key)
    if not state:
        raise LoadException("(Loader) registerAddValues, "+result)

    loader = _local_getAndInitCallerModule(loaderClass, subLoaderName)
    loader.valueToAddTo.append((key, value,))


def registerSet(key,
                obj,
                loaderClass,
                expectedClass,
                noErrorIfKeyExist=False,
                override=False,
                subLoaderName=None):
    # #test key
    state, result = isAValidStringPath(key)
    if not state:
        raise LoadException("(Loader) registerSetValue, "+result)

    # check typ si different de None
    if not isinstance(obj, expectedClass):
        # TODO try to instanciate expectedClass before to raise

        raise LoadException("(Loader) registerSetValue, obj must be an "
                            "instance of "+str(expectedClass.__name__))

    loader = _local_getAndInitCallerModule(loaderClass, subLoaderName)
    loader.valueToSet.append((key, obj, noErrorIfKeyExist, override,))


class ParameterAbstractLoader(AbstractLoader):
    def __init__(self, containerName):
        AbstractLoader.__init__(self)
        self.valueToAddTo = []
        self.valueToSet = []

        self.valueToUnset = None
        self.valueToRemove = None  # TODO not used...

        self.containerName = containerName

    def _removeValueTo(self,
                       container,
                       keyName,
                       valueToRemove,
                       attributeName,
                       listOfExceptions):
        envObject = container.getParameter(keyName,
                                           perfectMatch=True,
                                           startWithLocal=False,
                                           exploreOtherLevel=False)
        if envObject is None:
            le = LoadException("(ParamaterLoader) addValueTo, fail to add "
                               "value '"+str(valueToRemove)+"' to '" +
                               str(keyName)+"': unknow key name")
            listOfExceptions.addException(le)
            return

        try:
            envObject.removeValues(valueToRemove)
        except Exception as ex:
            listOfExceptions.addException(ex)

    def _addValueTo(self,
                    container,
                    keyName,
                    valueToAdd,
                    attributeName,
                    listOfExceptions):
        envObject = container.getParameter(keyName,
                                           perfectMatch=True,
                                           startWithLocal=False,
                                           exploreOtherLevel=False)
        if envObject is None:
            le = LoadException("(ParamaterLoader) addValueTo, fail to add "
                               "value '"+str(valueToAdd)+"' to '" +
                               str(keyName)+"': unknow key name")
            listOfExceptions.addException(le)
            return

        try:
            envObject.addValues(valueToAdd)
            self.valueToRemove.append((keyName, valueToAdd, attributeName))
        except Exception as ex:
            listOfExceptions.addException(ex)

    def _unsetValueTo(self,
                      container,
                      exist,
                      oldValue,
                      keyName,
                      attributeName,
                      value,
                      listOfExceptions):
        # still exist ?
        envItem = container.getParameter(keyName,
                                         perfectMatch=True,
                                         startWithLocal=False,
                                         exploreOtherLevel=False)
        if envItem is None:
            le = LoadException("(ParamaterLoader) unsetValueTo, fail to unset "
                               "value with key '"+str(keyName)+"': key does "
                               "not exist")
            listOfExceptions.addException(le)

        if exist:  # TODO could try to use envItem even if it is None, no ?
            # if current value is still the value loaded with this addon,
            # restore the old value
            if envItem.getValue() == value:
                envItem.setValue(oldValue)
            # otherwise, the value has been updated and the item already
            # exist before the loading of this module, so do nothing
        else:
            try:
                container.unsetParameter(keyName,
                                         startWithLocal=False,
                                         exploreOtherLevel=False)
            except ParameterException as pe:
                le = LoadException("(ParamaterLoader) unsetValueTo, fail to "
                                   "unset value with key '"+str(keyName) +
                                   "': "+str(pe))
                listOfExceptions.addException(le)

    def _setValueTo(self,
                    container,
                    keyName,
                    value,
                    noErrorIfKeyExist,
                    override,
                    attributeName,
                    listOfExceptions):
        param = container.getParameter(keyName,
                                       perfectMatch=True,
                                       startWithLocal=False,
                                       exploreOtherLevel=False)
        exist = param is not None
        oldValue = None
        if exist:
            oldValue = param.getValue()
            if not override:
                if not noErrorIfKeyExist:
                    le = LoadException("(ParamaterLoader) setValueTo, fail to "
                                       "set value with key '"+str(keyName)+"':"
                                       " key already exists")
                    listOfExceptions.addException(le)

                return
        try:
            container.setParameter(keyName, value, localParam=False)
            self.valueToUnset.append((exist,
                                      oldValue,
                                      keyName,
                                      attributeName,
                                      value,))
        except ParameterException as pe:
            le = LoadException("(ParamaterLoader) setValueTo, fail to set "
                               "value with key '"+str(keyName)+"': "+str(pe))
            listOfExceptions.addException(le)

    def load(self, parameterManager=None, subLoaderName=None):
        self.valueToUnset = []
        self.valueToRemove = []
        AbstractLoader.load(self, parameterManager, subLoaderName)

        if parameterManager is None:
            return  # TODO shouldn't raise ?

        if not hasattr(parameterManager, self.containerName):
            raise LoadException("(ParamaterLoader) load, environment "
                                "container does not have the attribute '" +
                                str(self.containerName)+"'")

        container = getattr(parameterManager, self.containerName)

        exceptions = ListOfException()

        # add value
        for contextKey, value, parent in self.valueToAddTo:
            self._addValueTo(container, contextKey, value, parent, exceptions)

        # set value
        for value in self.valueToSet:
            key, instance, noErrorIfKeyExist, override, parent = value
            self._setValueTo(container,
                             key,
                             instance,
                             noErrorIfKeyExist,
                             override,
                             parent,
                             exceptions)

        # raise error list
        if exceptions.isThrowable():
            raise exceptions

    def unload(self, parameterManager=None, subLoaderName=None):
        AbstractLoader.unload(self, parameterManager, subLoaderName)

        if parameterManager is None:
            return  # TODO shouldn't raise ?

        if not hasattr(parameterManager, self.containerName):
            raise LoadException("(ParamaterLoader) unload, environment "
                                "container does not have the attribute '" +
                                str(self.containerName)+"'")

        container = getattr(parameterManager, self.containerName)

        exceptions = ListOfException()

        # remove values added
        for contextKey, value, parent in self.valueToRemove:
            self._removeValueTo(container,
                                contextKey,
                                value,
                                parent,
                                exceptions)

        # remove object set
        for exist, oldValue, keyName, parentName, value in self.valueToUnset:
            self._unsetValueTo(container,
                               exist,
                               oldValue,
                               keyName,
                               parentName,
                               value,
                               exceptions)

        # raise error list
        if exceptions.isThrowable():
            raise exceptions

