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
from glob import glob
from wfpm.package import Package
from ..utils import test_package


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

            if include_tests:
                test_package(path)

        except Exception as ex:
            echo(f"Failed to install package: {pkg}. {ex}")
            failed_pkgs.append(pkg)

    if not pkgs:  # install dependent package(s) specified in pkg.json
        # first find all local packages
        pkg_jsons = sorted(glob(os.path.join(project.root, '*', 'pkg.json')))
        for pkg_json in pkg_jsons:
            package = Package(pkg_json=pkg_json)
            dependencies = package.dependencies
            devDependencies = package.devDependencies

            # TODO: some duplicated code with the above section, need cleanup
            # TODO: improvement: gather all dependencies first and combine them into a unique set to avoid duplicated install
            for dep_pkg_uri in dependencies + devDependencies:
                if not dep_pkg_uri:  # this shouldn't be necessary, but let's safeguard this for now
                    continue

                package = Package(pkg_uri=dep_pkg_uri)
                installed = False
                try:
                    path = package.install(
                        project.root,
                        include_tests=include_tests,
                        force=force
                    )
                    installed = True
                    echo(f"Package installed in: {path}")
                except Exception as ex:
                    echo(f"Failed to install package: {dep_pkg_uri}. {ex}")
                    failed_pkgs.append(dep_pkg_uri)

                if include_tests and installed:
                    test_package(path)

    if failed_pkgs:
        ctx.exit(1)
