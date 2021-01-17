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

from . import RepoBase
from ..utils import run_cmd


class Git(RepoBase):
    repotype = 'git'

    def __init__(self):
        super().__init__(self)

    def root(self):
        stdout, stderr, returncode = run_cmd('git rev-parse --show-toplevel')
        if returncode:
            if 'not a git repository' in stderr:
                raise Exception('Not in a git repository')
        else:
            return stdout  # abspath of the git repo
