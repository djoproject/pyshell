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

import errno
import os
from tempfile import NamedTemporaryFile
from uuid import uuid1

import pytest

from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.loader.exception import UnloadException
from pyshell.register.loader.file import FileLoader
from pyshell.register.profile.file import FileLoaderProfile
from pyshell.register.profile.globale import GlobalProfile
from pyshell.register.result.command import CommandResult
from pyshell.register.utils.addon import AddonInformation
from pyshell.system.container import ParameterContainer
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.environment import EnvironmentParameterManager
from pyshell.system.setting.environment import EnvironmentGlobalSettings
from pyshell.system.variable import VariableParameterManager
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import ENVIRONMENT_CONFIG_DIRECTORY_KEY
from pyshell.utils.constants import VARIABLE_ATTRIBUTE_NAME


class TestFileMisc(object):

    def test_createProfileInstance(self):
        profile = FileLoader.createProfileInstance()
        assert isinstance(profile, FileLoaderProfile)


class TestFileGetFilePath(object):

    def setup_method(self, method):
        self.addon_information = AddonInformation('test.loader.file')
        self.global_profile = GlobalProfile(
            'profile_name', self.addon_information)
        self.profile = FileLoader.createProfileInstance()
        self.profile.setGlobalProfile(self.global_profile)

    def test_getFilePathNoContainer(self):
        path = FileLoader.getFilePath(parameter_container=None,
                                      profile_object=self.profile)
        assert path == "/home/djo/.pyshell/test.loader.file.profile_name.pys"

    def test_getFilePathNoEnv(self):
        pc = ParameterContainer()
        path = FileLoader.getFilePath(parameter_container=pc,
                                      profile_object=self.profile)
        assert path == "/home/djo/.pyshell/test.loader.file.profile_name.pys"

    def test_getFilePathNoParam(self):
        pc = ParameterContainer()
        pc.registerParameterManager(
            ENVIRONMENT_ATTRIBUTE_NAME,
            EnvironmentParameterManager(pc))
        path = FileLoader.getFilePath(parameter_container=pc,
                                      profile_object=self.profile)
        assert path == "/home/djo/.pyshell/test.loader.file.profile_name.pys"

    def test_getFilePathNormalCase(self):
        pc = ParameterContainer()
        pc.registerParameterManager(
            ENVIRONMENT_ATTRIBUTE_NAME,
            EnvironmentParameterManager(pc))
        env = getattr(pc, ENVIRONMENT_ATTRIBUTE_NAME)
        ctype = DefaultInstanceArgChecker.getStringArgCheckerInstance()
        env.setParameter(
            ENVIRONMENT_CONFIG_DIRECTORY_KEY,
            EnvironmentParameter(value="/home/toto/",
                                 settings=EnvironmentGlobalSettings(
                                     checker=ctype)),
            local_param=False)
        path = FileLoader.getFilePath(parameter_container=pc,
                                      profile_object=self.profile)
        assert path == "/home/toto/test.loader.file.profile_name.pys"


class FileLoaderForTest(FileLoader):
    TEST_PATH = None

    @staticmethod
    def getFilePath(parameter_container, profile_object):
        return FileLoaderForTest.TEST_PATH


class TestFileLoad(object):

    def setup_method(self, method):
        FileLoaderForTest.TEST_PATH = None

    def test_nonePath(self):
        FileLoaderForTest.load(None, None)

    def test_pathDoesNotExist(self):
        FileLoaderForTest.TEST_PATH = os.path.join('~', str(uuid1()))
        FileLoaderForTest.load(None, None)

    def test_validCase(self):
        pc = ParameterContainer()
        pc.registerParameterManager(VARIABLE_ATTRIBUTE_NAME,
                                    VariableParameterManager(pc))

        with NamedTemporaryFile() as file_descr:
            FileLoaderForTest.TEST_PATH = file_descr.name
            FileLoaderForTest.load(None, pc)


class ResultAa(AbstractLoader):
    pass


class ResultBb(AbstractLoader):
    pass


class ResultCc(AbstractLoader):
    pass


class TestFileUnload(object):

    def setup_method(self, method):
        FileLoaderForTest.TEST_PATH = None
        self.addon_information = AddonInformation('test.loader.file')
        self.global_profile = GlobalProfile(
            'profile_name', self.addon_information)
        self.profile = FileLoader.createProfileInstance()
        self.profile.setGlobalProfile(self.global_profile)

    def test_nonePath(self):
        with pytest.raises(UnloadException):
            FileLoaderForTest.unload(self.profile, None)

    def test_noResultAndPathExists(self):
        file_descr = NamedTemporaryFile()
        assert os.path.exists(file_descr.name)
        FileLoaderForTest.TEST_PATH = file_descr.name
        FileLoaderForTest.unload(self.profile, None)
        assert not os.path.exists(file_descr.name)

        try:
            file_descr.close()
        except OSError as ose:
            assert ose.errno == errno.ENOENT

    def test_noResultAndPathDoesNotExist(self):
        FileLoaderForTest.TEST_PATH = os.path.join('~', str(uuid1()))
        FileLoaderForTest.unload(self.profile, None)

    def test_validCase(self):
        result1 = CommandResult(["toto", "titi"],
                                "result1",
                                set(["addon1", "addon2"]))
        self.global_profile.postResult(ResultAa, result1)

        result2 = CommandResult(["plip", "plap"],
                                "result2",
                                set(["addon1", "addon3"]))
        self.global_profile.postResult(ResultBb, result2)

        result3 = CommandResult(["glip", "glop"], "result3")
        self.global_profile.postResult(ResultCc, result3)

        expected_addon = ["addon load addon1",
                          "addon load addon2",
                          "addon load addon3"]
        expected_result1 = ["toto", "titi"]
        expected_result2 = ["plip", "plap"]
        expected_result3 = ["glip", "glop"]

        current_expected = expected_addon
        expecteds = [expected_result1, expected_result2, expected_result3]

        with NamedTemporaryFile(mode="r") as file_descr:
            FileLoaderForTest.TEST_PATH = file_descr.name
            FileLoaderForTest.unload(self.profile, None)

            index = 0
            for line in file_descr.readlines():
                line = line.rstrip()

                if len(line) == 0:
                    continue

                # the current expected block is empty ? pick the next one
                if index >= len(current_expected):
                    index = 0
                    for next_expected in expecteds:
                        if next_expected[index] == line:
                            current_expected = next_expected
                            break
                    else:
                        # no next expected block was found
                        print(line)  # noqa
                        assert False

                assert line == current_expected[index]
                index += 1
