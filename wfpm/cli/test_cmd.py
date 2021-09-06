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

import sys
from click import echo
from ..utils import test_package


def test_cmd(project):
    pkg_count = 0
    invalid_pkg_count = 0
    failed_test_count = 0
    for pkg in project.pkgs:
        if project.current_pkg and project.current_pkg.name != pkg.name:
            continue

        pkg_count += 1
        echo(f"Validating package: {pkg.pkg_path}")
        pkg_issues = pkg.validate(
            project.repo_server,
            project.repo_account,
            project.name,
            project.installed_pkgs)
        if pkg_issues:
            echo("Package issues identified:")
            for i in range(len(pkg_issues)):
                echo(f"[{i+1}/{len(pkg_issues)}] {pkg_issues[i]}")
            invalid_pkg_count += 1
        else:
            echo("Pakcage valid.")
            echo(f"Testing package: {pkg.pkg_path}")
            failed_test_count += test_package(pkg.pkg_path)

    if not pkg_count:
        echo("No package to test.")

    if invalid_pkg_count or failed_test_count:
        sys.exit(1)  # signal failure
