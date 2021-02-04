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
from pathlib import Path
from shutil import copytree
from click.testing import CliRunner
from wfpm.cli import main

TEST_DIR = Path(__file__).parent
DATA_DIR = os.path.join(TEST_DIR, 'data')


@pytest.mark.datafiles(DATA_DIR)
def test_good_new_workflow(workdir, datafiles):
    # copy _project_dir to under workdir, then make it cwd
    copytree(os.path.join(datafiles, '_project_dir'), os.path.join(workdir, '_project_dir'))
    os.chdir(os.path.join(workdir, '_project_dir'))

    runner = CliRunner()
    conf_json = os.path.join(datafiles, 'new_workflow', 'good', '02.conf.json')
    cli_option = ['new', 'workflow', 'fastqc-wf2', '-c', conf_json]

    result = runner.invoke(main, cli_option)
    assert "New package created in: fastqc-wf2" in result.output

    # after installation, check if tests of the installed dependencies run successful
    assert "Tested package: demo-utils@1.2.0, PASSED: 3, FAILED: 0" in result.output
    assert "Tested package: fastqc-wf@0.2.0, PASSED: 1, FAILED: 0" in result.output


@pytest.mark.datafiles(DATA_DIR)
def test_good_new_workflow_install(workdir, datafiles):
    os.chdir(os.path.join(workdir, '_project_dir', 'fastqc-wf2'))

    runner = CliRunner()
    cli_option = ['install']
    result = runner.invoke(main, cli_option)

    assert "Pakcage already installed: " in result.output


@pytest.mark.datafiles(DATA_DIR)
def test_good_new_workflow_test(workdir, datafiles):
    os.chdir(os.path.join(workdir, '_project_dir', 'fastqc-wf2'))

    runner = CliRunner()
    cli_option = ['test']  # right, we are testing 'test' here
    result = runner.invoke(main, cli_option)

    assert "Tested package: fastqc-wf2, PASSED: 1, FAILED: 0" in result.output
