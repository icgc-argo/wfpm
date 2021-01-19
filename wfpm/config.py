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
import yaml
from .utils import Singleton, locate_nearest_parent_dir_with_file


class Config(object):
    __metaclass__ = Singleton

    debug: bool = False
    root: str = None
    project_name: str = None
    license: str = None
    repo_type: str = None
    repo_server: str = None
    repo_account: str = None
    cwd: str = None
    current_pkg: str = None

    def __init__(self, debug=False) -> None:
        self.cwd = os.getcwd()
        self.debug = debug

        # locate project root
        project_root = locate_nearest_parent_dir_with_file(
            start_dir=self.cwd,
            filename='.wfpm'
        )
        if project_root:
            self.root = project_root
            self.config_file = os.path.join(self.root, '.wfpm')
            self._get_info_from_config()

            current_pkg_path = locate_nearest_parent_dir_with_file(
                start_dir=self.cwd,
                filename='pkg.json'
            )
            if current_pkg_path:
                self.current_pkg = os.path.basename(current_pkg_path)

        else:
            self.root = None  # indicate not in a valid project (yet)

    def _get_info_from_config(self) -> None:
        with open(self.config_file, 'r') as c:
            conf = yaml.safe_load(c)

        fields = ['project_name', 'repo_type', 'repo_server', 'repo_account']
        if set(fields) - set(conf.keys()):
            raise Exception(f"Invalid .wfpm file: {self.config_file}, expected fields: {', '.join(fields)}")
        else:
            self.project_name = conf['project_name']
            self.license = conf['license']
            self.repo_type = conf['repo_type']
            self.repo_server = conf['repo_server']
            self.repo_account = conf['repo_account']
