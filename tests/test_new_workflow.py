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
from click.testing import CliRunner
from wfpm.cli import main
from wfpm.utils import run_cmd

TEST_DIR = Path(__file__).parent
DATA_DIR = os.path.join(TEST_DIR, 'data')


@pytest.mark.datafiles(DATA_DIR)
def test_good_new_workflow(workdir, datafiles):
    # unpack _project_dir.tar.gz to under workdir, then make it cwd
    run_cmd(f'cd {datafiles} && tar xzf _project_dir.tar.gz -C {workdir}')
    os.chdir(os.path.join(workdir, '_project_dir'))

    runner = CliRunner()
    conf_json = os.path.join(datafiles, 'new_workflow', 'good', '01.conf.json')
    cli_option = ['new', 'workflow', 'demo-fastqc-wf', '-c', conf_json]

    result = runner.invoke(main, cli_option)
    assert "New package created in: demo-fastqc-wf" in result.output

    # after installation, check if tests of the installed dependencies run successful
    assert "Tested package: demo-utils@1.3.0, PASSED: 3, FAILED: 0" in result.output
    assert "Checker script version '0.1.0' does not match version in pkg.json '0.2.0'" in result.output

    assert "Copying dependency 'github.com/icgc-argo/demo-wfpkgs/demo-utils@1.3.0' to:" in result.output


@pytest.mark.datafiles(DATA_DIR)
def test_good_new_workflow_install(workdir, datafiles):
    os.chdir(os.path.join(workdir, '_project_dir', 'demo-fastqc-wf'))

    runner = CliRunner()
    cli_option = ['install']
    result = runner.invoke(main, cli_option)

    assert "Package already installed: " in result.output


@pytest.mark.datafiles(DATA_DIR)
def test_good_new_workflow_install_force(workdir, datafiles):
    os.chdir(os.path.join(workdir, '_project_dir', 'demo-fastqc-wf'))

    runner = CliRunner()
    cli_option = ['install', '-f']
    result = runner.invoke(main, cli_option)

    assert "Tested package: demo-utils@1.3.0, PASSED: 3, FAILED: 0" in result.output
    assert "Checker script version '0.1.0' does not match version in pkg.json '0.2.0'" in result.output


@pytest.mark.datafiles(DATA_DIR)
def test_good_new_workflow_test(workdir, datafiles):
    os.chdir(os.path.join(workdir, '_project_dir', 'demo-fastqc-wf'))

    runner = CliRunner()
    cli_option = ['test']  # right, we are testing 'test' here
    result = runner.invoke(main, cli_option)

    assert "Tested package: demo-fastqc-wf, PASSED: 2, FAILED: 0" in result.output


@pytest.mark.datafiles(DATA_DIR)
def test_good_new_workflow_test_main_script_directly(workdir, datafiles):
    os.chdir(os.path.join(workdir, '_project_dir', 'demo-fastqc-wf', 'tests'))

    stdout, stderr, retcode = run_cmd('nextflow run ../main.nf -params-file test-job-1.json')

    assert retcode == 0
    assert ":demoFastqc     [100%] 1 of 1" in stdout


@pytest.mark.datafiles(DATA_DIR)
def test_good_new_workflow_workon(workdir, datafiles):
    os.chdir(os.path.join(workdir, '_project_dir', 'demo-fastqc-wf'))

    runner = CliRunner()
    cli_option = ['workon']
    result = runner.invoke(main, cli_option)

    assert "Package being worked on: demo-fastqc-wf@0.2.0" in result.output
    assert "Packages released: <none>\nPackages in development:\n  demo-fastqc-wf: 0.2.0\n  fastqc: 0.2.0" in result.output


@pytest.mark.datafiles(DATA_DIR)
def test_good_new_workflow_workon_stop_fail(workdir, datafiles):
    os.chdir(os.path.join(workdir, '_project_dir', 'demo-fastqc-wf'))

    runner = CliRunner()
    cli_option = ['workon', '-s']
    result = runner.invoke(main, cli_option)

    assert "Must run this command under project root dir" in result.output


@pytest.mark.datafiles(DATA_DIR)
def test_good_new_workflow_workon_stop_ok(workdir, datafiles):
    os.chdir(os.path.join(workdir, '_project_dir'))

    runner = CliRunner()
    cli_option = ['workon', '-s']
    result = runner.invoke(main, cli_option)

    assert "Stopped work on demo-fastqc-wf@0.2.0" in result.output


@pytest.mark.datafiles(DATA_DIR)
def test_good_new_workflow_workon_none(workdir, datafiles):
    os.chdir(os.path.join(workdir, '_project_dir'))

    runner = CliRunner()
    cli_option = ['workon']
    result = runner.invoke(main, cli_option)

    assert "Package being worked on: <none>" in result.output
    assert "Packages released: <none>\nPackages in development:\n  demo-fastqc-wf: 0.2.0\n  fastqc: 0.2.0" in result.output
