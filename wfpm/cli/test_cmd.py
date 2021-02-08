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
import sys
from click import echo
from ..utils import test_package


def test_cmd(project):
    if project.pkg_workon:  # test the current pkg only
        pkg_path = os.path.join(project.root, project.pkg_workon.split('@')[0])
        echo(f"Testing package: {pkg_path}")
        failed_test_count = test_package(pkg_path)

        if failed_test_count:
            sys.exit(1)  # signal failure

    else:  # test all pkgs
        pkg_names = sorted([pkg.name for pkg in project.pkgs])
        pkg_count = len(pkg_names)
        failed_test_count = 0

        for i in range(pkg_count):
            pkg_path = os.path.join(project.root, pkg_names[i])
            echo(f"Testing package: {pkg_path}")
            failed_test_count += test_package(pkg_path)

        if not pkg_count:
            echo("No test to run.")

        if failed_test_count:
            sys.exit(1)  # signal failure
