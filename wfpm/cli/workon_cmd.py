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
from wfpm.project import Project


def workon_cmd(
    project: Project = None,
    pkg: str = None,
    stop: bool = False
):
    if stop:
        if project.pkg_workon:
            if not project.git.branch_clean():
                echo(f"Package branch '{project.pkg_workon}' not clean, please complete on-going work and commit changes.")
                sys.exit(1)

            project.git.cmd_checkout_branch('main')
            echo(f"Stopped work on {project.pkg_workon}")
        else:
            echo("Not working on any package.")
        sys.exit()

    if pkg is None:
        echo(f"Package being worked on: {project.pkg_workon if project.pkg_workon else '<none>'}")
        echo(f"Packages in development: {', '.join(project.pkgs_in_dev) if project.pkgs_in_dev else '<none>'}")

    elif pkg in project.pkgs_in_dev:
        project.set_workon(pkg)
        echo(f"Now work on '{pkg}'")

    else:
        echo(f"Not a package in development: '{pkg}'")
        echo("To create a new package, please run 'wfpm new' command.")
