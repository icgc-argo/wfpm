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

import re
from .utils import run_cmd


class Git(object):
    """
    Git object keeps all information about the git availability/config/repo/branch etc
    """
    version: str = None
    user_name: str = ''
    user_email: str = ''

    def __init__(self):
        self._get_git_info()

    def _get_git_info(self):
        stdout, stderr, ret = run_cmd('git --version')
        if ret != 0:  # error out, git not available
            return

        ver = re.match(r'.*?(([0-9]+)\.[0-9]+\.[0-9]+)', stdout)
        if ver and int(ver.groups()[1]) >= 2:
            self.version = ver.groups()[0]
        else:
            return  # git version too low or unable to determine version

        git_user_info_str, stderr, ret = run_cmd('git config --list | grep user')
        if ret == 0:  # cmd success
            for info in git_user_info_str.split("\n"):
                key, value = info.split('=')
                if key.strip() == 'user.name':
                    self.user_name = value.strip()

                if key.strip() == 'user.email':
                    self.user_email = value.strip()
