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

from threading import current_thread
from uuid import uuid4

import pytest

from tries import multiLevelTries

from pyshell.system.container import DummyParameterContainer
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.parameter import Parameter
from pyshell.system.parameter import ParameterManager
from pyshell.system.parameter import ParameterTriesNode
from pyshell.system.parameter import _buildExistingPathFromError
from pyshell.system.parameter import isAValidStringPath
from pyshell.system.settings import GlobalSettings
from pyshell.system.settings import LocalSettings
from pyshell.utils.exception import ParameterException


class TestParameterManagerMisc(object):
    # isAValidStringPath, with invalid string

    def test_parameterMisc2(self):
        state, message = isAValidStringPath(object())
        assert not state
        assert message == ("invalid string_path, a string was expected, "
                           "got '<type 'object'>'")

    # isAValidStringPath with empty string
    def test_parameterMisc3(self):
        state, path = isAValidStringPath("")
        assert state
        assert len(path) == 0

    # isAValidStringPath with no char between two point
    def test_parameterMisc4(self):
        state, path = isAValidStringPath("plop..plap")
        assert state
        assert len(path) == 2
        assert path == ("plop", "plap",)

    # isAValidStringPath with no point in string
    def test_parameterMisc5(self):
        state, path = isAValidStringPath("plop")
        assert state
        assert len(path) == 1
        assert path == ("plop",)

    # isAValidStringPath with point in string
    def test_parameterMisc6(self):
        state, path = isAValidStringPath("plop.plap.plip")
        assert state
        assert len(path) == 3
        assert path == ("plop", "plap", "plip",)


