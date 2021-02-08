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

import sys
from click import echo
from wfpm.project import Project


def nextver_cmd(
    project: Project = None,
    pkg: str = None,
    version: str = None
):
    echo('To be implemented, check back soon.\n')
    # need to make sure local repo is sync'd with remote before proceeding
    # checkout from a release tag: git checkout tags/fastqc.v0.1.0 -b fastqc@0.1.3

    sys.exit()
