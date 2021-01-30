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


def list_cmd(ctx):
    project = ctx.obj['PROJECT']
    if not project.root:
        echo("Not in a package project directory.")
        ctx.abort()

    echo('\t'.join(['TYPE', 'PKG_URI']))
    for pkg in sorted([pkg.pkg_uri for pkg in project.pkgs]):
        echo('\t'.join(['local', str(pkg)]))

    for pkg in sorted([pkg.pkg_uri for pkg in project.installed_pkgs]):
        echo('\t'.join(['dep', str(pkg)]))
