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
import logging
from glob import glob
from collections import OrderedDict
from typing import List
from click import echo
from functools import lru_cache
from .git import Git
from .package import Package
from .utils import locate_nearest_parent_dir_with_file


class Project(object):
    """
    Project object keeps all information about the package project
    """
    debug: bool = False
    logger: logging.Logger = None
    git: Git = None
    root: str = None
    name: str = None
    fullname: str = None
    license: str = None
    repo_type: str = None
    repo_server: str = None
    repo_account: str = None
    cwd: str = None
    pkg_cwd_under: Package = None
    pkgs: List[Package] = []
    installed_pkgs: List[Package] = []
    pkg_workon: str = None
    pkgs_in_dev: List[str] = []
    pkgs_released: List[str] = []

    def __init__(self, debug=False, project_root=None):
        self.cwd = os.getcwd()
        self.debug = debug
        self.git = Git()

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

        self._init_logger()

        if not self.root:
            self.logger.info('Project object initialized without root dir.')
            return  # not a real project yet, no need to go further
        else:
            self.logger.info(f'Project object initialized in {self.root}')

        with open(os.path.join(self.root, '.wfpm'), 'r') as c:
            conf = yaml.safe_load(c)

            fields = ['project_name', 'repo_type', 'repo_server', 'repo_account']
            if set(fields) - set(conf.keys()):
                raise Exception(f"Invalid .wfpm file: {os.path.join(self.root, '.wfpm')}, "
                                f"expected fields: {', '.join(fields)}")
            else:
                self.name = conf['project_name']
                self.repo_type = conf['repo_type']
                self.repo_server = conf['repo_server']
                self.repo_account = conf['repo_account'].lower()
                self.license = conf.get('license', '')

        self._populate_pkgs()
        self._populate_pkg_status()

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
                self.pkg_cwd_under = pkg

    @property
    @lru_cache()
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

    def _populate_pkg_status(self):
        rel_cans = self.git.rel_candidates
        pkgs_in_dev = OrderedDict()
        for pkg in sorted(rel_cans.keys()):
            for v in rel_cans[pkg]:
                pkgs_in_dev[f"{pkg}@{v}"] = 1

        self.pkgs_in_dev = list(pkgs_in_dev.keys())

        rels = self.git.releases
        pkgs_released = OrderedDict()
        for pkg in sorted(rels.keys()):
            for v in rels[pkg]:
                pkgs_released[f"{pkg}@{v}"] = 1

        self.pkgs_released = list(pkgs_released.keys())

        if self.git.current_branch and \
                '@' in self.git.current_branch and \
                self.git.current_branch in self.pkgs_in_dev:
            self.pkg_workon = self.git.current_branch

    def set_workon(self, pkg_fullname):
        if os.getcwd() != self.root:
            echo("Must run this command under project root dir.")
            sys.exit(1)

        self.git.cmd_checkout_branch(branch=pkg_fullname)
        self.pkg_workon = pkg_fullname

    def _init_logger(self):
        logger = logging.getLogger('wfpm')
        if self.debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARN)

        if self.root:
            log_file = os.path.join(self.root, ".log")
            fh = logging.FileHandler(log_file)
            logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] %(message)s")
            fh.setFormatter(logFormatter)
            logger.addHandler(fh)

        else:  # don't create log file, output logging to console
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter("[%(levelname)-5.5s] %(message)s"))
            logger.addHandler(ch)

        self.logger = logger
