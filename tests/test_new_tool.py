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
from wfpm.utils import run_cmd

TEST_DIR = Path(__file__).parent
DATA_DIR = os.path.join(TEST_DIR, 'data')


@pytest.mark.datafiles(DATA_DIR)
def test_good_new_tool(workdir, datafiles):
    # copy _project_dir to under workdir, then make it cwd
    copytree(os.path.join(datafiles, '_project_dir'), os.path.join(workdir, '_project_dir'))
    os.chdir(os.path.join(workdir, '_project_dir'))

    run_cmd('mv .git-db .git')
    # workaround for now, otherwise it complains git branch not clean,
    # two scripts strangely render mode change
    # old mode 100755
    # new mode 100644
    run_cmd('git checkout .')

    runner = CliRunner()
    conf_json = os.path.join(datafiles, 'new_tool', 'good', 'conf.json')
    cli_option = ['new', 'tool', 'fastqc', '-c', conf_json]

    result = runner.invoke(main, cli_option)
    assert "New package created in: fastqc" in result.output
