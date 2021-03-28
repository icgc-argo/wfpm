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
import traceback
from wfpm import __version__ as ver
from .init_cmd import init_cmd
from .new_cmd import new_cmd
from .install_cmd import install_cmd
from .list_cmd import list_cmd
from .uninstall_cmd import uninstall_cmd
from .outdated_cmd import outdated_cmd
from .test_cmd import test_cmd
from .workon_cmd import workon_cmd
from .nextver_cmd import nextver_cmd
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
        click.echo(f"Failed to create the project object: {ex}")
        traceback.print_exc()
        ctx.exit(1)


@main.command()
@click.option('--conf-json', '-c', type=click.File('rb'),
              help='Optional config JSON with needed info to initialize a new project.')
@click.pass_context
def init(ctx, conf_json):
    """
    Start a workflow package project with necessary scaffolds.
    """
    project = ctx.obj.get('PROJECT')
    if project.root:
        click.echo(f"Already under a project directory: {project.root}")
        ctx.abort()

    init_cmd(project, conf_json)


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
    project = ctx.obj.get('PROJECT')
    if not project.root:
        click.echo("Not in a package project directory.")
        ctx.abort()

    new_cmd(project, pkg_type, pkg_name, conf_json)


@main.command()
# diable this for now ## @click.argument('pkgs', nargs=-1, required=False)
@click.option('--force', '-f', is_flag=True, help='Force installation even already installed.')
@click.option('--skip-tests', '-T', is_flag=True, help='Not to run tests after installation.')
@click.pass_context
def install(ctx, force, skip_tests):
    """
    Install dependencies for the package currently being worked on.
    """
    project = ctx.obj.get('PROJECT')
    if not project.root:
        click.echo("Not in a package project directory.")
        ctx.abort()

    install_cmd(project, force, skip_tests)


@main.command()
@click.pass_context
def list(ctx):
    """
    List local and installed dependent packages.
    """
    project = ctx.obj.get('PROJECT')
    if not project.root:
        click.echo("Not in a package project directory.")
        ctx.abort()

    list_cmd(project)


@main.command()
@click.pass_context
def uninstall(ctx):
    """
    Uninstall packages.
    """
    project = ctx.obj.get('PROJECT')
    if not project.root:
        click.echo("Not in a package project directory.")
        ctx.abort()

    uninstall_cmd(project)


@main.command()
@click.pass_context
def outdated(ctx):
    """
    List outdated dependent packages.
    """
    project = ctx.obj.get('PROJECT')
    if not project.root:
        click.echo("Not in a package project directory.")
        ctx.abort()

    outdated_cmd(project)


@main.command()
# TODO: add an optional argument to specify which package to test
@click.pass_context
def test(ctx):
    """
    Run tests.
    """
    project = ctx.obj.get('PROJECT')
    if not project.root:
        click.echo("Not in a package project directory.")
        ctx.abort()

    test_cmd(project)


@main.command()
@click.argument('pkg', required=False)
@click.option('--stop', '-s', is_flag=True, help='Stop working on the current package.')
@click.option('--update', '-u', is_flag=True, help='Perform git fetch to update branches/tags.')
@click.pass_context
def workon(ctx, pkg=None, stop=False, update=False):
    """
    Start work on a package, display packages released or in dev.
    """
    project = ctx.obj.get('PROJECT')
    if not project.root:
        click.echo("Not in a package project directory.")
        ctx.abort()

    workon_cmd(
        project=project,
        pkg=pkg,
        stop=stop,
        update=update
    )


@main.command()
@click.argument('pkg', type=str, required=True)
@click.argument('version', type=str, required=True)
@click.pass_context
def nextver(ctx, pkg=None, version=False):
    """
    Start a new version of a released or in development package.
    """
    project = ctx.obj.get('PROJECT')
    if not project.root:
        click.echo("Not in a package project directory.")
        ctx.abort()

    nextver_cmd(
        project=project,
        pkg=pkg,
        version=version
    )
