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


def list_cmd(ctx):
    config = ctx.obj['CONFIG']
    project = ctx.obj['PROJECT']
    if not project.root:
        echo("Not in a package project directory.")
        ctx.abort()

    packages = []

    pkg_jsons = sorted(glob(os.path.join(project.root, '*', 'pkg.json')))
    for pkg_json in pkg_jsons:
        packages.append(
            ('local', Package(pkg_json=pkg_json))
        )

    ins_dep_paths = sorted(glob(os.path.join(project.root, 'wfpr_modules/*/*/*/*')))
    for ins_dep_path in ins_dep_paths:
        pkg_uri = '/'.join(ins_dep_path.split(os.sep)[-4:])
        packages.append(
            ('dep', Package(pkg_uri=pkg_uri))
        )

    echo('\t'.join([
        'TYPE',
        'PKG_URI',
    ]))
    for pkg in packages:
        echo('\t'.join([
            pkg[0],
            str(pkg[1]),
        ]))
