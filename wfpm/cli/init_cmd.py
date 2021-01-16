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


def init_cmd(ctx):
    cwd = os.getcwd()

    # make sure the current directory is empty
    if os.listdir(cwd):
        echo('Current directory not empty, exit now.')
        ctx.exit(0)

    # create the project scaffold in a temp dir first then move to cwd
    with tempfile.TemporaryDirectory() as tmpdirname:
        try:
            os.chdir(tmpdirname)

            project_dir = cookiecutter(project_tmplt)
            copy_tree(project_dir, cwd)

            echo(f"Project initialized in: {cwd}")

        except Exception as ex:
            echo("Project initiation failed: %s" % ex)
            ctx.exit(1)

        finally:
            os.chdir(cwd)

    subprocess.run(['git', 'init'], check=True)
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', 'commit', '-m', 'initial commit'], check=True)
    subprocess.run(['git', 'branch', '-M', 'main'], check=True)

    echo(f"Project initialized and first commit done in: {cwd}")