class TestParameterNode(object):

    def test_init(self):
        ParameterTriesNode("path")

    def test_notDefinedLocalVar1(self):
        p = ParameterTriesNode("path")
        assert not p.hasLocalVar("plop")

        with pytest.raises(KeyError):
            p.getLocalVar("plop")

    def test_notDefinedLocalVar2(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        p.setLocalVar("tutu", param)
        assert not p.hasLocalVar("plop")

        with pytest.raises(KeyError):
            p.getLocalVar("plop")

    def test_definedLocalVar(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        p.setLocalVar("tutu", param)
        assert p.hasLocalVar("tutu")
        assert p.getLocalVar("tutu") is param

    def test_notDefinedGlobalVar(self):
        p = ParameterTriesNode("path")
        with pytest.raises(ParameterException):
            p.getGlobalVar()

    def test_definedGlobalVar(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        p.setGlobalVar(param, "loader name")
        assert p.getGlobalVar() is param

    def test_setMultipleLocalVar(self):
        p = ParameterTriesNode("path")
        param1 = Parameter("value")
        param2 = Parameter("value")
        param3 = Parameter("value")

        p.setLocalVar("p1", param1)
        p.setLocalVar("p2", param2)
        p.setLocalVar("p3", param3)

        assert p.getLocalVar("p1") is param1
        assert p.getLocalVar("p2") is param2
        assert p.getLocalVar("p3") is param3

    def test_overwriteLocalVar(self):
        p = ParameterTriesNode("path")
        param1 = Parameter("value")
        param2 = Parameter("value")

        p.setLocalVar("p1", param1)
        assert p.getLocalVar("p1") is param1

        p.setLocalVar("p1", param2)
        assert p.getLocalVar("p1") is param2

    def test_overwriteLocalVarWithReadOnly(self):
        p = ParameterTriesNode("path")
        param1 = Parameter("value1")
        param1.settings.setReadOnly(True)
        p.setLocalVar("tutu", param1)

        param2 = Parameter("value2")
        with pytest.raises(ParameterException):
            p.setLocalVar("tutu", param2)

    def test_setGlobalVarWithoutFreeze(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        p.setGlobalVar(param, "loader name")
        assert p.getGlobalVar() is param

    def test_setGlobalVarWithFreeze(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        p.setGlobalVar(param, "loader", freeze=True)
        assert p.getGlobalVar() is param

    def test_setGlobalVarWithFreezeAndNoneLoader(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        with pytest.raises(ParameterException):
            p.setGlobalVar(param, None, freeze=True)

    def test_overwriteGlobalVarWithoutPreviousFreezing(self):
        p = ParameterTriesNode("path")
        param1 = Parameter("value")
        p.setGlobalVar(param1, "loader name")

        param2 = Parameter("value")
        p.setGlobalVar(param2, "loader name")

        assert p.getGlobalVar() is param2
        assert not p.isFrozen()

    def test_overwriteGlobalVarWithPreviousFreezing(self):
        p = ParameterTriesNode("path")
        param1 = Parameter("value")
        p.setGlobalVar(param1, "loader 1", freeze=True)

        param2 = Parameter("value")
        p.setGlobalVar(param2, "loader 1")

        assert p.getGlobalVar() is param2
        assert param2.settings.startingHash == param1.settings.startingHash
        assert p.isFrozen()

    def test_overwriteGlobalVarWithOnlyFreezingOnOverwrite(self):
        p = ParameterTriesNode("path")
        param1 = Parameter("value")
        p.setGlobalVar(param1, "loader name")

        param2 = Parameter("value")
        p.setGlobalVar(param2, "loader 2", freeze=True)

        assert p.getGlobalVar() is param2
        assert param2.settings.startingHash == param2.settings.startingHash
        assert p.isFrozen()

    def test_overwriteGlobalVarWithFreezingOnPreviousAndCurrent(self):
        p = ParameterTriesNode("path")
        param1 = Parameter("value")
        p.setGlobalVar(param1, "loader 1", freeze=True)
        assert p.isFrozen()

        param2 = Parameter("value")

        with pytest.raises(ParameterException):
            p.setGlobalVar(param2, "loader 2", freeze=True)

    def test_overwriteGlobalVarWithFreezingOnPreviousAndNewLoaderOrigin(self):
        p = ParameterTriesNode("path")
        param1 = Parameter("value")
        p.setGlobalVar(param1, "loader 1", freeze=True)
        assert p.isFrozen()

        param2 = Parameter("value")

        with pytest.raises(ParameterException):
            p.setGlobalVar(param2, "loader 2", freeze=False)

    def test_overwriteGlobalVarWithReadOnly(self):
        p = ParameterTriesNode("path")
        param1 = Parameter("value1")
        param1.settings.setReadOnly(True)
        p.setGlobalVar(param1, "loader name")

        param2 = Parameter("value2")
        with pytest.raises(ParameterException):
            p.setGlobalVar(param2, "loader name")

    def test_unsetUnexistantLocalVar(self):
        p = ParameterTriesNode("path")
        p.unsetLocalVar("does not exist")
        assert not p.hasLocalVar("does not exist")

    def test_unsetExistantLocalVar(self):
        p = ParameterTriesNode("path")
        param1 = Parameter("value1")
        p.setLocalVar("plop", param1)
        assert p.hasLocalVar("plop")
        p.unsetLocalVar("plop")
        assert not p.hasLocalVar("plop")

    def test_unsetExistantLocalVarNotRemovable(self):
        p = ParameterTriesNode("path")
        param1 = Parameter("value1")
        param1.settings.setRemovable(False)
        p.setLocalVar("plop", param1)
        assert p.hasLocalVar("plop")
        with pytest.raises(ParameterException):
            p.unsetLocalVar("plop")

    def test_unsetUnexistantGlobalVar(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        p.setLocalVar("tutu", param)
        assert p.hasLocalVar("tutu")
        p.unsetLocalVar("tutu")
        assert not p.hasLocalVar("tutu")

    def test_unsetExistantGlobalVarWithoutFreeze(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        p.setGlobalVar(param, "loader name")
        assert p.getGlobalVar() is param
        p.unsetGlobalVar()

        with pytest.raises(ParameterException):
            p.getGlobalVar()

    def test_unsetExistantGlobalVarWithFreeze(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        p.setGlobalVar(param, "loader 1", freeze=True)
        assert p.getGlobalVar() is param
        p.unsetGlobalVar()

        with pytest.raises(ParameterException):
            p.getGlobalVar()

    def test_unsetExistantGlobalVarNotRemovable(self):
        p = ParameterTriesNode("path")
        param1 = Parameter("value1")
        param1.settings.setRemovable(False)
        p.setGlobalVar(param1, "loader name")
        assert p.hasGlobalVar()
        with pytest.raises(ParameterException):
            p.unsetGlobalVar()

    def test_isRemovableWithNothingStored1(self):
        p = ParameterTriesNode("path")
        assert p.isRemovable()

    def test_isRemovableWithNothingStored2(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        p.setLocalVar("local", param)
        p.unsetLocalVar("local")
        assert p.isRemovable()

    def test_isRemovableWithNothingStored3(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        p.setGlobalVar(param, "loader name")
        p.unsetGlobalVar()
        assert p.isRemovable()

    def test_isRemovableWithLocalVar(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        p.setLocalVar("local", param)
        assert not p.isRemovable()

    def test_isRemovableWithGlobalVar(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        p.setGlobalVar(param, "loader name")
        assert not p.isRemovable()

    def test_isRemovableWithFreeze(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")
        p.setGlobalVar(param, "loader 1", freeze=True)
        p.unsetGlobalVar()
        assert not p.isRemovable()

    def test_unfreeze(self):
        p = ParameterTriesNode("path")
        param = Parameter("value")

        p.setGlobalVar(param, "loader 1", freeze=True)
        assert p.isFrozen()
        assert not p.isRemovable()

        p.unsetGlobalVar()
        assert p.isFrozen()
        assert not p.isRemovable()

        p.unfreeze()
        assert not p.isFrozen()
        assert p.isRemovable()


# # ParameterManager constructor # #
class TestParameterManager(object):

    def setup_method(self, method):
        self.params = ParameterManager()
        self.params.setParameter("aa.bb.cc", Parameter("plop"))
        self.params.setParameter("ab.bc.cd", Parameter("plip"))

    # with parent None + test getCurrentId
    def test_parameterManagerConstructor1(self):
        params = ParameterManager(parent=None)
        curr_id = params.parentContainer.getCurrentId()
        assert curr_id == current_thread().ident

    # with valid parent + test getCurrentId
    def test_parameterManagerConstructor2(self):
        params = ParameterManager(parent=DummyParameterContainer())
        curr_id = params.parentContainer.getCurrentId()
        assert curr_id == current_thread().ident

    # with parent without getCurrentId + test getCurrentId
    def test_parameterManagerConstructor3(self):
        with pytest.raises(ParameterException):
            ParameterManager(object())

    # # ParameterManager methods # #

    # _buildExistingPathFromError, with 0 token found and some wrong token
    def test_parameterManager1(self):
        path = ("plop", "plip", "plap",)
        mltries = multiLevelTries()
        advanced_result = mltries.advancedSearch(path)
        buildedpath = tuple(_buildExistingPathFromError(path, advanced_result))
        assert buildedpath == path

    # _buildExistingPathFromError, with some token found and 0 wrong token
    def test_parameterManager2(self):
        path = ("plop", "plip", "plap",)
        mltries = multiLevelTries()
        mltries.insert(("plop", "plip", "plap", "plup",), object())
        advanced_result = mltries.advancedSearch(path)
        buildedpath = tuple(_buildExistingPathFromError(path, advanced_result))
        assert buildedpath == path

    # _buildExistingPathFromError, with some token found and some wrong token
    def test_parameterManager3(self):
        path = ("plop", "plip", "plap",)
        mltries = multiLevelTries()
        mltries.insert(("plop", "plip", "plyp", "plup",), object())
        advanced_result = mltries.advancedSearch(path)
        buildedpath = tuple(_buildExistingPathFromError(path, advanced_result))
        assert buildedpath == path

    # #

    # _getAdvanceResult, search a invalid path
    def test_parameterManager4(self):
        with pytest.raises(ParameterException):
            self.params._getAdvanceResult("test", object())

    # _getAdvanceResult, raise_if_ambiguous=True and ambiguous
    def test_parameterManager5(self):
        with pytest.raises(ParameterException):
            self.params._getAdvanceResult("test",
                                          "a.b.c",
                                          raise_if_ambiguous=True,
                                          raise_if_not_found=False)

    # _getAdvanceResult, raise_if_ambiguous=True and not ambiguous
    def test_parameterManager6(self):
        result = self.params._getAdvanceResult("test",
                                               "aa.bb.cc",
                                               raise_if_ambiguous=True,
                                               raise_if_not_found=False)
        assert result.isValueFound()

    # _getAdvanceResult, raise_if_ambiguous=False and ambiguous
    def test_parameterManager7(self):
        result = self.params._getAdvanceResult("test",
                                               "a.b.c",
                                               raise_if_ambiguous=False,
                                               raise_if_not_found=False)
        assert not result.isValueFound()
        assert result.isAmbiguous()

    # _getAdvanceResult, raise_if_not_found=True and not found
    def test_parameterManager8(self):
        with pytest.raises(ParameterException):
            self.params._getAdvanceResult("test",
                                          "plop",
                                          raise_if_not_found=True,
                                          raise_if_ambiguous=False)

    # _getAdvanceResult, raise_if_not_found=True and found
    def test_parameterManager9(self):
        with pytest.raises(ParameterException):
            self.params._getAdvanceResult("test",
                                          "plop",
                                          raise_if_not_found=True,
                                          raise_if_ambiguous=False)

    # _getAdvanceResult, raise_if_not_found=False and not found
    def test_parameterManager10(self):
        result = self.params._getAdvanceResult("test",
                                               "plop",
                                               raise_if_ambiguous=False,
                                               raise_if_not_found=False)
        assert not result.isValueFound()
        assert not result.isAmbiguous()

    # _getAdvanceResult, with perfect_match
    def test_parameterManager11(self):
        result = self.params._getAdvanceResult("test",
                                               "a.b.c",
                                               raise_if_ambiguous=False,
                                               raise_if_not_found=False,
                                               perfect_match=True)
        assert not result.isValueFound()
        assert not result.isAmbiguous()

    # _getAdvanceResult, with perfect_match
    def test_parameterManager11b(self):
        result = self.params._getAdvanceResult("test",
                                               "aa.bb.cc",
                                               raise_if_ambiguous=False,
                                               raise_if_not_found=False,
                                               perfect_match=True)
        assert result.isValueFound()
        assert not result.isAmbiguous()

    # #

    # test getAllowedType
    def test_parameterManager12(self):
        assert self.params.getAllowedType() is Parameter

    # test isAnAllowedType, should not allow inherited type
    def test_parameterManager13(self):
        assert not self.params.isAnAllowedType(EnvironmentParameter("plop"))
        assert self.params.isAnAllowedType(Parameter("titi"))

    # test extractParameter, with a valid type
    def test_parameterManager14(self):
        p = Parameter(42)
        assert self.params._extractParameter(p) is p

    # test extractParameter, with another parameter type
    def test_parameterManager15(self):
        assert isinstance(self.params._extractParameter(42), Parameter)

    # test extractParameter, with something else
    # (to try to instanciate an allowed type)
    def test_parameterManager16(self):
        with pytest.raises(ParameterException):
            self.params._extractParameter(EnvironmentParameter("plop"))

    ##

    # setParameter, try to set local with freeze enable
    def test_parameterManager17a(self):
        with pytest.raises(ParameterException):
            self.params.setParameter("plop",
                                     Parameter("toto"),
                                     local_param=True,
                                     freeze=True)

    # setParameter, local exists + local + existing is readonly
    def test_parameterManager17b(self):
        param = self.params.setParameter("plop",
                                         Parameter("toto"),
                                         local_param=True)
        curr_id = self.params.parentContainer.getCurrentId()
        assert len(self.params.threadLocalVar[curr_id]) > 0
        node = None
        for n in self.params.threadLocalVar[curr_id]:
            if n.string_key == "plop":
                node = n
        assert node is not None
        assert node.getLocalVar(curr_id) is param
        assert isinstance(param.settings, LocalSettings)
        param.settings.setReadOnly(True)
        with pytest.raises(ParameterException):
            self.params.setParameter("plop",
                                     Parameter("titi"),
                                     local_param=True)

    # setParameter, local exists + local + existing is removable
    def test_parameterManager18(self):
        param1 = self.params.setParameter("plop",
                                          Parameter("toto"),
                                          local_param=True)
        curr_id = self.params.parentContainer.getCurrentId()
        assert len(self.params.threadLocalVar[curr_id]) > 0
        node = None
        for n in self.params.threadLocalVar[curr_id]:
            if n.string_key == "plop":
                node = n
        assert node is not None
        assert node.getLocalVar(curr_id) is param1
        assert isinstance(param1.settings, LocalSettings)
        param1.settings.setRemovable(True)

        param2 = self.params.setParameter("plop",
                                          Parameter("titi"),
                                          local_param=True)
        curr_id = self.params.parentContainer.getCurrentId()
        node = None
        for n in self.params.threadLocalVar[curr_id]:
            if n.string_key == "plop":
                node = n
        assert node is not None
        assert node.getLocalVar(curr_id) is param2
        assert isinstance(param2.settings, LocalSettings)
        assert param1 is not param2

    # setParameter, global exists (not local) + local + existing is readonly
    def test_parameterManager19(self):
        param1 = self.params.setParameter("plop",
                                          Parameter("toto"),
                                          local_param=False)
        assert isinstance(param1.settings, GlobalSettings)
        param1.settings.setReadOnly(True)

        param2 = self.params.setParameter("plop",
                                          Parameter("titi"),
                                          local_param=True)
        curr_id = self.params.parentContainer.getCurrentId()
        node = None
        for n in self.params.threadLocalVar[curr_id]:
            if n.string_key == "plop":
                node = n
        assert node is not None
        assert node.getLocalVar(curr_id) is param2
        assert isinstance(param2.settings, LocalSettings)
        assert param1 is not param2

    # setParameter, global exists (not local) + local + existing is removable
    def test_parameterManager20(self):
        param1 = self.params.setParameter("plop",
                                          Parameter("toto"),
                                          local_param=False)
        assert isinstance(param1.settings, GlobalSettings)
        param1.settings.setRemovable(True)

        param2 = self.params.setParameter("plop",
                                          Parameter("titi"),
                                          local_param=True)
        curr_id = self.params.parentContainer.getCurrentId()
        node = None
        for n in self.params.threadLocalVar[curr_id]:
            if n.string_key == "plop":
                node = n
        assert node is not None
        assert node.getLocalVar(curr_id) is param2
        assert isinstance(param2.settings, LocalSettings)
        assert param1 is not param2

    # setParameter, nothing exists + local
    def test_parameterManager21(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=True)
        curr_id = self.params.parentContainer.getCurrentId()
        node = None
        for n in self.params.threadLocalVar[curr_id]:
            if n.string_key == "plop":
                node = n
        assert node is not None
        assert node.getLocalVar(curr_id) is param
        assert isinstance(param.settings, LocalSettings)
        assert self.params.getParameter("plop") is param

    # setParameter, local exists + global + existing is readonly
    def test_parameterManager22(self):
        param1 = self.params.setParameter("plop",
                                          Parameter("titi"),
                                          local_param=True)
        curr_id = self.params.parentContainer.getCurrentId()
        node = None
        for n in self.params.threadLocalVar[curr_id]:
            if n.string_key == "plop":
                node = n
        assert node is not None
        assert node.getLocalVar(curr_id) is param1
        assert isinstance(param1.settings, LocalSettings)
        param1.settings.setReadOnly(True)

        param2 = self.params.setParameter("plop",
                                          Parameter("toto"),
                                          local_param=False)
        assert isinstance(param2.settings, GlobalSettings)

        assert param1 is not param2

    # setParameter, local exists + global + existing is removable
    def test_parameterManager23(self):
        param1 = self.params.setParameter("plop",
                                          Parameter("titi"),
                                          local_param=True)
        curr_id = self.params.parentContainer.getCurrentId()
        node = None
        for n in self.params.threadLocalVar[curr_id]:
            if n.string_key == "plop":
                node = n
        assert node is not None
        assert node.getLocalVar(curr_id) is param1
        assert isinstance(param1.settings, LocalSettings)
        param1.settings.setRemovable(True)

        param2 = self.params.setParameter("plop",
                                          Parameter("toto"),
                                          local_param=False)
        assert isinstance(param2.settings, GlobalSettings)

        assert param1 is not param2

    # setParameter, global exists (not local) + global + existing is readonly
    def test_parameterManager24(self):
        param1 = self.params.setParameter("plop",
                                          Parameter("titi"),
                                          local_param=False)
        assert isinstance(param1.settings, GlobalSettings)
        param1.settings.setReadOnly(True)

        with pytest.raises(ParameterException):
            self.params.setParameter("plop",
                                     Parameter("toto"), local_param=False)

    # setParameter, global exists (not local) + global + existing is removable
    def test_parameterManager25(self):
        param1 = self.params.setParameter("plop",
                                          Parameter("titi"),
                                          local_param=False)
        assert isinstance(param1.settings, GlobalSettings)
        param1.settings.setRemovable(True)

        param2 = self.params.setParameter("plop",
                                          Parameter("toto"),
                                          local_param=False)
        assert isinstance(param2.settings, GlobalSettings)

        assert param1 is not param2

    # setParameter, nothing exists + global
    def test_parameterManager26(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=False)
        assert isinstance(param.settings, GlobalSettings)
        assert self.params.getParameter("plop") is param

    # setParameter, on global overwritte ONLY, setting has to be
    # transfered/merged from old to new
    def test_parameterManagerSetParameter1(self):
        p = Parameter("titi")
        param = self.params.setParameter("plop",
                                         p,
                                         local_param=False,
                                         origin_loader="loader A",
                                         freeze=True)

        assert hasattr(param.settings, "startingHash")

        has = param.settings.startingHash

        param = self.params.setParameter("plop",
                                         Parameter("tata"),
                                         origin_loader="loader A",
                                         local_param=False)

        assert param.settings.startingHash == has

    def test_setParameterFirstParameterForThisLoader(self):
        p = Parameter("titi")
        self.params.setParameter("plop",
                                 p,
                                 local_param=False,
                                 origin_loader="loader A")

        l = self.params.getLoaderNodes("loader A")
        assert len(l) == 1
        assert l[0].getGlobalVar() is p

    def test_setParameterSeveralParameterForThisLoader(self):
        p1 = Parameter("titi")
        self.params.setParameter("plop",
                                 p1,
                                 local_param=False,
                                 origin_loader="loader A")

        p2 = Parameter("titi")
        self.params.setParameter("plap",
                                 p2,
                                 local_param=False,
                                 origin_loader="loader A")

        l = self.params.getLoaderNodes("loader A")
        assert len(l) == 2
        l = [pm.getGlobalVar() for pm in l]
        assert p1 in l
        assert p2 in l

    def test_setParameterOverrideParameterInLoader(self):
        p1 = Parameter("titi")
        self.params.setParameter("plop",
                                 p1,
                                 local_param=False,
                                 origin_loader="loader A")

        p2 = Parameter("titi")
        self.params.setParameter("plop",
                                 p2,
                                 local_param=False,
                                 origin_loader="loader A")

        l = self.params.getLoaderNodes("loader A")
        assert len(l) == 1
        l = [pm.getGlobalVar() for pm in l]
        assert p2 in l

    def test_clearFrozenNodeLoaderDoesNotExist(self):
        self.params.clearFrozenNode("plop")

    def test_clearFrozenNodeFrozenNodeWithGlobalVarSet(self):
        p1 = Parameter("titi")
        self.params.setParameter("plop",
                                 p1,
                                 local_param=False,
                                 origin_loader="loader A",
                                 freeze=True)
        self.params.clearFrozenNode("loader A")
        assert self.params.hasParameter("plop")
        assert "loader A" in self.params.loaderGlobalVar
        self.params.unsetParameter("plop")
        assert not self.params.hasParameter("plop")
        assert "loader A" not in self.params.loaderGlobalVar

    def test_clearFrozenNodeFrozenNodeWithoutVarSet(self):
        p1 = Parameter("titi")
        self.params.setParameter("plop",
                                 p1,
                                 local_param=False,
                                 origin_loader="loader A",
                                 freeze=True)
        self.params.unsetParameter("plop")
        assert not self.params.hasParameter("plop")
        assert "loader A" in self.params.loaderGlobalVar
        self.params.clearFrozenNode("loader A")
        assert "loader A" not in self.params.loaderGlobalVar

    def test_clearFrozenNodeFrozenNodeWithLocalVarSet(self):
        p1 = Parameter("titi")
        self.params.setParameter("plop",
                                 p1,
                                 local_param=False,
                                 origin_loader="loader A",
                                 freeze=True)
        p2 = Parameter("tutu")
        self.params.setParameter("plop",
                                 p2,
                                 local_param=True)
        self.params.unsetParameter("plop",
                                   local_param=False,
                                   explore_other_level=False)
        assert "loader A" in self.params.loaderGlobalVar
        self.params.clearFrozenNode("loader A")
        assert "loader A" not in self.params.loaderGlobalVar
        assert self.params.hasParameter("plop")

    # #

    # getParameter, local exists + local_param=True + explore_other_level=True
    def test_parameterManager27(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=True)
        pget = self.params.getParameter("plop",
                                        local_param=True,
                                        explore_other_level=True)
        assert param is pget

    # getParameter, local exists + local_param=True + explore_other_level=False
    def test_parameterManager28(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=True)
        pget = self.params.getParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)
        assert param is pget

    # getParameter, global exists + local_param=True + explore_other_level=True
    def test_parameterManager29(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=False)
        pget = self.params.getParameter("plop",
                                        local_param=True,
                                        explore_other_level=True)
        assert param is pget

    # getParameter, global exists + local_param=True +
    # explore_other_level=False
    def test_parameterManager30(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)
        pget = self.params.getParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)
        assert pget is None

    # getParameter, local exists + local_param=False + explore_other_level=True
    def test_parameterManager31(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=True)
        pget = self.params.getParameter("plop",
                                        local_param=False,
                                        explore_other_level=True)
        assert param is pget

    # getParameter, local exists + local_param=False +
    # explore_other_level=False
    def test_parameterManager32(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=True)
        pget = self.params.getParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)
        assert pget is None

    # getParameter, global exists + local_param=False +
    # explore_other_level=True
    def test_parameterManager33(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=False)
        pget = self.params.getParameter("plop",
                                        local_param=False,
                                        explore_other_level=True)
        assert param is pget

    # getParameter, global exists + local_param=False +
    # explore_other_level=False
    def test_parameterManager34(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=False)
        pget = self.params.getParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)
        assert param is pget

    # getParameter, nothing exists + local_param=True +
    # explore_other_level=True
    def test_parameterManager35(self):
        pget = self.params.getParameter("plop",
                                        local_param=True,
                                        explore_other_level=True)
        assert pget is None

    # getParameter, nothing exists + local_param=True +
    # explore_other_level=False
    def test_parameterManager36(self):
        pget = self.params.getParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)
        assert pget is None

    # getParameter, nothing exists + local_param=False +
    # explore_other_level=True
    def test_parameterManager37(self):
        pget = self.params.getParameter("plop",
                                        local_param=False,
                                        explore_other_level=True)
        assert pget is None

    # getParameter, nothing exists + local_param=False +
    # explore_other_level=False
    def test_parameterManager38(self):
        pget = self.params.getParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)
        assert pget is None

    ##

    # hasParameter, local exists + local_param=True +
    # explore_other_level=True
    def test_parameterManager39(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=True)
        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=True)

    # hasParameter, local exists + local_param=True +
    # explore_other_level=False
    def test_parameterManager40(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=True)
        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)

    # hasParameter, global exists + local_param=True +
    # explore_other_level=True
    def test_parameterManager41(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)
        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=True)

    # hasParameter, global exists + local_param=True +
    # explore_other_level=False
    def test_parameterManager42(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)
        assert not self.params.hasParameter("plop",
                                            local_param=True,
                                            explore_other_level=False)

    # hasParameter, local exists + local_param=False +
    # explore_other_level=True
    def test_parameterManager43(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=True)
        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=True)

    # hasParameter, local exists + local_param=False +
    # explore_other_level=False
    def test_parameterManager44(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=True)
        assert not self.params.hasParameter("plop",
                                            local_param=False,
                                            explore_other_level=False)

    # hasParameter, global exists + local_param=False +
    # explore_other_level=True
    def test_parameterManager45(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)
        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=True)

    # hasParameter, global exists + local_param=False +
    # explore_other_level=False
    def test_parameterManager46(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)
        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)

    # hasParameter, nothing exists + local_param=True +
    # explore_other_level=True
    def test_parameterManager47(self):
        assert not self.params.hasParameter("plop",
                                            local_param=True,
                                            explore_other_level=True)

    # hasParameter, nothing exists + local_param=True +
    # explore_other_level=False
    def test_parameterManager48(self):
        assert not self.params.hasParameter("plop",
                                            local_param=True,
                                            explore_other_level=False)

    # hasParameter, nothing exists + local_param=False +
    # explore_other_level=True
    def test_parameterManager49(self):
        assert not self.params.hasParameter("plop",
                                            local_param=False,
                                            explore_other_level=True)

    # hasParameter, nothing exists + local_param=False +
    # explore_other_level=False
    def test_parameterManager50(self):
        assert not self.params.hasParameter("plop",
                                            local_param=False,
                                            explore_other_level=False)

    ##

    # unsetParameter, local exists + local_param=True +
    # explore_other_level=True
    def test_parameterManager51(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=True)
        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)
        self.params.unsetParameter("plop",
                                   local_param=True,
                                   explore_other_level=True)
        assert not self.params.hasParameter("plop",
                                            local_param=True,
                                            explore_other_level=False)

    # unsetParameter, local exists + local_param=True +
    # explore_other_level=False
    def test_parameterManager52(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=True)
        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)
        self.params.unsetParameter("plop",
                                   local_param=True,
                                   explore_other_level=False)
        assert not self.params.hasParameter("plop",
                                            local_param=True,
                                            explore_other_level=False)

    # unsetParameter, global exists + local_param=True +
    # explore_other_level=True
    def test_parameterManager53(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)
        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)
        self.params.unsetParameter("plop",
                                   local_param=True,
                                   explore_other_level=True)
        assert not self.params.hasParameter("plop",
                                            local_param=False,
                                            explore_other_level=False)

    # unsetParameter, global exists + local_param=True +
    # explore_other_level=False
    def test_parameterManager54(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)
        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)
        with pytest.raises(ParameterException):
            self.params.unsetParameter("plop",
                                       local_param=True,
                                       explore_other_level=False)
        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)

    # unsetParameter, local exists + local_param=False +
    # explore_other_level=True
    def test_parameterManager55(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=True)
        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)
        self.params.unsetParameter("plop",
                                   local_param=False,
                                   explore_other_level=True)
        assert not self.params.hasParameter("plop",
                                            local_param=True,
                                            explore_other_level=False)

    # unsetParameter, local exists + local_param=False +
    # explore_other_level=False
    def test_parameterManager56(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=True)

        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)
        with pytest.raises(ParameterException):
            self.params.unsetParameter("plop",
                                       local_param=False,
                                       explore_other_level=False)
        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)

    # unsetParameter, global exists + local_param=False +
    # explore_other_level=True
    def test_parameterManager57(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)
        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)
        self.params.unsetParameter("plop",
                                   local_param=False,
                                   explore_other_level=True)
        assert not self.params.hasParameter("plop",
                                            local_param=False,
                                            explore_other_level=False)

    # unsetParameter, global exists + local_param=False +
    # explore_other_level=False
    def test_parameterManager58(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)
        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)
        self.params.unsetParameter("plop",
                                   local_param=False,
                                   explore_other_level=False)
        assert not self.params.hasParameter("plop",
                                            local_param=False,
                                            explore_other_level=False)

    # unsetParameter, local + global exists + local_param=False +
    # explore_other_level=True
    def test_parameterManager59(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=True)
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)

        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)
        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)

        self.params.unsetParameter("plop",
                                   local_param=False,
                                   explore_other_level=True)

        assert not self.params.hasParameter("plop",
                                            local_param=False,
                                            explore_other_level=False)
        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)

    # unsetParameter, local + global exists + local_param=False +
    # explore_other_level=False
    def test_parameterManager60(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=True)
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)

        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)
        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)

        self.params.unsetParameter("plop",
                                   local_param=False,
                                   explore_other_level=False)

        assert not self.params.hasParameter("plop",
                                            local_param=False,
                                            explore_other_level=False)
        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)

    # unsetParameter, global + local exists + local_param=True +
    # explore_other_level=True
    def test_parameterManager61(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=True)
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)

        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)
        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)

        self.params.unsetParameter("plop",
                                   local_param=True,
                                   explore_other_level=True)

        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)
        assert not self.params.hasParameter("plop",
                                            local_param=True,
                                            explore_other_level=False)

    # unsetParameter, global + local exists + local_param=True +
    # explore_other_level=False
    def test_parameterManager62(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=True)
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)

        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)
        assert self.params.hasParameter("plop",
                                        local_param=True,
                                        explore_other_level=False)

        self.params.unsetParameter("plop",
                                   local_param=True,
                                   explore_other_level=True)

        assert self.params.hasParameter("plop",
                                        local_param=False,
                                        explore_other_level=False)
        assert not self.params.hasParameter("plop",
                                            local_param=True,
                                            explore_other_level=False)

    # unsetParameter, nothing exists + local_param=True +
    # explore_other_level=True
    def test_parameterManager63(self):
        with pytest.raises(ParameterException):
            self.params.unsetParameter("plop",
                                       local_param=True,
                                       explore_other_level=True)

    # unsetParameter, nothing exists + local_param=True +
    # explore_other_level=False
    def test_parameterManager64(self):
        with pytest.raises(ParameterException):
            self.params.unsetParameter("plop",
                                       local_param=True,
                                       explore_other_level=False)

    # unsetParameter, nothing exists + local_param=False +
    # explore_other_level=True
    def test_parameterManager65(self):
        with pytest.raises(ParameterException):
            self.params.unsetParameter("plop",
                                       local_param=False,
                                       explore_other_level=True)

    # unsetParameter, nothing exists + local_param=False +
    # explore_other_level=False
    def test_parameterManager66(self):
        with pytest.raises(ParameterException):
            self.params.unsetParameter("plop",
                                       local_param=False,
                                       explore_other_level=False)

    # unsetParameter, try to remove an existing global one, not removable
    # with loader dependancies
    def test_parameterManagerUnsetParameter1(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=False)
        param.settings.setRemovable(False)
        with pytest.raises(ParameterException):
            self.params.unsetParameter("plop",
                                       local_param=False,
                                       explore_other_level=False)

    # unsetParameter, try to remove an existing global one, with loader
    # dependancies and force
    def test_parameterManagerUnsetParameter2(self):
        self.params.setParameter("plop",
                                 Parameter("titi"),
                                 local_param=False)
        self.params.unsetParameter("plop",
                                   local_param=False,
                                   explore_other_level=False,
                                   force=True)
        assert not self.params.hasParameter("plop",
                                            local_param=False,
                                            explore_other_level=False)

    # unsetParameter, try to remove an existing global one, not removable
    # and force
    def test_parameterManagerUnsetParameter3(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=False)
        param.settings.setRemovable(False)
        self.params.unsetParameter("plop",
                                   local_param=False,
                                   explore_other_level=False,
                                   force=True)
        assert not self.params.hasParameter("plop",
                                            local_param=False,
                                            explore_other_level=False)

    # unsetParameter, try to remove an existing local one, not removable
    # and force
    def test_parameterManagerUnsetParameter4(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=True)
        param.settings.setRemovable(False)
        self.params.unsetParameter("plop",
                                   local_param=True,
                                   explore_other_level=False,
                                   force=True)
        assert not self.params.hasParameter("plop",
                                            local_param=True,
                                            explore_other_level=False)

    # unsetParameter, try to remove an existing global one, not removable
    def test_parameterManagerUnsetParameter5(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=False)
        param.settings.setRemovable(False)
        with pytest.raises(ParameterException):
            self.params.unsetParameter("plop",
                                       local_param=False,
                                       explore_other_level=False)

    # unsetParameter, try to remove an existing local one, not removable
    def test_parameterManagerUnsetParameter6(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=True)
        param.settings.setRemovable(False)
        with pytest.raises(ParameterException):
            self.params.unsetParameter("plop",
                                       local_param=True,
                                       explore_other_level=False)

    def test_unsetParameterLastParameterForLoader(self):
        p1 = Parameter("titi")
        self.params.setParameter("plop",
                                 p1,
                                 local_param=False,
                                 origin_loader="loader A")

        p = self.params.unsetParameter("plop")
        assert p is p1

        l = self.params.getLoaderNodes("loader A")
        assert len(l) == 0

    def test_unsetParameterRemainParameterForLoader(self):
        p1 = Parameter("titi")
        self.params.setParameter("plop",
                                 p1,
                                 local_param=False,
                                 origin_loader="loader A")

        p2 = Parameter("titi")
        self.params.setParameter("plup",
                                 p2,
                                 local_param=False,
                                 origin_loader="loader A")

        p = self.params.unsetParameter("plop")
        assert p is p1

        l = self.params.getLoaderNodes("loader A")
        assert len(l) == 1
        l = [pm.getGlobalVar() for pm in l]
        assert p2 in l

    def test_unsetParameterLastFrozenParameterForLoader(self):
        p1 = Parameter("titi")
        self.params.setParameter("plop",
                                 p1,
                                 local_param=False,
                                 origin_loader="loader A",
                                 freeze=True)

        p = self.params.unsetParameter("plop")
        assert p is p1

        l = self.params.getLoaderNodes("loader A")
        assert len(l) == 1
        assert not l[0].hasGlobalVar()

    def test_unsetParameterLastFrozenParameterForLoaderWithUnfreeze(self):
        p1 = Parameter("titi")
        self.params.setParameter("plop",
                                 p1,
                                 local_param=False,
                                 origin_loader="loader A",
                                 freeze=True)

        p = self.params.unsetParameter("plop", unfreeze=True)
        assert p is p1

        l = self.params.getLoaderNodes("loader A")
        assert len(l) == 0

    ##

    # flushVariableLevelForThisThread, nothing for the current thread
    def test_parameterManager67(self):
        params = ParameterManager()
        params.setParameter("plop", Parameter("titi"), local_param=False)
        curr_id = params.parentContainer.getCurrentId()
        assert curr_id not in params.threadLocalVar
        params.flush()
        curr_id = params.parentContainer.getCurrentId()
        assert curr_id not in params.threadLocalVar

    # flushVariableLevelForThisThread, flush parameter that only exists for
    # the current thread
    def test_parameterManager68(self):
        params = ParameterManager()
        params.setParameter("plop", Parameter("titi"), local_param=True)

        assert params.hasParameter("plop",
                                   local_param=True,
                                   explore_other_level=False)
        curr_id = params.parentContainer.getCurrentId()
        assert curr_id in params.threadLocalVar

        params.flush()

        assert not params.hasParameter("plop",
                                       local_param=True,
                                       explore_other_level=False)
        curr_id = params.parentContainer.getCurrentId()
        assert curr_id not in params.threadLocalVar

    # flushVariableLevelForThisThread, flush parameter that exist for the
    # current thread and at global level
    def test_parameterManager69(self):
        params = ParameterManager()
        params.setParameter("plap", Parameter("tata"), local_param=False)
        params.setParameter("plop", Parameter("titi"), local_param=True)

        assert params.hasParameter("plap",
                                   local_param=False,
                                   explore_other_level=False)
        assert params.hasParameter("plop",
                                   local_param=True,
                                   explore_other_level=False)
        curr_id = params.parentContainer.getCurrentId()
        assert curr_id in params.threadLocalVar

        params.flush()

        assert params.hasParameter("plap",
                                   local_param=False,
                                   explore_other_level=False)
        assert not params.hasParameter("plop",
                                       local_param=True,
                                       explore_other_level=False)
        curr_id = params.parentContainer.getCurrentId()
        assert curr_id not in params.threadLocalVar

    # flushVariableLevelForThisThread, flush parameter that exist for the
    # current thread and for others thread
    def test_parameterManager70(self):
        params = ParameterManager()

        # construct fake other var
        params.setParameter("plop", Parameter("titi"), local_param=True)
        key = params.parentContainer.getCurrentId()
        name_set = params.threadLocalVar[key]
        del params.threadLocalVar[key]
        params.threadLocalVar["ANY_KEY"] = name_set

        result = params.mltries.advancedSearch(("plop",), True)
        parameter_node = result.getValue()
        param = parameter_node.getLocalVar(key)
        parameter_node.unsetLocalVar(key)
        parameter_node.setLocalVar("ANY_KEY", param)

        params.setParameter("plip", Parameter("tutu"), local_param=True)

        assert params.hasParameter("plip",
                                   local_param=True,
                                   explore_other_level=True)
        assert not params.hasParameter("plop",
                                       local_param=True,
                                       explore_other_level=True)
        curr_id = params.parentContainer.getCurrentId()
        assert curr_id in params.threadLocalVar

        params.flush()

        assert not params.hasParameter("plip",
                                       local_param=True,
                                       explore_other_level=True)
        assert not params.hasParameter("plop",
                                       local_param=True,
                                       explore_other_level=True)

        curr_id = params.parentContainer.getCurrentId()
        assert curr_id not in params.threadLocalVar

        result = params.mltries.advancedSearch(("plop",), True)
        parameter_node = result.getValue()
        assert parameter_node.hasLocalVar("ANY_KEY")

    # #

    # buildDictionnary, search with invalid string
    def test_parameterManager71(self):
        params = ParameterManager()
        with pytest.raises(ParameterException):
            params.buildDictionnary(object())

    # buildDictionnary, local exists + local_param=True +
    # explore_other_level=True
    def test_parameterManager72(self):
        params = ParameterManager()
        p1 = params.setParameter("aa.bb.cc",
                                 Parameter("titi"),
                                 local_param=True)
        p2 = params.setParameter("ab.ac.cd",
                                 Parameter("tata"),
                                 local_param=True)
        p3 = params.setParameter("aa.plop",
                                 Parameter("toto"),
                                 local_param=True)

        result = params.buildDictionnary("",
                                         local_param=True,
                                         explore_other_level=True)

        assert result == {"aa.bb.cc": p1, "ab.ac.cd": p2, "aa.plop": p3}

    # buildDictionnary, local exists + local_param=True +
    # explore_other_level=False
    def test_parameterManager73(self):
        params = ParameterManager()
        p1 = params.setParameter("aa.bb.cc",
                                 Parameter("titi"),
                                 local_param=True)
        p2 = params.setParameter("ab.ac.cd",
                                 Parameter("tata"),
                                 local_param=True)
        p3 = params.setParameter("aa.plop",
                                 Parameter("toto"),
                                 local_param=True)

        result = params.buildDictionnary("",
                                         local_param=True,
                                         explore_other_level=False)

        assert result == {"aa.bb.cc": p1, "ab.ac.cd": p2, "aa.plop": p3}

    # buildDictionnary, global exists + local_param=True +
    # explore_other_level=True
    def test_parameterManager74(self):
        params = ParameterManager()
        p1 = params.setParameter("uu.vv.ww",
                                 Parameter("plap"),
                                 local_param=False)
        p2 = params.setParameter("uv.vw.wx",
                                 Parameter("plop"),
                                 local_param=False)
        p3 = params.setParameter("uu.titi",
                                 Parameter("plup"),
                                 local_param=False)

        result = params.buildDictionnary("",
                                         local_param=True,
                                         explore_other_level=True)

        assert result == {"uu.vv.ww": p1, "uv.vw.wx": p2, "uu.titi": p3}

    # buildDictionnary, global exists + local_param=True +
    # explore_other_level=False
    def test_parameterManager75(self):
        params = ParameterManager()
        params.setParameter("uu.vv.ww",
                            Parameter("plap"),
                            local_param=False)
        params.setParameter("uv.vw.wx",
                            Parameter("plop"),
                            local_param=False)
        params.setParameter("uu.titi",
                            Parameter("plup"),
                            local_param=False)

        result = params.buildDictionnary("",
                                         local_param=True,
                                         explore_other_level=False)

        assert result == {}

    # buildDictionnary, local exists + local_param=False +
    # explore_other_level=True
    def test_parameterManager76(self):
        params = ParameterManager()
        p1 = params.setParameter("aa.bb.cc",
                                 Parameter("titi"),
                                 local_param=True)
        p2 = params.setParameter("ab.ac.cd",
                                 Parameter("tata"),
                                 local_param=True)
        p3 = params.setParameter("aa.plop",
                                 Parameter("toto"),
                                 local_param=True)

        result = params.buildDictionnary("",
                                         local_param=False,
                                         explore_other_level=True)

        assert result == {"aa.bb.cc": p1, "ab.ac.cd": p2, "aa.plop": p3}

    # buildDictionnary, local exists + local_param=False +
    # explore_other_level=False
    def test_parameterManager77(self):
        params = ParameterManager()
        params.setParameter("aa.bb.cc",
                            Parameter("titi"),
                            local_param=True)
        params.setParameter("ab.ac.cd",
                            Parameter("tata"),
                            local_param=True)
        params.setParameter("aa.plop",
                            Parameter("toto"),
                            local_param=True)

        result = params.buildDictionnary("",
                                         local_param=False,
                                         explore_other_level=False)

        assert result == {}

    # buildDictionnary, global exists + local_param=False +
    # explore_other_level=True
    def test_parameterManager78(self):
        params = ParameterManager()
        p1 = params.setParameter("uu.vv.ww",
                                 Parameter("plap"),
                                 local_param=False)
        p2 = params.setParameter("uv.vw.wx",
                                 Parameter("plop"),
                                 local_param=False)
        p3 = params.setParameter("uu.titi",
                                 Parameter("plup"),
                                 local_param=False)

        result = params.buildDictionnary("",
                                         local_param=False,
                                         explore_other_level=True)

        assert result == {"uu.vv.ww": p1, "uv.vw.wx": p2, "uu.titi": p3}

    # buildDictionnary, global exists + local_param=False +
    # explore_other_level=False
    def test_parameterManager79(self):
        params = ParameterManager()
        p1 = params.setParameter("uu.vv.ww",
                                 Parameter("plap"),
                                 local_param=False)
        p2 = params.setParameter("uv.vw.wx",
                                 Parameter("plop"),
                                 local_param=False)
        p3 = params.setParameter("uu.titi",
                                 Parameter("plup"),
                                 local_param=False)

        result = params.buildDictionnary("",
                                         local_param=False,
                                         explore_other_level=False)

        assert result == {"uu.vv.ww": p1, "uv.vw.wx": p2, "uu.titi": p3}

    # buildDictionnary, nothing exists + local_param=True +
    # explore_other_level=True
    def test_parameterManager80(self):
        params = ParameterManager()
        result = params.buildDictionnary("",
                                         local_param=True,
                                         explore_other_level=True)
        assert result == {}

    # buildDictionnary, nothing exists + local_param=True +
    # explore_other_level=False
    def test_parameterManager81(self):
        params = ParameterManager()
        result = params.buildDictionnary("",
                                         local_param=True,
                                         explore_other_level=False)
        assert result == {}

    # buildDictionnary, nothing exists + local_param=False +
    # explore_other_level=True
    def test_parameterManager82(self):
        params = ParameterManager()
        result = params.buildDictionnary("",
                                         local_param=False,
                                         explore_other_level=True)
        assert result == {}

    # buildDictionnary, nothing exists + local_param=False +
    # explore_other_level=False
    def test_parameterManager83(self):
        params = ParameterManager()
        result = params.buildDictionnary("",
                                         local_param=False,
                                         explore_other_level=False)
        assert result == {}

    # buildDictionnary, local + global exists + local_param=False +
    # explore_other_level=True  (mixe several cases)
    def test_parameterManager84(self):
        params = ParameterManager()
        params.setParameter("aa.bb.cc",
                            Parameter("titi"),
                            local_param=True)
        p2 = params.setParameter("ab.ac.cd",
                                 Parameter("tata"),
                                 local_param=True)
        p3 = params.setParameter("aa.plop",
                                 Parameter("toto"),
                                 local_param=True)
        p4 = params.setParameter("aa.bb.cc",
                                 Parameter("plap"),
                                 local_param=False)
        p5 = params.setParameter("uv.vw.wx",
                                 Parameter("plop"),
                                 local_param=False)
        p6 = params.setParameter("uu.titi",
                                 Parameter("plup"),
                                 local_param=False)

        result = params.buildDictionnary("",
                                         local_param=False,
                                         explore_other_level=True)

        assert result == {"aa.bb.cc": p4,
                          "ab.ac.cd": p2,
                          "aa.plop": p3,
                          "uv.vw.wx": p5,
                          "uu.titi": p6}

    # buildDictionnary, local + global exists + local_param=False +
    # explore_other_level=False (mixe several cases)
    def test_parameterManager85(self):
        params = ParameterManager()
        params.setParameter("aa.bb.cc",
                            Parameter("titi"),
                            local_param=True)
        params.setParameter("ab.ac.cd",
                            Parameter("tata"),
                            local_param=True)
        params.setParameter("aa.plop",
                            Parameter("toto"),
                            local_param=True)
        p4 = params.setParameter("aa.bb.cc",
                                 Parameter("plap"),
                                 local_param=False)
        p5 = params.setParameter("uv.vw.wx",
                                 Parameter("plop"),
                                 local_param=False)
        p6 = params.setParameter("uu.titi",
                                 Parameter("plup"),
                                 local_param=False)

        result = params.buildDictionnary("",
                                         local_param=False,
                                         explore_other_level=False)

        assert result == {"aa.bb.cc": p4, "uv.vw.wx": p5, "uu.titi": p6}

    # buildDictionnary, global + local exists + local_param=True +
    # explore_other_level=True   (mixe several cases)
    def test_parameterManager86(self):
        params = ParameterManager()
        p1 = params.setParameter("aa.bb.cc",
                                 Parameter("titi"),
                                 local_param=True)
        p2 = params.setParameter("ab.ac.cd",
                                 Parameter("tata"),
                                 local_param=True)
        p3 = params.setParameter("aa.plop",
                                 Parameter("toto"),
                                 local_param=True)
        params.setParameter("aa.bb.cc",
                            Parameter("plap"),
                            local_param=False)
        p5 = params.setParameter("uv.vw.wx",
                                 Parameter("plop"),
                                 local_param=False)
        p6 = params.setParameter("uu.titi",
                                 Parameter("plup"),
                                 local_param=False)

        result = params.buildDictionnary("",
                                         local_param=True,
                                         explore_other_level=True)

        assert result == {"aa.bb.cc": p1,
                          "ab.ac.cd": p2,
                          "aa.plop": p3,
                          "uv.vw.wx": p5,
                          "uu.titi": p6}

    # buildDictionnary, global + local exists + local_param=True +
    # explore_other_level=False  (mixe several cases)
    def test_parameterManager87(self):
        params = ParameterManager()
        p1 = params.setParameter("aa.bb.cc",
                                 Parameter("titi"),
                                 local_param=True)
        p2 = params.setParameter("ab.ac.cd",
                                 Parameter("tata"),
                                 local_param=True)
        p3 = params.setParameter("aa.plop",
                                 Parameter("toto"),
                                 local_param=True)
        params.setParameter("aa.bb.cc",
                            Parameter("plap"),
                            local_param=False)
        params.setParameter("uv.vw.wx",
                            Parameter("plop"),
                            local_param=False)
        params.setParameter("uu.titi",
                            Parameter("plup"),
                            local_param=False)

        result = params.buildDictionnary("",
                                         local_param=True,
                                         explore_other_level=False)

        assert result == {"aa.bb.cc": p1, "ab.ac.cd": p2, "aa.plop": p3}

    def test_getLoaderNodesLoaderDoesNotExist(self):
        l = self.params.getLoaderNodes("loader A")
        assert len(l) == 0

    def test_getLoaderNodesLoaderExist(self):
        p = Parameter("titi")
        self.params.setParameter("plop",
                                 p,
                                 local_param=False,
                                 origin_loader="loader A")

        l = self.params.getLoaderNodes("loader A")
        assert len(l) == 1


