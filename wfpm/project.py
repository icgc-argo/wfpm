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
import yaml
from glob import glob
from typing import List
from click import echo
from .config import Config
from .package import Package
from .utils import locate_nearest_parent_dir_with_file


class Project(object):
    """
    Project object keeps all information about the package project
    """
    config: Config = None
    root: str = None
    name: str = None
    fullname: str = None
    license: str = None
    repo_type: str = None
    repo_server: str = None
    repo_account: str = None
    cwd: str = None
    current_pkg: Package = None
    pkgs: List[Package] = []
    installed_pkgs: List[Package] = []

    def __init__(self, debug=False, project_root=None):
        self.cwd = os.getcwd()
        self.config = Config(debug=debug)

        if project_root:
            if os.path.isfile(os.path.join(project_root, '.wfpm')):
                self.root = project_root
            else:
                raise Exception(f"Specified project root path misses '.wfpm' file: {project_root}")
        else:
            self.root = locate_nearest_parent_dir_with_file(
                start_dir=self.cwd,
                filename='.wfpm'
            )

        if not self.root:
            return  # not a project yet, no need to go further

        with open(os.path.join(self.root, '.wfpm'), 'r') as c:
            conf = yaml.safe_load(c)

            fields = ['project_name', 'repo_type', 'repo_server', 'repo_account']
            if set(fields) - set(conf.keys()):
                raise Exception(f"Invalid .wfpm file: {self.config_file}, expected fields: {', '.join(fields)}")
            else:
                self.name = conf['project_name']
                self.repo_type = conf['repo_type']
                self.repo_server = conf['repo_server']
                self.repo_account = conf['repo_account'].lower()
                self.license = conf.get('license', '')

        self._populate_pkgs()

    @property
    def fullname(self):
        if self.repo_server and self.repo_account and self.name:
            return f"{self.repo_server}/{self.repo_account}/{self.name}"

    def __repr__(self):
        return self.fullname

    def _populate_pkgs(self):
        pkg_jsons = glob(os.path.join(self.root, '*', 'pkg.json'))
        for pkg_json in pkg_jsons:
            try:
                pkg = Package(pkg_json=pkg_json)
            except Exception as ex:
                echo(f"Problem encounter, invalid package json: {pkg_json}. {ex}", err=True)
                echo("Please fix the issue before continue.", err=True)
                sys.exit(1)

            self.pkgs.append(pkg)

            pkg_dir = os.path.join(os.path.dirname(pkg_json), '')
            if os.path.join(self.cwd, '').startswith(pkg_dir):
                self.current_pkg = pkg

    @property
    def installed_pkgs(self):
        installed_pkgs = []
        pkg_jsons = glob(os.path.join(
            self.root, 'wfpr_modules', 'github.com', '*', '*', '*', 'pkg.json')
        )

        for pkg_json in pkg_jsons:
            try:
                pkg = Package(pkg_json=pkg_json)
            except Exception as ex:
                echo(f"Problem encounter, invalid package json: {pkg_json}. {ex}", err=True)
                echo("Please fix the issue before continue.", err=True)
                sys.exit(1)

            installed_pkgs.append(pkg)

        return installed_pkgs
