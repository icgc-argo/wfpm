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

import networkx as nx
from .package import Package


def build_dep_graph(start_pkg: Package = None, DG: nx.DiGraph = None):
    for dep in start_pkg.allDependencies:
        if dep == start_pkg.pkg_uri:
            raise Exception(f"Self dependency detected: {start_pkg.pkg_uri} -> {dep}")

        DG.add_edge(start_pkg.pkg_uri, dep)

        pkg = Package(pkg_uri=dep)
        build_dep_graph(pkg, DG)
