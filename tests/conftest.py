# -*- coding: utf-8 -*-

"""
    Copyright (c) 2021, Ontario Institute for Cancer Research (OICR).

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Authors:
        Junjun Zhang <junjun.zhang@oicr.on.ca>
"""

import os
import pytest
from wfpm.utils import run_cmd


@pytest.fixture(scope="session", autouse=True)
def setup_git_user_info():
    stdout, stderr, ret = run_cmd('git config --list | grep user')
    if 'user.email' not in stdout or 'user.name' not in stdout:
        cmd = 'git config --global user.name "$USER" && git config --global user.email "user@example.com"'
        run_cmd(cmd)


@pytest.fixture(scope="module")
def workdir(tmpdir_factory):
    dir = tmpdir_factory.mktemp("workdir")
    os.chdir(dir)
    return dir
