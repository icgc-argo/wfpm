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
from shutil import copytree
from collections import OrderedDict
from click import echo
from cookiecutter.main import cookiecutter
from wfpm import PKG_NAME_REGEX
from ..pkg_templates import tool_tmplt
from ..pkg_templates import workflow_tmplt
from ..pkg_templates import function_tmplt
from ..utils import run_cmd


def new_cmd(ctx, pkg_type, pkg_name, conf_json=None):
    project = ctx.obj['PROJECT']
    if not project.root:
        echo("Not in a package project directory.")
        ctx.abort()

    if project.root != os.getcwd():
        echo(f"Must run this command under the project root dir: {project.root}")
        ctx.abort()

    if not re.match(PKG_NAME_REGEX, pkg_name):
        echo(f"'{pkg_name}' is not a valid package name, expected name pattern: '{PKG_NAME_REGEX}'")
        ctx.abort()

    if os.path.isdir(os.path.join(project.root, pkg_name)):
        echo(f"Package '{ pkg_name }' already exists.")
        ctx.abort()

    name_parts = pkg_name.split('-')
    workflow_name = ''.join([p.capitalize() for p in name_parts])  # workflow name starts with upper
    process_name = workflow_name[0].lower() + workflow_name[1:]  # tool/function name starts with lower

    if pkg_type == 'tool':
        extra_context = {
            '_pkg_name': pkg_name,
            '_repo_type': project.repo_type,
            '_repo_server': project.repo_server,
            '_repo_account': project.repo_account,
            '_repo_name': project.name,
            '_license': project.license,
            '_name': process_name
        }

        path = gen_template(
                ctx,
                template=tool_tmplt,
                pkg_name=pkg_name,
                extra_context=extra_context,
                conf_json=conf_json
            )

    elif pkg_type == 'workflow':
        extra_context = {
            '_pkg_name': pkg_name,
            '_repo_type': project.repo_type,
            '_repo_server': project.repo_server,
            '_repo_account': project.repo_account,
            '_repo_name': project.name,
            '_license': project.license,
            '_name': workflow_name
        }

        path = gen_template(
                ctx,
                template=workflow_tmplt,
                pkg_name=pkg_name,
                extra_context=extra_context,
                conf_json=conf_json
            )

    elif pkg_type == 'function':
        echo("Not implemented yet")
        ctx.exit()

    # create symlinks for 'wfpr_modules'
    cmd = f"cd {path} && ln -s ../wfpr_modules && cd tests && ln -s ../wfpr_modules"
    run_cmd(cmd)
    echo(f"New package created in: {os.path.basename(path)}")


def gen_template(
    ctx,
    template=None,
    pkg_name=None,
    extra_context=None,
    conf_json=None
):
    """
    generate template in a temp dir by calling cookiecutter, then perform necessary post-gen
    check and processing, finally copy the template into the current project root dir
    """
    conf_dict = {}
    if conf_json:
        conf_dict = json.load(conf_json)
        if "_copy_without_render" not in conf_dict:
            conf_dict["_copy_without_render"] = ["*.gz"]

        # TODO: validate of user supplied config JSON

        hidden_fields = {
            "_pkg_name": "{{ cookiecutter._pkg_name }}",
            "_repo_account": "{{ cookiecutter._repo_account }}",
            "_repo_type": "{{ cookiecutter._repo_type }}",
            "_repo_server": "{{ cookiecutter._repo_server }}",
            "_repo_name": "{{ cookiecutter._repo_name }}",
            "_name": "{{ cookiecutter._name }}",
            "_license": "{{ cookiecutter._license }}",
            "_copy_without_render": ["*.gz"]
        }

        conf_dict = {**conf_dict, **hidden_fields}

    with tempfile.TemporaryDirectory() as tmpdirname:
        # copy template directory tree to under tmpdir so that we can replace cookiecutter.json when needed
        dirname = ''.join(random.choice(string.ascii_letters) for i in range(20))
        new_tmplt_dir = os.path.join(tmpdirname, dirname)
        copytree(template, new_tmplt_dir)

        if conf_dict:
            # replace the default cookiecutter.json with user supplied
            with open(os.path.join(new_tmplt_dir, 'cookiecutter.json'), 'w') as j:
                json.dump(conf_dict, j)

        path = cookiecutter(
                template=template,
                extra_context=extra_context,
                output_dir=tmpdirname,
                no_input=True if conf_dict else False
            )

        # fix the list fields in pkg.json
        pkg_dict = json.load(
            open(os.path.join(path, 'pkg.json')),
            object_pairs_hook=OrderedDict
        )

        pkg_dict['keywords'] = [
            d.strip() for d in pkg_dict['keywords'] if d.strip()
        ]

        pkg_dict['dependencies'] = [
            d.strip() for d in pkg_dict['dependencies'] if d.strip()
        ]

        pkg_dict['devDependencies'] = [
            d.strip() for d in pkg_dict['devDependencies'] if d.strip()
        ]

        with open(os.path.join(path, 'pkg.json'), 'w') as p:
            p.write(json.dumps(pkg_dict, indent=4))

        dest = os.path.join(os.getcwd(), pkg_name)
        copytree(path, dest)

    return dest
