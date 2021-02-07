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
from click import echo
from typing import List, Dict
from functools import lru_cache
from distutils.version import LooseVersion
from .utils import run_cmd


class Git(object):
    """
    Git object keeps all information about the git availability/config/repo/branch etc
    """
    version: str = None
    user_name: str = ''
    user_email: str = ''
    remote_repo: bool = True
    current_branch: str = None
    local_branches: List[str] = []
    remote_branches: List[str] = []
    tags: List[str] = []
    offline: bool = False
    releases: Dict = {}

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

        """
        Need to think about it more how/when to do this
        # fetch remote branches and tags
        stdout, stderr, ret = run_cmd('git fetch --all --tags')
        if ret != 0:  # cmd failed
            if 'Repository not found' in stdout:
                echo("Remote repository not found. Please make sure the repository exists.")
                self.remote_repo = False
            else:
                echo("Info: unable to fetch remote git origin. "
                     "Seems like you are offline or don't have the correct access rights.")
                self.remote_repo = None
                self.offline = True
        """

        branch_info_str, stderr, ret = run_cmd('git branch -a')
        if ret == 0:
            for branch in branch_info_str.split('\n'):
                branch = branch.strip()
                if len(branch) == 0:
                    continue

                if branch.startswith('remotes/origin/'):
                    self.remote_branches.append(branch.replace('remotes/origin/', ''))
                else:
                    if branch.startswith('*'):
                        self.current_branch = branch.split(' ')[1]
                        self.local_branches.append(self.current_branch)
                    else:
                        self.local_branches.append(branch)

        tag_info_str, stderr, ret = run_cmd('git tag -l')
        if ret == 0:
            for tag in tag_info_str.split('\n'):
                if len(tag) == 0:
                    continue
                self.tags.append(tag)

    @property
    @lru_cache()
    def rel_candidates(self):
        cans = dict()
        rel_cans = dict()
        branches = set(self.remote_branches).union(set(self.local_branches))
        for br in branches:
            if '@' not in br:
                continue
            name, ver = br.split('@')
            if name not in cans:
                cans[name] = set()
            cans[name].add(ver)

        for pkg in cans:
            if pkg in self.releases:
                x = cans[pkg] - set(self.releases[pkg])
                if x:
                    rel_cans[pkg] = sorted(x, key=LooseVersion, reverse=True)
            else:
                rel_cans[pkg] = sorted(cans[pkg], key=LooseVersion, reverse=True)

        return rel_cans

    @property
    @lru_cache()
    def releases(self):
        unsorted_rels = dict()
        rels = dict()
        for t in self.tags:
            parts = t.split('.')
            name = parts[0]
            ver = '.'.join(parts[1:]).lstrip('v')
            if name not in unsorted_rels:
                unsorted_rels[name] = set()
            unsorted_rels[name].add(ver)

        for r in unsorted_rels:
            rels[r] = sorted(unsorted_rels[r], key=LooseVersion, reverse=True)

        return rels

    def cmd_checkout_branch(self, branch=None):
        if not branch:
            raise Exception("Error: must specify a branch to switch to.")

        # always cleanup module dir when switching branches
        paths_to_cleanup = [os.path.join('wfpr_modules', 'github.com')]
        if '@' in self.current_branch:  # whether currently on a package branch
            # clean up files/folders under the current package that are git ignored,
            # removing other untracked files can not happen because they will cause branch 'not clean'
            # that prevents branch switching from being started
            paths_to_cleanup.append(self.current_branch.split('@')[0])

        cmd = f'cd $(git rev-parse --show-toplevel) && git checkout {branch}' + \
              f' && git clean -xdf {" ".join(paths_to_cleanup)}'

        stdout, stderr, ret = run_cmd(cmd)
        if ret != 0:
            raise Exception(f"Failed to switch to '{branch}'.\nSTDOUT: {stdout}\nSTDERR: {stderr}")
        else:
            self.current_branch = branch

    def cmd_new_branch(self, branch=None):
        if not branch:
            raise Exception("Error: must specify a new branch name.")

        stdout, stderr, ret = run_cmd(f'git checkout -b {branch}')
        if ret != 0:
            raise Exception(f"Failed to create new branch '{branch}'.\nSTDOUT: {stdout}\nSTDERR: {stderr}")
        else:
            self.current_branch = branch

    def cmd_add_and_commit(self, path=None, message=None):
        if not (path and message):
            raise Exception("Error: must specify path to add and commit message.")

        cmd = f"git add {path} && git commit -m '{message}'"
        stdout, stderr, ret = run_cmd(cmd)
        if ret != 0:
            raise Exception(f"Failed to execute: {cmd}.\nSTDOUT: {stdout}\nSTDERR: {stderr}")

    def branch_clean(self):
        stdout, stderr, ret = run_cmd('git status')
        if 'working tree clean' in stdout:
            return True
        return False