class CopyableObject(object):
    def __init__(self, to_store):
        self.to_store = to_store

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other.to_store == self.to_store)

    def __hash__(self):
        return hash(self.to_store)


# # parameters test # #
class TestParameter(object):
    # test value/getvalue on constructor

    def test_parameterConstructor1(self):
        with pytest.raises(ParameterException):
            Parameter(None, object())

    def test_parameterConstructor2(self):
        p = Parameter(None)
        assert isinstance(p.settings, LocalSettings)

    def test_parameterConstructor3(self):
        ls = LocalSettings()
        p = Parameter(None, settings=ls)
        assert p.settings is ls

    def test_parameterConstructor4(self):
        ls = LocalSettings()
        ls.setReadOnly(True)
        o = object()
        p = Parameter(o, settings=ls)
        assert p.getValue() is o
        with pytest.raises(ParameterException):
            p.setValue("plop")

    # test setValue/getValue
    def test_parameter1(self):
        p = Parameter(None)
        assert p.getValue() is None
        p.setValue(42)
        assert p.getValue() == 42

    # test enableLocal
    def test_parameter2(self):
        p = Parameter(None)
        sett = p.settings
        assert isinstance(sett, LocalSettings)
        p.enableLocal()
        assert sett is p.settings

    # test enableGlobal
    def test_parameter3(self):
        p = Parameter(None)
        p.enableGlobal()
        sett = p.settings
        assert isinstance(sett, GlobalSettings)
        p.enableGlobal()
        assert sett is p.settings

    # test from global to local
    def test_parameter4(self):
        p = Parameter(None)
        p.settings.setRemovable(True)
        p.settings.setReadOnly(True)
        p.enableLocal()
        assert isinstance(p.settings, LocalSettings)
        assert p.settings.isReadOnly()
        assert p.settings.isRemovable()

    # test from global to local
    def test_parameter5(self):
        p = Parameter(None)
        p.settings.setRemovable(False)
        p.settings.setReadOnly(False)
        p.enableLocal()
        assert isinstance(p.settings, LocalSettings)
        assert not p.settings.isReadOnly()
        assert not p.settings.isRemovable()

    # test from local to global
    def test_parameter6(self):
        p = Parameter(None)
        p.enableLocal()
        assert isinstance(p.settings, LocalSettings)
        p.settings.setRemovable(False)
        p.settings.setReadOnly(False)
        p.enableGlobal()
        assert isinstance(p.settings, GlobalSettings)
        assert not p.settings.isReadOnly()
        assert not p.settings.isRemovable()

    # test from local to global
    def test_parameter7(self):
        p = Parameter(None)
        p.enableLocal()
        assert isinstance(p.settings, LocalSettings)
        p.settings.setRemovable(True)
        p.settings.setReadOnly(True)
        p.enableGlobal()
        assert isinstance(p.settings, GlobalSettings)
        assert p.settings.isReadOnly()
        assert p.settings.isRemovable()

    # test str
    def test_parameter8(self):
        p = Parameter(42)
        assert str(p) == "42"

    # test repr
    def test_parameter9(self):
        p = Parameter(42)
        assert repr(p) == "Parameter: 42"

    # test hash
    def test_parameter10(self):
        p1 = Parameter(42)
        p2 = Parameter(42)
        assert hash(p1) == hash(p2)
        p3 = Parameter(43)
        assert hash(p1) != hash(p3)
        p4 = Parameter(42)
        p4.settings.setReadOnly(True)
        assert hash(p1) != hash(p4)

    def test_clone(self):
        p = Parameter(CopyableObject(uuid4()))
        p_clone = p.clone()

        assert p is not p_clone
        assert p.settings is not p_clone
        assert p.getValue() is not p_clone.getValue()
        assert p.getValue() == p_clone.getValue()
        assert hash(p.settings) == hash(p_clone.settings)
        assert hash(p) == hash(p_clone)
