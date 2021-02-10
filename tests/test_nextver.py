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
def test_good_workon_01(workdir, datafiles):
    run_cmd('git clone https://github.com/ICGC-TCGA-PanCancer/awesome-wfpkgs2.git')
    run_cmd('cd awesome-wfpkgs2 && git fetch --all --tags')

    os.chdir(os.path.join(workdir, 'awesome-wfpkgs2'))

    runner = CliRunner()
    cli_option = ['workon', '-u']
    result = runner.invoke(main, cli_option)

    assert "Package being worked on: <none>" in result.output


@pytest.mark.datafiles(DATA_DIR)
def test_good_workon_nextver_fail_01(workdir, datafiles):
    os.chdir(os.path.join(workdir, 'awesome-wfpkgs2'))

    runner = CliRunner()
    cli_option = ['nextver', 'fastqc-wf2@0.1', '0.1.1']
    result = runner.invoke(main, cli_option)

    assert "No package found as: 'fastqc-wf2@0.1'. Run 'wfpm workon' to display package info." in result.output


@pytest.mark.datafiles(DATA_DIR)
def test_good_workon_nextver_ok(workdir, datafiles):
    os.chdir(os.path.join(workdir, 'awesome-wfpkgs2'))

    runner = CliRunner()
    cli_option = ['nextver', 'fastqc-wf2@0.1.0', '0.1.1']
    result = runner.invoke(main, cli_option)

    assert "Started a new package version: fastqc-wf2@0.1.1" in result.output


@pytest.mark.datafiles(DATA_DIR)
def test_good_workon_02(workdir, datafiles):
    run_cmd('git clone https://github.com/ICGC-TCGA-PanCancer/awesome-wfpkgs2.git')
    run_cmd('cd awesome-wfpkgs2 && git fetch --all --tags')

    os.chdir(os.path.join(workdir, 'awesome-wfpkgs2'))

    runner = CliRunner()
    cli_option = ['workon']
    result = runner.invoke(main, cli_option)

    assert "Package being worked on: fastqc-wf2@0.1.1" in result.output


@pytest.mark.datafiles(DATA_DIR)
def test_good_workon_nextver_fail_02(workdir, datafiles):
    os.chdir(os.path.join(workdir, 'awesome-wfpkgs2'))

    runner = CliRunner()
    cli_option = ['nextver', 'fastqc-wf2@0.1.0', '0.1.1']
    result = runner.invoke(main, cli_option)

    assert "Must stop working on 'fastqc-wf2@0.1.1' before creating a new package version" in result.output
