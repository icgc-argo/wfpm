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
import re
import sys
import json
from distutils.version import LooseVersion
from collections import OrderedDict
from click import echo
from wfpm.project import Project
from wfpm import PKG_VER_REGEX, __version__ as ver


def nextver_cmd(
    project: Project = None,
    pkg: str = None,
    version: str = None
):
    validate_input(project, pkg, version)

    git_branch_local_remote_cmp(project)

    new_pkg = f"{pkg.split('@')[0]}@{version}"

    if new_pkg in project.pkgs_in_dev or new_pkg in project.pkgs_released:
        echo(f"Specified new version already exists: {new_pkg}")
        sys.exit(1)

    if pkg in project.pkgs_in_dev:
        project.git.cmd_checkout_branch(pkg)
        git_branch_local_remote_cmp(project)

        project.git.cmd_new_branch(branch=new_pkg)
        start_from = 'in development'

    elif pkg in project.pkgs_released:
        tag = pkg.replace('@', '.v', 1)
        if tag not in project.git.tags:
            tag = pkg.replace('@', '.', 1)

        project.git.cmd_new_branch_from_tag(
            tag=tag,
            branch=new_pkg
        )
        start_from = 'released'

    else:
        echo(f"No package found as: '{pkg}'. Run 'wfpm workon' to display package info.")
        sys.exit(1)

    # refreshed the project object
    project = Project(project_root=project.root, debug=project.debug)

    update_pkg_json_and_main(project)

    paths_to_add = new_pkg.split('@')[0]
    project.git.cmd_add_and_commit(
        path=paths_to_add,
        message=f'[wfpm v.{ver}] started a new version {new_pkg} from {pkg} which was {start_from}'
    )

    echo(f"Started a new package version: {new_pkg}\n" +
         "Code updated with new version number, added and committed to git. Please continue working on it.")


def validate_input(project, pkg, version):
    if '@' not in pkg:
        echo("Please specify package full name, ie, <pkg_name>@<version>")
        sys.exit(1)

    if not re.match(PKG_VER_REGEX, version):
        echo(f"Specified new version is not valid, expected pattern: {PKG_VER_REGEX}")
        sys.exit(1)

    if LooseVersion(version) <= LooseVersion(pkg.split('@')[1]):
        echo(f"New version '{version}' must be higher than the starting version '{pkg.split('@')[1]}'")
        sys.exit(1)

    if project.root != os.getcwd():
        echo(f"Must run this command under the project root dir: {project.root}")
        sys.exit(1)

    if not (project.git.user_name and project.git.user_email):
        echo("Git not configured with 'user.name' and 'user.email', please set them using 'git config'.")
        sys.exit(1)

    if project.pkg_workon:
        echo(f"Must stop working on '{project.pkg_workon}' before creating a new package version. "
             "Please run: wfpm workon -s")
        sys.exit(1)

    if project.git.current_branch != 'main':
        echo(f"Must run this command on main branch, current branch: {project.git.current_branch}")
        sys.exit(1)

    if not project.git.branch_clean():
        echo(f"Git branch '{project.git.current_branch}' not clean. Please complete current work and commit changes.")
        sys.exit(1)

    if not project.git.fetch_and_housekeeping():
        echo("Unable to fetch branches/tags from remote.")
        sys.exit(1)


def git_branch_local_remote_cmp(project):
    git_status = project.git.get_status()
    branch = project.git.current_branch

    if git_status in ('up_to_date-clean', 'up_to_date', 'clean', ''):  # good statuses
        return

    if git_status.startswith('behind'):
        echo(f"Local '{branch}' branch is behind the remote. Please 'git pull' to update.")
        sys.exit(1)
    elif git_status.startswith('ahead'):
        echo(f"Local '{branch}' branch is ahead of remote. Please 'git push' to publish local changes.")
        sys.exit(1)
    elif git_status.startswith('diverged'):
        echo(f"Local '{branch}' branch has diverged from remote. Please resolve the changes and synchronize.")
        sys.exit(1)


def update_pkg_json_and_main(project):
    pkg_name, version = project.pkg_workon.split('@')
    pkg_json = os.path.join(
        project.root,
        pkg_name,
        'pkg.json'
    )

    pkg_dict = json.load(open(pkg_json), object_pairs_hook=OrderedDict)

    pkg_dict['version'] = version

    with open(pkg_json, 'w') as p:
        p.write(json.dumps(pkg_dict, indent=4))

    main_script_name = pkg_dict['main'] if pkg_dict['main'].endswith('.nf') else f"{pkg_dict['main']}.nf"

    main_script = os.path.join(
        project.root,
        pkg_name,
        main_script_name
    )

    new_main_script_str = ''
    with open(main_script, 'r') as f:
        found = False
        for line in f:
            if not found and line.strip().startswith('version'):
                line = f"version = '{version}'\n"
                found = True

            new_main_script_str += line

    with open(main_script, 'w') as f:
        f.write(new_main_script_str)
