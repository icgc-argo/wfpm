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
import pytest
import filecmp
from pathlib import Path
from click.testing import CliRunner
from wfpm.cli import main
from wfpm.utils import run_cmd

TEST_DIR = Path(__file__).parent
DATA_DIR = os.path.join(TEST_DIR, 'data')


@pytest.mark.datafiles(DATA_DIR)
def test_good_init(workdir, datafiles):
    # unpack _project_dir.tar.gz to under workdir, then make it cwd
    run_cmd(f'cd {datafiles} && tar xzf _project_dir.tar.gz -C {workdir}')

    runner = CliRunner()
    conf_json = os.path.join(datafiles, 'init', 'good', 'conf.json')
    cli_option = ['init', '-c', conf_json]

    result = runner.invoke(main, cli_option)
    assert "Project initialized in: github-repo" in result.output
    assert os.path.isdir(os.path.join('github-repo', '.git'))
    assert filecmp.cmp(
        os.path.join('_project_dir', '.wfpm'),
        os.path.join('github-repo', '.wfpm'),
    )


@pytest.mark.datafiles(DATA_DIR)
def test_bad_init_01(workdir, datafiles):
    runner = CliRunner()
    conf_json = os.path.join(datafiles, 'init', 'bad', '01.conf.json')
    cli_option = ['init', '-c', conf_json]

    result = runner.invoke(main, cli_option)
    assert "Provided project_slug: 'Github-Repo' invalid" in result.output
    assert "Name invalid, does not match the required pattern" in result.output
