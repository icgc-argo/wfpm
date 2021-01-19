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


from .utils import Singleton


class Project(object):
    __metaclass__ = Singleton

    name: str = None
    fullname: str = None
    license: str = None
    repo_type: str = None
    repo_server: str = None
    repo_account: str = None

    def __init__(
        self,
        config=None,
        repo_type=None,
        repo_server=None,
        repo_account=None,
        repo_name=None
    ):
        # TODO: add validation of arguments
        if config:
            self.root = config.root
            if self.root:
                self.name = config.project_name
                self.license = config.license
                self.repo_type = config.repo_type
                self.repo_server = config.repo_server
                self.repo_account = config.repo_account
                self.fullname = f"{self.repo_server}/{self.repo_account}/{self.name}"
        else:
            self.root = None
            self.name = repo_name
            self.repo_type = repo_type
            self.repo_server = repo_server
            self.repo_account = repo_account
            self.fullname = f"{self.repo_server}/{self.repo_account}/{self.name}"
