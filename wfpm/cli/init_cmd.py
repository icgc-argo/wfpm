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
import yaml
import tempfile
import random
import string
from shutil import copytree
from click import echo
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException, FailedHookException
from ..pkg_templates import project_tmplt
from ..utils import run_cmd, validate_project_name
from ..config import Config


def init_cmd(ctx, conf_json=None):
    project = ctx.obj['PROJECT']
    if project.root:
        echo(f"Already in a package project directory: {project.root}")
        ctx.abort()

    try:
        project_dir = gen_project(ctx, project_tmplt=project_tmplt, conf_json=conf_json)
        echo(f"Project initialized in: {os.path.basename(project_dir)}")
    except FailedHookException as ex:
        echo(f"Failed to initialize the project. {ex}")
        ctx.abort()
    except OutputDirExistsException as ex:
        echo(f"Failed to initialize the project. {ex}")
        ctx.abort()

    with open(os.path.join(project_dir, '.wfpm'), 'r') as c:
        conf = yaml.safe_load(c)

    cmd = f"cd {project_dir} && git init && git add . && git commit -m 'inital commit' && git branch -M main && " \
          f"git remote add origin git@{conf['repo_server']}:{conf['repo_account']}/{conf['project_name']}.git"

    out, err, ret = run_cmd(cmd)
    if ret != 0:
        echo(f"Git commands failed, please ensure 'git' is installed. STDERR: {err}. STDOUT: {out}")
        ctx.exit(1)
    else:
        echo(
            "Git repo initialized and first commit done. " +
            f"When ready, you may push to {conf['repo_server']} using:\n" +
            "git push -u origin main"
        )


def gen_project(
    ctx,
    project_tmplt=None,
    conf_json=None
) -> str:
    conf_dict = {}
    if conf_json:
        conf_dict = json.load(conf_json)
        if "_copy_without_render" not in conf_dict:
            conf_dict["_copy_without_render"] = [".github"]

        # TODO: complete the validation of user supplied config JSON
        project_name = conf_dict.get('project_slug', '')
        try:
            validate_project_name(project_name)
        except Exception as ex:
            echo(f"Provided project_slug: '{project_name}' invalid: {ex}")
            ctx.abort()

    with tempfile.TemporaryDirectory() as tmpdirname:
        # copy template directory tree to under tmpdir so that we can replace cookiecutter.json when needed
        dirname = ''.join(random.choice(string.ascii_letters) for i in range(20))
        new_tmplt_dir = os.path.join(tmpdirname, dirname)
        copytree(project_tmplt, new_tmplt_dir)

        if conf_dict:
            # replace the default cookiecutter.json with user supplied
            with open(os.path.join(new_tmplt_dir, 'cookiecutter.json'), 'w') as j:
                json.dump(conf_dict, j)

        project_dir = cookiecutter(
            new_tmplt_dir,
            no_input=True if conf_dict else False
        )

        return project_dir
