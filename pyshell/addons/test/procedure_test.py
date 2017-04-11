#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2017  Jonathan Delvaux <pyshell@djoproject.net>

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

import os

from pyshell.addons.parameter import _loaders as parameter_loader
from pyshell.addons.procedure import _postProcess
from pyshell.addons.procedure import _process
from pyshell.addons.procedure import startNamedProcedure
from pyshell.addons.procedure import startProcedure
from pyshell.addons.system import _loaders as system_loader
from pyshell.command.procedure import FileProcedure
from pyshell.control import ControlCenter
from pyshell.register.loader.file import FileLoader
from pyshell.system.parameter.procedure import ProcedureParameter
from pyshell.utils.constants import ENABLE_ON_POST_PROCESS
from pyshell.utils.constants import ENABLE_ON_PRE_PROCESS
from pyshell.utils.constants import ENABLE_ON_PROCESS


class TestProcedure(object):
    def setup_method(self, method):
        self.params = ControlCenter()
        addons = self.params.getAddonManager()

        # disable file saving/loading
        system_loader.unbindLoaderToProfile(FileLoader, None)

        # load the default addon
        addons["pyshell.addons.system"] = system_loader
        system_loader.load(self.params)

        # load the parameter addon
        addons["pyshell.addons.parameter"] = parameter_loader
        parameter_loader.load(self.params)

        # create procedure path
        self.path = os.path.abspath(__file__)
        self.path = os.path.dirname(self.path)
        self.path = os.path.join(self.path, "ressources", "create_env")

    def teardown_method(self, method):
        parameter_loader.unload(self.params)
        system_loader.unload(self.params)

    def test_startNamedProcedureExecutionOnPreProcess(self):
        p = ProcedureParameter(self.path)
        p.settings.setErrorGranularity(-1)
        p.settings.setEnableOn(ENABLE_ON_PRE_PROCESS)
        exchange = {}
        startNamedProcedure(
            p, args=(), parameters=self.params, exchange=exchange)
        assert self.params.getEnvironmentManager().hasParameter("toto")
        assert exchange["enable_on"] == ENABLE_ON_PRE_PROCESS

    def test_startNamedProcedureExecutionOnOtherThanPreProcess(self):
        p = ProcedureParameter(self.path)
        p.settings.setErrorGranularity(-1)
        p.settings.setEnableOn(ENABLE_ON_PROCESS)
        exchange = {}
        startNamedProcedure(
            p, args=(), parameters=self.params, exchange=exchange)
        assert not self.params.getEnvironmentManager().hasParameter("toto")
        assert exchange["enable_on"] == ENABLE_ON_PROCESS

    def test_startProcedureExecutionOnPreProcess(self):
        exchange = {}
        startProcedure(file_path=self.path,
                       args=(),
                       granularity=-1,
                       enable_on=ENABLE_ON_PRE_PROCESS,
                       parameters=self.params,
                       exchange=exchange)
        assert self.params.getEnvironmentManager().hasParameter("toto")
        assert exchange["enable_on"] == ENABLE_ON_PRE_PROCESS

    def test_startProcedureExecutionOnOtherThanPreProcess(self):
        exchange = {}
        startProcedure(file_path=self.path,
                       args=(),
                       granularity=-1,
                       enable_on=ENABLE_ON_POST_PROCESS,
                       parameters=self.params,
                       exchange=exchange)
        assert not self.params.getEnvironmentManager().hasParameter("toto")
        assert exchange["enable_on"] == ENABLE_ON_POST_PROCESS

    def test_processOnProcess(self):
        procedure = FileProcedure(file_path=self.path,
                                  execute_on=ENABLE_ON_PROCESS,
                                  granularity=-1)

        exchange = {}
        exchange["procedure"] = procedure
        exchange["enable_on"] = ENABLE_ON_PROCESS

        _process(args=(), parameters=self.params, exchange=exchange)
        assert self.params.getEnvironmentManager().hasParameter("toto")

    def test_processOnOtherThanProcess(self):
        procedure = FileProcedure(file_path=self.path,
                                  execute_on=ENABLE_ON_PRE_PROCESS,
                                  granularity=-1)

        exchange = {}
        exchange["procedure"] = procedure
        exchange["enable_on"] = ENABLE_ON_PRE_PROCESS

        _process(args=(), parameters=self.params, exchange=exchange)
        assert not self.params.getEnvironmentManager().hasParameter("toto")

    def test_postProcessOnPostProcess(self):
        procedure = FileProcedure(file_path=self.path,
                                  execute_on=ENABLE_ON_POST_PROCESS,
                                  granularity=-1)

        exchange = {}
        exchange["procedure"] = procedure
        exchange["enable_on"] = ENABLE_ON_POST_PROCESS

        _postProcess(args=(), parameters=self.params, exchange=exchange)
        assert self.params.getEnvironmentManager().hasParameter("toto")

    def test_postProcessOnOtherThanPostProcess(self):
        procedure = FileProcedure(file_path=self.path,
                                  execute_on=ENABLE_ON_PROCESS,
                                  granularity=-1)

        exchange = {}
        exchange["procedure"] = procedure
        exchange["enable_on"] = ENABLE_ON_PROCESS

        _postProcess(args=(), parameters=self.params, exchange=exchange)
        assert not self.params.getEnvironmentManager().hasParameter("toto")
