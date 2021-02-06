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
import json
import requests
import tempfile
from typing import Set
from .utils import run_cmd, pkg_uri_parser, pkg_asset_download_urls


class Package(object):
    name: str = None
    version: str = None
    main: str = None

    repo_type: str = 'git'  # hardcode for now
    repo_server: str = None
    repo_account: str = None
    repo_name: str = None

    dependencies: Set[str] = set()
    devDependencies: Set[str] = set()
    allDependencies: Set[str] = set()

    def __init__(self, pkg_uri=None, pkg_json=None):
        if pkg_uri and pkg_json:
            raise Exception("Cannot specify both pkg_uri and pkg_json")
        elif pkg_uri:
            self._init_by_uri(pkg_uri)
        elif pkg_json:
            self._init_by_json(pkg_json)
        else:
            raise Exception("Must specify either pkg_uri or pkg_json")

    def _init_by_uri(self, pkg_uri):
        try:
            repo_server, repo_account, repo_name, name, version = pkg_uri_parser(pkg_uri)
        except Exception as ex:
            raise Exception(f"Package uri error: {ex}")

        self.name = name
        self.version = version

        self.repo_server = repo_server
        self.repo_account = repo_account.lower()
        self.repo_name = repo_name

        # download pkg-release.json from github release asset and parse it to get addition info
        pkg_json_str = ''
        download_urls = pkg_asset_download_urls(self.pkg_json_url)
        for download_url in download_urls:
            r = requests.get(download_url)
            if r.status_code == 200:
                pkg_json_str = r.text
                break

        if not pkg_json_str:
            raise Exception("Failed to download 'pkg-release.json'. Looks like this package has "
                            f"not been released: {self.pkg_uri}.")

        self._init_by_json(pkg_json_str=pkg_json_str)

    def _init_by_json(self, pkg_json=None, pkg_json_str=None):
        if pkg_json:
            with open(pkg_json, 'r') as f:
                pkg_dict = json.load(f)
        elif pkg_json_str:
            pkg_dict = json.loads(pkg_json_str)
        else:
            raise Exception("Must specify 'pkg_json' or 'pkg_json_str' when call '_init_by_json'")

        self.name = pkg_dict['name']
        self.version = pkg_dict['version']
        self.main = pkg_dict['main']

        _, _, repo_server, repo_account, repo_name = \
            pkg_dict['repository']['url'].split('/')

        self.repo_server = repo_server
        self.repo_account = repo_account.lower()
        self.repo_name = repo_name.split('.')[0]  # repo_name.git

        self._init_deps(
            pkg_dict.get('dependencies', []),
            pkg_dict.get('devDependencies', [])
        )

    @property
    def fullname(self):
        return f"{self.name}@{self.version}"

    @property
    def project_fullname(self):
        return f"{self.repo_server}/{self.repo_account}/{self.repo_name}"

    @property
    def pkg_uri(self):
        return f"{self.project_fullname}/{self.fullname}"

    @property
    def release_tag(self):
        return self.fullname.replace('@', '.v')

    @property
    def pkg_tar_url(self):
        return f"https://{self.project_fullname}/releases/download/{self.release_tag}/{self.release_tag}.tar.gz"

    @property
    def pkg_json_url(self):
        return f"https://{self.project_fullname}/releases/download/{self.release_tag}/pkg-release.json"

    def install(self, target_project_root, force=False):
        target_path = os.path.join(
            target_project_root,
            'wfpr_modules',
            self.repo_server,
            self.repo_account,
            self.repo_name,
            self.fullname
        )

        if os.path.isdir(target_path) and not force:
            raise Exception(f"Pakcage already installed: {target_path.replace(os.path.join(os.getcwd(), ''), '')}, "
                            "skip unless force option is specified.")

        if force:
            out, err, ret = run_cmd(f"rm -fr {target_path}")  # remove possible previous installation
            if ret != 0:
                raise Exception(f"Unable to remove previously installed package: {err}")

        return self._download_and_install(target_path)

    def _download_and_install(self, target_path=None):
        success = False
        for download_url in pkg_asset_download_urls(self.pkg_tar_url):
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                success = True
                break

        if success:
            with tempfile.TemporaryDirectory() as tmpdirname:
                local_tar_path = os.path.join(tmpdirname, os.path.basename(self.pkg_tar_url))

                with open(local_tar_path, 'wb') as f:
                    for chunk in response.raw.stream(1024, decode_content=False):
                        if chunk:
                            f.write(chunk)

                cmd = f"mkdir -p {target_path} && " \
                      f"tar -xzf {local_tar_path} -C {target_path} && " \
                      f"cd {target_path} && ln -s ../../../../../wfpr_modules . && " \
                      "cd tests && ln -s ../wfpr_modules ."

                out, err, ret = run_cmd(cmd)
                if ret != 0:
                    run_cmd(f"rm -fr {target_path}")  # undo partial installation
                    raise Exception(f"Package downloaded but installation failed: {err}")

                return target_path  # return the path the package was installed

        else:
            raise Exception(f"Looks like this package has not been released: {self.pkg_uri}")

    def __repr__(self):
        return self.pkg_uri

    def _init_deps(self, dependencies=[], devDependencies=[]):
        # some basic validation
        if len(dependencies) != len(set(dependencies)):
            raise Exception(f"Duplicated dependencies found: {', '.join(dependencies)}")
        else:
            dependencies = set(dependencies)

        if len(devDependencies) != len(set(devDependencies)):
            raise Exception(f"Duplicated devDependencies found: {', '.join(devDependencies)}")
        else:
            devDependencies = set(devDependencies)

        if dependencies.intersection(devDependencies):
            raise Exception("Dependency duplicated in 'dependencies' and 'devDependencies': "
                            f"{ ', '.join(dependencies.intersection(devDependencies)) }")

        allDependencies = dependencies.union(devDependencies)

        for dep_pkg_uri in allDependencies:
            try:
                pkg_uri_parser(dep_pkg_uri)   # make sure pkg_uri format is valid, although we don't use the return values
            except Exception as ex:
                raise Exception(f"Invalid dependency: {dep_pkg_uri}. Message: {ex}")

        self.dependencies = dependencies
        self.devDependencies = devDependencies

        # at this stage, let's just treat all dependencies the same way,
        # later may need to handle devDep differently
        self.allDependencies = self.dependencies.union(self.devDependencies)
