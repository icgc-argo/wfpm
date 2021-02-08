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
import subprocess
from glob import glob
from click import echo
from typing import Tuple, List
from wfpm import PRJ_NAME_REGEX, PKG_NAME_REGEX, PKG_VER_REGEX


def locate_nearest_parent_dir_with_file(start_dir=None, filename=None):
    paths = os.path.abspath(start_dir).split(os.path.sep)

    for i in sorted(range(len(paths)), reverse=True):
        path = os.path.sep.join(paths[:(i+1)])
        if os.path.isfile(os.path.join(path, filename)):
            return path


def run_cmd(cmd):
    # keep this simple for now
    proc = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
    stdout, stderr = proc.communicate()

    return (
        stdout.decode("utf-8").strip(),
        stderr.decode("utf-8").strip(),
        proc.returncode
    )


def test_package(pkg_path):
    test_path = os.path.join(pkg_path, 'tests')
    job_files = sorted(glob(os.path.join(test_path, 'test-*.json')))
    test_count = len(job_files)
    failed_count = 0
    for i in range(test_count):
        cmd = f"cd {test_path} && ./checker.nf -params-file {job_files[i]}"
        echo(f"[{i+1}/{test_count}] Testing: {job_files[i]}. ", nl=False)
        out, err, ret = run_cmd(cmd)
        if ret != 0:
            failed_count += 1
            echo("FAILED")
            echo(f"STDOUT: {out}")
            echo(f"STDERR: {err}")
        else:
            echo("PASSED")

    if not test_count:
        echo("No test to run.")

    echo(f"Tested package: {os.path.basename(pkg_path)}, PASSED: {test_count - failed_count}, FAILED: {failed_count}")

    return failed_count  # return number of failed tests


def pkg_uri_parser(pkg_uri) -> Tuple[str, str, str, str, str]:
    try:
        repo_server, repo_account, repo_name, pkg_fullname = pkg_uri.split('/')
        repo_account = repo_account.lower()  # make sure repo account is all lower case
        name, version = pkg_fullname.split('@')
    except ValueError:
        raise Exception(f"Invalid package uri: {pkg_uri}, expected format: "
                        "repo_server/repo_account/repo_name/pkg_name@pkg_version")

    if not re.match(PKG_NAME_REGEX, name):
        raise Exception(f"Invalid package name: {name}, expected name pattern: {PKG_NAME_REGEX}")

    if not re.match(PKG_VER_REGEX, version):
        raise Exception(f"Invalid package version: {version}, expected version pattern: {PKG_VER_REGEX}")

    return repo_server, repo_account, repo_name, name, version


def validate_project_name(name):
    if not re.match(PRJ_NAME_REGEX, name):
        raise Exception(f"Name invalid, does not match the required pattern: {PRJ_NAME_REGEX}")

    return True


def pkg_asset_download_urls(url) -> List[str]:
    """
    Example URL for release assets:
       tarball: https://github.com/ICGC-TCGA-PanCancer/awesome-wfpkgs2/releases/download/fastqc-wf.0.2.0/fastqc-wf.0.2.0.tar.gz
       json: https://github.com/ICGC-TCGA-PanCancer/awesome-wfpkgs2/releases/download/fastqc-wf.0.2.0/pkg-release.json
    This currently is to address the compatibilty issue related to
    release tag change, eg, fastqc-wf.0.2.0 => fastqc-wf.v0.2.0
    The added 'v' provides a bit more clarity and it's mentioned in github as a common practice

    Later it's possible we use this to expand support for downloading package asset in multiple mirror sites
    """
    urls = [url]

    url_parts = url.split('/')
    release_tag, filename = url_parts[-2:]

    if release_tag.split('.')[1].startswith('v'):
        release_tag = release_tag.replace('.v', '.', 1)
        if filename.endswith('.tar.gz'):
            filename = filename.replace('.v', '.', 1)

        urls.append('/'.join(url_parts[:-2] + [release_tag, filename]))

    return urls
