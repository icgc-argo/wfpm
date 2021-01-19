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
import subprocess
from click import echo
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException, FailedHookException
from ..pkg_templates import project_tmplt
from ..utils import run_cmd
from ..config import Config


def init_cmd(ctx):
    project = ctx.obj['PROJECT']
    if project.root:
        echo(f"Already in a package project directory: {project.root}")
        ctx.abort()

    try:
        project_dir = cookiecutter(project_tmplt)
        echo(f"Project initialized in: {os.path.basename(project_dir)}")
    except FailedHookException as ex:
        echo(f"Failed to initialize the project. {ex}")
        ctx.abort()
    except OutputDirExistsException as ex:
        echo(f"Failed to initialize the project. {ex}")
        ctx.abort()

    os.chdir(project_dir)

    # project initialized, now can get config from .wfpm file
    config = Config()

    cmd = "git init && git add . && git commit -m 'inital commit' && git branch -M main && " \
          f"git remote add origin git@{config.repo_server}:{config.repo_account}/{config.project_name}.git"

    out, err, ret = run_cmd(cmd)
    if ret != 0:
        echo("Git commands failed, please ensure 'git' is installed.")
        ctx.exit(1)
    else:
        echo(
            "Git repo initialized and first commit done. " + \
            f"When ready, you may push to {config.repo_server} using:\n" + \
            "git push -u origin main"
        )
