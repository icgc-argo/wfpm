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
from glob import glob
from click import echo
from ..utils import run_cmd


def test_cmd(ctx):
    config = ctx.obj['CONFIG']
    project = ctx.obj['PROJECT']
    if not project.root:
        echo("Not in a package project directory.")
        ctx.abort()

    current_pkg = config.current_pkg
    if current_pkg:
        pkg_path = os.path.join(project.root, current_pkg)
        echo(f"Testing package: {pkg_path}")
        test_package(pkg_path)

    elif config.cwd == project.root:
        pkg_jsons = sorted(glob(os.path.join(project.root, '*', 'pkg.json')))
        pkg_count = len(pkg_jsons)
        for i in range(pkg_count):
            pkg_path = os.path.dirname(pkg_jsons[i])
            echo(f"Testing package: {pkg_path}")
            test_package(pkg_path)

    else:
        echo(f"Must run test under the project root dir or a package dir.")
        ctx.abort()


def test_package(pkg_path):
    test_path = os.path.join(pkg_path, 'tests')
    job_files = sorted(glob(os.path.join(test_path, 'test-*.json')))
    test_count = len(job_files)
    pass_count = 0
    for i in range(test_count):
        cmd = f"cd {test_path} && ./checker.nf -params-file {job_files[i]}"
        echo(f"[{i+1}/{test_count}] Test: {job_files[i]}. ", nl=False)
        out, err, ret = run_cmd(cmd)
        if ret != 0:
            echo(f"FAILED")
            echo(f"STDOUT: {out}")
            echo(f"STDERR: {err}")
        else:
            pass_count += 1
            echo(f"PASSED")

    echo(f"Package: {os.path.basename(pkg_path)}, PASSED: {pass_count}, FAILED: {test_count - pass_count}")
