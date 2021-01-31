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
from .new_cmd import new_cmd
from .install_cmd import install_cmd
from .list_cmd import list_cmd
from .uninstall_cmd import uninstall_cmd
from .outdated_cmd import outdated_cmd
from .test_cmd import test_cmd
from .config_cmd import config_cmd
from wfpm.project import Project


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
    # initializing the project
    ctx.obj = dict()
    try:
        ctx.obj['PROJECT'] = Project(debug=debug)
    except Exception as ex:
        click.echo(ex)
        ctx.exit(1)


@main.command()
@click.option('--conf-json', '-c', type=click.File('rb'),
              help='Optional config JSON with needed info to initialize a new project.')
@click.pass_context
def init(ctx, conf_json):
    """
    Start a workflow package project with necessary scaffolds.
    """
    if ctx.obj['PROJECT'].root:
        click.echo(f"Already under a project directory: {ctx.obj['PROJECT'].root}")
        ctx.abort()

    init_cmd(ctx, conf_json)


@main.command()
@click.argument(
    'pkg_type', nargs=1,
    type=click.Choice(['tool', 'workflow', 'function'], case_sensitive=False)
)
@click.argument('pkg_name', nargs=1)
@click.option('--conf-json', '-c', type=click.File('rb'),
              help='Optional config JSON with needed info to create a new package.')
@click.pass_context
def new(ctx, pkg_type, pkg_name, conf_json):
    """
    Start a new package with necessary scaffolds.
    """
    new_cmd(ctx, pkg_type, pkg_name, conf_json)


@main.command()
# diable this for now ## @click.argument('pkgs', nargs=-1, required=False)
@click.option('--force', '-f', is_flag=True, help='Force installation even already installed.')
@click.option('--skip-tests', '-T', is_flag=True, help='Not to run tests after installation.')
@click.pass_context
def install(ctx, force, skip_tests):
    """
    Install dependent packages.
    """
    install_cmd(ctx, force, skip_tests)


@main.command()
@click.pass_context
def list(ctx):
    """
    List local and installed dependent packages.
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


@main.command()
@click.option('--set', '-s', is_flag=True, help="Create global config file '.wfpmconf' under user home dir.")
@click.option('--force', '-f', is_flag=True, help="Force to overwrite.")
@click.pass_context
def config(ctx, set, force):
    """
    Show or set configuration for wfpm.
    """
    config_cmd(ctx, set=set, force=force)
