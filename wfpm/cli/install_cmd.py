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
from pathlib import Path
from click import echo
from wfpm.package import Package
from ..utils import test_package, pkg_uri_parser


def install_cmd(ctx, force, include_tests):
    project = ctx.obj['PROJECT']
    if not project.root:
        echo("Not in a package project directory.")
        ctx.abort()

    if str(Path(os.getcwd()).parent) != project.root:
        echo("Not in a package directory.")
        ctx.abort()

    if not os.path.isfile('pkg.json'):
        echo("Not in a package directory, 'pkg.json' not found in the current direcotry.")
        ctx.abort()

    pkg_json = os.path.join(os.getcwd(), 'pkg.json')
    package = Package(pkg_json=pkg_json)
    dependencies = package.dependencies
    devDependencies = package.devDependencies

    dep_pkgs = []
    bad_dep_pkgs = []
    for dep_pkg_uri in dependencies + devDependencies:
        try:
            pkg_uri_parser(dep_pkg_uri)   # make sure pkg_uri format is valid, although we don't use the return values
        except Exception as ex:
            echo(f"Invalid dependency: {dep_pkg_uri}. Message: {ex}")
            if dep_pkg_uri not in bad_dep_pkgs:
                bad_dep_pkgs.append(dep_pkg_uri)
            continue

        if dep_pkg_uri not in dep_pkgs:
            dep_pkgs.append(dep_pkg_uri)

    if bad_dep_pkgs:
        echo("Unable to proceed with dependency installation. Check message above.")
        ctx.exit(1)

    failed_pkgs = []
    for dep_pkg_uri in dep_pkgs:
        package = Package(pkg_uri=dep_pkg_uri)
        installed = False
        try:
            path = package.install(
                project.root,
                include_tests=include_tests,
                force=force
            )
            installed = True
            echo(f"Package installed in: {path.replace(os.path.join(os.getcwd(), ''), '')}")
        except Exception as ex:
            echo(f"Failed to install package: {dep_pkg_uri}. {ex}")
            failed_pkgs.append(dep_pkg_uri)

        if include_tests and installed:
            test_package(path)

    if failed_pkgs:
        ctx.exit(1)
