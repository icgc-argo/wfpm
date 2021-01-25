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
import click
from wfpm import __version__ as ver
from .init_cmd import init_cmd
from .new_cmd import new_cmd
from .install_cmd import install_cmd
from .list_cmd import list_cmd
from .uninstall_cmd import uninstall_cmd
from .outdated_cmd import outdated_cmd
from .test_cmd import test_cmd
from wfpm.config import Config
from wfpm.project import Project


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f'wfpm {ver}')
    ctx.exit()


def initialize(ctx, debug):
    ctx.obj = dict()
    ctx.obj['CONFIG'] = Config(debug)
    ctx.obj['PROJECT'] = Project(config=ctx.obj['CONFIG'])


@click.group()
@click.option('--debug/--no-debug', '-d', is_flag=True, default=False,
              help='Show debug information in STDERR.')
@click.option('--version', '-v', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help='Show wfpm version.')
@click.pass_context
def main(ctx, debug):
    # initializing the project
    initialize(ctx, debug)


@main.command()
@click.pass_context
def init(ctx):
    """
    Start a workflow package project with necessary scaffolds.
    """
    if ctx.obj['PROJECT'].root:
        click.echo(f"Already under a project directory: {ctx.obj['PROJECT'].root}")
        ctx.abort()

    init_cmd(ctx)


@main.command()
@click.argument(
    'pkg_type', nargs=1,
    type=click.Choice(['tool', 'workflow', 'function'], case_sensitive=False)
)
@click.argument('pkg_name', nargs=1)
@click.pass_context
def new(ctx, pkg_type, pkg_name):
    """
    Start a new package with necessary scaffolds.
    """
    new_cmd(ctx, pkg_type, pkg_name)


@main.command()
## diable this for now ## @click.argument('pkgs', nargs=-1, required=False)
@click.option('--force', '-f', is_flag=True, help='Force installation even already installed.')
@click.option('--include-tests', '-t', is_flag=True, help='Force installation even already installed.')
@click.pass_context
def install(ctx, force, include_tests):
    """
    Install packages.
    """
    install_cmd(ctx, force, include_tests)


@main.command()
@click.pass_context
def list(ctx):
    """
    List installed packages.
    """
    list_cmd(ctx)


@main.command()
@click.pass_context
def uninstall(ctx):
    """
    Uninstall packages.
    """
    uninstall_cmd(ctx)


@main.command()
@click.pass_context
def outdated(ctx):
    """
    List outdated dependent packages.
    """
    outdated_cmd(ctx)


@main.command()
@click.pass_context
def test(ctx):
    """
    Run tests.
    """
    test_cmd(ctx)
