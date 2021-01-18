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

from click import echo
from wfpm.package import Package


def install_cmd(ctx, pkgs, force, include_tests):
    project = ctx.obj['PROJECT']
    if not project.root:
        echo("Not in a package project directory.")
        ctx.abort()

    failed_pkgs = []
    for pkg in pkgs:  # install command line specified package(s)
        try:
            package = Package(pkg_uri=pkg)
        except Exception as ex:
            echo(f"Failed to initial package: {pkg}. {ex}")
            failed_pkgs.append(pkg)
            continue

        try:
            path = package.install(
                project.root,
                include_tests=include_tests,
                force=force
            )
            echo(f"Package installed in: {path}")

        except Exception as ex:
            echo(f"Failed to install package: {pkg}. {ex}")
            failed_pkgs.append(pkg)

    else:  # install dependent packages(s) specified in pkg.json
        # TODO: retrieve dependencies from pkg.json
        pass

    if failed_pkgs:
        ctx.exit(1)
