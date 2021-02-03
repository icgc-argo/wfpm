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
import networkx as nx
from pathlib import Path
from click import echo
from wfpm.package import Package
from wfpm.dependency import build_dep_graph
from ..utils import test_package


def install_cmd(ctx, force=False, skip_tests=False, pkg_json=None):
    if not pkg_json:
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

        install_dest = project.root
        pkg_json = os.path.join(os.getcwd(), 'pkg.json')

    else:
        install_dest = os.path.dirname(os.path.dirname(pkg_json))  # parent dir of where pkg.json is

    try:
        package = Package(pkg_json=pkg_json)
        dep_graph = nx.DiGraph()
        build_dep_graph(package, DG=dep_graph)
    except Exception as ex:
        echo(f"Unable to build package dependency graph: {ex}")
        ctx.abort()

    # exclude the first one which is the current package itself, it's important to reverse the order
    dep_pkgs = list(reversed(list(nx.topological_sort(dep_graph))[1:]))

    if dep_pkgs:
        echo("Start dependency installation.")
    else:
        echo("No dependency defined, no installation needed.")

    failed_pkgs = []
    installed_pkgs = []
    for dep_pkg_uri in dep_pkgs:
        package = Package(pkg_uri=dep_pkg_uri)
        installed = False

        try:
            path = package.install(
                install_dest,
                force=force
            )
            installed = True
            installed_pkgs.append(dep_pkg_uri)
            echo(f"Package installed in: {path.replace(os.path.join(os.getcwd(), ''), '')}")

        except Exception as ex:
            echo(f"{ex}")
            failed_pkgs.append(dep_pkg_uri)

        if not skip_tests and installed:
            test_package(path)

    return installed_pkgs, failed_pkgs
