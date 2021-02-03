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
import json
import tempfile
import random
import string
import questionary
from shutil import copytree
from click import echo
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException, FailedHookException
from wfpm import PRJ_NAME_REGEX, GIT_ACCT_REGEX
from wfpm.project import Project
from ..pkg_templates import project_tmplt
from ..utils import run_cmd, validate_project_name, git_cli_readiness


def init_cmd(ctx, conf_json=None):
    project = ctx.obj['PROJECT']
    if project.root:
        echo(f"Already in a package project directory: {project.root}")
        ctx.abort()

    if not git_cli_readiness():
        ctx.exit(1)

    try:
        project_dir = gen_project(ctx, project, project_tmplt=project_tmplt, conf_json=conf_json)
        echo(f"Project initialized in: {os.path.basename(project_dir)}")
    except FailedHookException as ex:
        echo(f"Failed to initialize the project. {ex}")
        ctx.abort()
    except OutputDirExistsException as ex:
        echo(f"Failed to initialize the project. {ex}")
        ctx.abort()

    # recreate the project
    project = Project(project_root=project_dir, debug=project.config.debug)
    ctx.obj['PROJECT'] = project

    cmd = f"cd {project_dir} && git init && git add . && git commit -m 'inital commit' && git branch -M main && " \
          f"git remote add origin git@{project.repo_server}:{project.repo_account}/{project.name}.git"

    out, err, ret = run_cmd(cmd)
    if ret != 0:
        echo(f"Git commands failed, please ensure 'git' is installed. STDERR: {err}. STDOUT: {out}")
        ctx.exit(1)
    else:
        echo(
            "Git repo initialized and first commit done. " +
            f"When ready, you may push to {project.repo_server} using:\n" +
            "git push -u origin main"
        )


def gen_project(
    ctx,
    project=None,
    project_tmplt=None,
    conf_json=None
) -> str:
    conf_dict = {}
    if conf_json:
        conf_dict = json.load(conf_json)

        # TODO: complete the validation of user supplied config JSON
        project_name = conf_dict.get('project_slug', '')
        try:
            validate_project_name(project_name)
        except Exception as ex:
            echo(f"Provided project_slug: '{project_name}' invalid: {ex}")
            ctx.abort()

    else:  # interactively provide inputs
        conf_dict = collect_project_init_info(ctx, project)

    if "_copy_without_render" not in conf_dict:
        conf_dict["_copy_without_render"] = [".github"]

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


def collect_project_init_info(ctx, project=None):
    defaults = {
        "full_name": "Your Name",
        "email": f"{project.config.git_user_email}",
        "project_title": "Awesome Workflow Packages",
        "github_account": "github-account",
        "project_slug": "github-repo",
    }

    project_slug = questionary.text(
            f"Project name / GitHub repo name [{defaults['project_slug']}]:", default=""
        ).ask()

    if project_slug is None:
        ctx.abort()
    elif project_slug == '':
        project_slug = defaults['project_slug']

    if not re.match(PRJ_NAME_REGEX, project_slug):
        echo(f"Error: '{project_slug}' is not a valid project name. Expected pattern: '{PRJ_NAME_REGEX}'")
        ctx.abort()

    if os.path.isdir(project_slug):
        echo(f"Error: '{project_slug}' directory already exists")
        ctx.abort()

    answers = questionary.form(
        github_account=questionary.text(f"GitHub account [{defaults['github_account']}]:", default=""),
        project_title=questionary.text(f"Project title [{defaults['project_title']}]:", default=""),
        full_name=questionary.text(f"Organization or your name [{defaults['full_name']}]:", default=""),
        email=questionary.text(f"Your email [{defaults['email']}]:", default=""),
        open_source_license=questionary.select("Open source license:", choices=[
            "MIT",
            "BSD",
            "ISC",
            "Apache Software License 2.0",
            "GNU General Public License v3",
            "Not open source"
        ])
    ).ask()

    if not answers:
        ctx.abort()

    answers = {'project_slug': project_slug, **answers}

    for q in answers:
        if answers[q] == "" and defaults.get(q):
            answers[q] = defaults[q]

    if not re.match(GIT_ACCT_REGEX, answers['github_account']):
        echo(f"Invalid GitHub account: '{answers['github_account']}'. Excepted pattern: '{GIT_ACCT_REGEX}'")
        ctx.abort()

    echo(json.dumps(answers, indent=4))
    res = questionary.confirm("Please confirm the information and continue:", default=True).ask()

    if not res:
        ctx.abort()

    return answers
