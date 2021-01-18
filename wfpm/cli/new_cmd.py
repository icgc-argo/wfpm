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
from click import echo
from cookiecutter.main import cookiecutter
from ..pkg_templates import tool_tmplt
from ..pkg_templates import workflow_tmplt
from ..pkg_templates import function_tmplt
from ..utils import run_cmd


def new_cmd(ctx, pkg_type):
    project = ctx.obj['PROJECT']
    if not project.root:
        echo("Not in a package project directory.")
        ctx.abort()

    if project.root != os.getcwd():
        echo(f"Must run this command under the project root dir: {project.root}")
        ctx.abort()

    if pkg_type == 'tool':
        path = cookiecutter(tool_tmplt)

    elif pkg_type == 'workflow':
        path = cookiecutter(workflow_tmplt)

    elif pkg_type == 'function':
        echo("Not implemented yet")
        ctx.exit()

    # create symlinks for 'wfpr_modules'
    cmd = f"cd {path} && ln -s ../wfpr_modules && cd tests && ln -s ../wfpr_modules"
    run_cmd(cmd)
    echo(f"New package created in: {os.path.basename(path)}")
