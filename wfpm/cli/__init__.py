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
from wfpm import __version__ as ver
from .init_cmd import init_cmd
from .install_cmd import install_cmd
from .list_cmd import list_cmd
from .uninstall_cmd import uninstall_cmd
from .outdated_cmd import outdated_cmd
from .test_cmd import test_cmd
from wfpm.config import Config


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f'wfpm {ver}')
    ctx.exit()


@click.group()
@click.option('--debug/--no-debug', '-d', is_flag=True, default=False,
              help='Show debug information in STDERR.')
@click.option('--version', '-v', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help='Show wfpm version.')
@click.pass_context
def main(ctx, debug):
    # initializing ctx.obj
    ctx.obj = {}
    ctx.obj['DEBUG'] = debug

    # gether WFPM config / project / package info
    ctx.obj['CONFIG'] = Config()


@main.command()
@click.pass_context
def init(ctx):
    """
    Initialize a package with necessary scaffolding.
    """
    init_cmd(ctx)


@main.command()
@click.pass_context
def install(ctx):
    """
    Install packages.
    """
    install_cmd(ctx)


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
    List outdated packages.
    """
    outdated_cmd(ctx)


@main.command()
@click.pass_context
def test(ctx):
    """
    Run tests.
    """
    test_cmd(ctx)
