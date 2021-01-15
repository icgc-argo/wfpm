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


import click
from cookiecutter.main import cookiecutter
from cookiecutter.config import get_user_config
from cookiecutter.replay import load
from ..pkg_templates import project_tmplt_path
from ..pkg_templates import tool_tmplt_path
from ..pkg_templates import workflow_tmplt_path
from ..pkg_templates import function_tmplt_path


def init_cmd(ctx):
    # click.echo(project_tmplt_path)
    cookiecutter(tool_tmplt_path)
