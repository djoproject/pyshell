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

import pytest

from tries import multiLevelTries

from pyshell.system.container import DummyParameterContainer
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.parameter import Parameter
from pyshell.system.parameter import ParameterManager
from pyshell.system.parameter import _buildExistingPathFromError
from pyshell.system.parameter import isAValidStringPath
from pyshell.system.settings import GlobalSettings
from pyshell.system.settings import LocalSettings
from pyshell.utils.exception import ParameterException


class TestParameter(object):

    def setup_method(self, method):
        self.params = ParameterManager()
        self.params.setParameter("aa.bb.cc", Parameter("plop"))
        self.params.setParameter("ab.bc.cd", Parameter("plip"))

    # # misc # #

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

    # # ParameterManager constructor # #

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
        assert self.params.extractParameter(p) is p

    # test extractParameter, with another parameter type
    def test_parameterManager15(self):
        assert isinstance(self.params.extractParameter(42), Parameter)

    # test extractParameter, with something else
    # (to try to instanciate an allowed type)
    def test_parameterManager16(self):
        with pytest.raises(ParameterException):
            self.params.extractParameter(EnvironmentParameter("plop"))

    ##

    # setParameter, local exists + local + existing is readonly
    def test_parameterManager17(self):
        param = self.params.setParameter("plop",
                                         Parameter("toto"),
                                         local_param=True)
        curr_id = self.params.parentContainer.getCurrentId()
        assert "plop" in self.params.threadLocalVar[curr_id]
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
        assert "plop" in self.params.threadLocalVar[curr_id]
        assert isinstance(param1.settings, LocalSettings)
        param1.settings.setRemovable(True)

        param2 = self.params.setParameter("plop",
                                          Parameter("titi"),
                                          local_param=True)
        curr_id = self.params.parentContainer.getCurrentId()
        assert "plop" in self.params.threadLocalVar[curr_id]
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
        assert "plop" in self.params.threadLocalVar[curr_id]
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
        assert "plop" in self.params.threadLocalVar[curr_id]
        assert isinstance(param2.settings, LocalSettings)
        assert param1 is not param2

    # setParameter, nothing exists + local
    def test_parameterManager21(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=True)
        curr_id = self.params.parentContainer.getCurrentId()
        assert "plop" in self.params.threadLocalVar[curr_id]
        assert isinstance(param.settings, LocalSettings)
        assert self.params.getParameter("plop") is param

    # setParameter, local exists + global + existing is readonly
    def test_parameterManager22(self):
        param1 = self.params.setParameter("plop",
                                          Parameter("titi"),
                                          local_param=True)
        curr_id = self.params.parentContainer.getCurrentId()
        assert "plop" in self.params.threadLocalVar[curr_id]
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
        assert "plop" in self.params.threadLocalVar[curr_id]
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
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=False)
        param.settings.addLoader("uhuh")
        param.settings.addLoader("ahah")
        param.settings.addLoader("uhuh")

        # self.assertTrue(hasattr(param.settings, "origin"))
        # self.assertTrue(hasattr(param.settings, "originArg"))
        assert hasattr(param.settings, "startingHash")

        param.settings.origin = "aaa"
        param.settings.originArg = "bbb"
        has = param.settings.startingHash

        param = self.params.setParameter("plop",
                                         Parameter("tata"),
                                         local_param=False)

        # self.assertEqual(param.settings.origin, "aaa")
        # self.assertEqual(param.settings.originArg, "bbb")
        assert param.settings.startingHash == has
        loaders = tuple(sorted(param.settings.getLoaders()))
        assert loaders == ("ahah", "uhuh",)

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
        param.settings.addLoader("load1")
        param.settings.setRemovable(False)
        with pytest.raises(ParameterException):
            self.params.unsetParameter("plop",
                                       local_param=False,
                                       explore_other_level=False)

    # unsetParameter, try to remove an existing global one, with loader
    # dependancies and force
    def test_parameterManagerUnsetParameter2(self):
        param = self.params.setParameter("plop",
                                         Parameter("titi"),
                                         local_param=False)
        param.settings.addLoader("load1")
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
        g, l = result.getValue()
        param = l[key]
        del l[key]
        l["ANY_KEY"] = param

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
        g, l = result.getValue()
        assert "ANY_KEY" in l

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

    # # parameters test # #

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

    # test from local to global
    def test_parameter4(self):
        p = Parameter(None)
        p.settings.setRemovable(True)
        p.settings.setReadOnly(True)
        p.enableGlobal()
        assert isinstance(p.settings, GlobalSettings)
        assert p.settings.isReadOnly()
        assert p.settings.isRemovable()

    # test from local to global
    def test_parameter5(self):
        p = Parameter(None)
        p.settings.setRemovable(False)
        p.settings.setReadOnly(False)
        p.enableGlobal()
        assert isinstance(p.settings, GlobalSettings)
        assert not p.settings.isReadOnly()
        assert not p.settings.isRemovable()

    # test from global to local
    def test_parameter6(self):
        p = Parameter(None)
        p.enableGlobal()
        assert isinstance(p.settings, GlobalSettings)
        p.settings.setRemovable(False)
        p.settings.setReadOnly(False)
        p.enableLocal()
        assert isinstance(p.settings, LocalSettings)
        assert not p.settings.isReadOnly()
        assert not p.settings.isRemovable()

    # test from global to local
    def test_parameter7(self):
        p = Parameter(None)
        p.enableGlobal()
        assert isinstance(p.settings, GlobalSettings)
        p.settings.setRemovable(True)
        p.settings.setReadOnly(True)
        p.enableLocal()
        assert isinstance(p.settings, LocalSettings)
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
