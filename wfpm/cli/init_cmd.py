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
import tempfile
import subprocess
from distutils.dir_util import copy_tree
from click import echo
from cookiecutter.main import cookiecutter
from ..pkg_templates import project_tmplt


def init_cmd(ctx, git_commit):
    cwd = os.getcwd()

    # make sure the current directory is empty
    if os.listdir(cwd):
        echo('Current directory not empty, exit now.')
        ctx.exit(0)

    success = False

    # create the project scaffold in a temp dir
    with tempfile.TemporaryDirectory() as tmpdirname:
        try:
            os.chdir(tmpdirname)

            project_dir = cookiecutter(project_tmplt)
            copy_tree(project_dir, cwd)

            success = True
            echo(f"Project initialized in: {cwd}")

        finally:
            os.chdir(cwd)

    if success and git_commit:
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'initial commit'], check=True)
        subprocess.run(['git', 'branch', '-M', 'main'], check=True)
