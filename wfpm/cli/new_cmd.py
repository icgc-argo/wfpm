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
import sys
import json
import tempfile
import random
import string
import questionary
from pathlib import Path
from typing import List
from shutil import copytree, rmtree
from collections import OrderedDict
from click import echo
from cookiecutter.main import cookiecutter
from wfpm import PKG_NAME_REGEX, PKG_VER_REGEX, CONTAINER_REG_ACCT_REGEX, __version__ as ver
from wfpm.project import Project
from wfpm.package import Package
from ..pkg_templates import tool_tmplt
from ..pkg_templates import workflow_tmplt
from ..pkg_templates import function_tmplt
from ..utils import run_cmd
from .install_cmd import install_cmd


def new_cmd(project, pkg_type, pkg_name, conf_json=None):
    validate_input(project, pkg_name)

    name_parts = pkg_name.split('-')
    workflow_name = ''.join([p.capitalize() for p in name_parts])  # workflow name starts with upper
    process_name = workflow_name[0].lower() + workflow_name[1:]  # tool/function name starts with lower

    license_text_short = 'Please add your license short form text here.'

    # read from 'LICENSE-short' file if exists
    license_short_file = os.path.join(project.root, 'LICENSE-short')
    if os.path.isfile(license_short_file):
        with open(license_short_file, 'r') as f:
            license_text_short = ''
            for line in f:
                license_text_short += f"  {line}" if line.strip() else line

    if pkg_type == 'tool':
        extra_context = {
            '_pkg_name': pkg_name,
            '_repo_type': project.repo_type,
            '_repo_server': project.repo_server,
            '_repo_account': project.repo_account,
            '_repo_name': project.name,
            '_license': project.license,
            '_license_text_short': license_text_short,
            '_name': process_name
        }

        template = tool_tmplt

    elif pkg_type == 'workflow':
        extra_context = {
            '_pkg_name': pkg_name,
            '_repo_type': project.repo_type,
            '_repo_server': project.repo_server,
            '_repo_account': project.repo_account,
            '_repo_name': project.name,
            '_license': project.license,
            '_license_text_short': license_text_short,
            '_name': workflow_name
        }

        template = workflow_tmplt

    elif pkg_type == 'function':
        template = function_tmplt

        echo("Not implemented yet")
        sys.exit(1)

    path = gen_template(
            project,
            template=template,
            pkg_name=pkg_name,
            extra_context=extra_context,
            conf_json=conf_json
        )

    # create symlinks for 'wfpr_modules'
    cmd = f"cd {path} && ln -s ../wfpr_modules && cd tests && ln -s ../wfpr_modules"
    run_cmd(cmd)

    new_pkg = Package(pkg_json=os.path.join(path, 'pkg.json'))
    project.git.cmd_new_branch(new_pkg.fullname)
    project = Project(project_root=project.root, debug=project.debug)

    paths_to_add = f"{path} {os.path.join(project.root, 'wfpr_modules')}"
    project.git.cmd_add_and_commit(path=paths_to_add, message=f'[wfpm v{ver}] added starting template for {project.pkg_workon}')

    echo(f"New package created in: {os.path.basename(path)}. Starting template added and "
         "committed to git. Please continue working on it.")


def validate_input(project, pkg_name):
    if not project.root:
        echo("Not in a package project directory.")
        sys.exit(1)

    if project.root != os.getcwd():
        echo(f"Must run this command under the project root dir: {project.root}")
        sys.exit(1)

    if not (project.git.user_name and project.git.user_email):
        echo("Git not configured with 'user.name' and 'user.email', please set them using 'git config'.")
        sys.exit(1)

    if project.pkg_workon:
        echo(f"Must stop working on '{project.pkg_workon}' before creating a new package. "
             "Please run: wfpm workon -s")
        sys.exit(1)

    if not re.match(PKG_NAME_REGEX, pkg_name):
        echo(f"'{pkg_name}' is not a valid package name, expected name pattern: '{PKG_NAME_REGEX}'")
        sys.exit(1)

    if os.path.isdir(os.path.join(project.root, pkg_name)):
        echo(f"Package '{ pkg_name }' already exists.")
        sys.exit(1)

    for pkg in project.pkgs_in_dev:
        if pkg_name == pkg.split('@')[0]:
            echo(f"Package '{pkg_name}' is already in development as '{pkg}'. "
                 f"To continue work on it, run: wfpm workon {pkg}")
            sys.exit(1)

    for pkg in project.pkgs_released:
        if pkg_name == pkg.split('@')[0]:
            echo(f"Package '{pkg_name}' is already released as '{pkg}', not create.")
            sys.exit(1)

    if not project.git.branch_clean():
        echo(f"Unable to create new package, git branch '{project.git.current_branch}' not clean. "
             "Please complete current work and commit changes.")
        sys.exit(1)


def gen_template(
    project=None,
    template=None,
    pkg_name=None,
    extra_context=None,
    conf_json=None
):
    """
    generate template in a temp dir by calling cookiecutter, then perform necessary post-gen
    check and processing, finally copy the template into the current project root dir
    """
    pkg_type = os.path.basename(template)
    conf_dict = {}
    if conf_json:
        conf_dict = json.load(conf_json)
        # TODO: validate of user supplied config JSON

        if pkg_type == 'tool' and conf_dict.get("container_registry", "") == "ghcr.io":
            conf_dict['registry_account'] = project.repo_account

    else:
        conf_dict = collect_new_pkg_info(project, template)

    hidden_fields = {
        "_pkg_name": "{{ cookiecutter._pkg_name }}",
        "_repo_account": "{{ cookiecutter._repo_account }}",
        "_repo_type": "{{ cookiecutter._repo_type }}",
        "_repo_server": "{{ cookiecutter._repo_server }}",
        "_repo_name": "{{ cookiecutter._repo_name }}",
        "_name": "{{ cookiecutter._name }}",
        "_license": "{{ cookiecutter._license }}",
        "_license_text_short": "{{ cookiecutter._license_text_short }}",
        "_copy_without_render": ["*.gz", "*.bam"]
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
                template=new_tmplt_dir,
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

        installed_pkgs, failed_pkgs = install_cmd(
                                          pkg_json=os.path.join(path, 'pkg.json')
                                      )

        if failed_pkgs:
            echo(f"Failed to install dependencies: {', '.join(failed_pkgs)}")
            sys.exit(1)

        main_script_name = pkg_dict['main'] if pkg_dict['main'].endswith('.nf') else f"{pkg_dict['main']}.nf"
        if pkg_type == 'workflow':
            # update workflow main script with proper include/call/output
            update_wf_pkg_scripts_nf(
                main_script=os.path.join(path, main_script_name),
                checker_script=os.path.join(path, 'tests', 'checker.nf'),
                package=Package(pkg_json=os.path.join(path, 'pkg.json')),
                deps=installed_pkgs,
                deps_installed_dir=tmpdirname
            )
        elif pkg_type == 'tool':
            # update tool main scripts, ie, process and wrapper python script
            update_tool_pkg_scripts_nf(
                main_script=os.path.join(path, main_script_name)
            )

        # copy generated new package dir
        dest = os.path.join(os.getcwd(), pkg_name)
        copytree(path, dest)

        # copy installed deps (skip those already installed)
        for pkg in installed_pkgs:
            pkg_uri = pkg.pkg_uri
            dep_src = os.path.join(tmpdirname, 'wfpr_modules', *(pkg_uri.split('/')))
            dep_dest = os.path.join(project.root, 'wfpr_modules', *(pkg_uri.split('/')))

            if os.path.exists(dep_dest):
                # we could choose skipping for previously installed package, but let's
                # remove and re-copying again, we may later let the user choose what to do
                rmtree(dep_dest)

            # remove temp files created by tests
            cmd = f"cd {dep_src}/tests && rm -fr work .nextflow* outdir"
            # remove symlinks 'wfpr_modules'
            cmd += f" && cd {dep_src} && rm -f wfpr_modules && cd tests && rm -f wfpr_modules"
            run_cmd(cmd)

            echo(f"Copying dependency '{pkg_uri}' to: {os.path.join(project.root, 'wfpr_modules')}")
            copytree(dep_src, dep_dest)

            # create symlinks 'wfpr_modules'
            cmd = f"cd {dep_dest} && ln -s ../../../../../wfpr_modules . && " \
                  "cd tests && ln -s ../wfpr_modules ."
            run_cmd(cmd)

    return dest


def collect_new_pkg_info(project=None, template=None):
    pkg_type = os.path.basename(template)

    defaults = {
        "full_name": f"{project.git.user_name}",
        "email": f"{project.git.user_email}",
        "pkg_version": "0.1.0",
    }

    if pkg_type == 'tool':
        defaults.update({
            "pkg_description": "FastQC tool",
            "keywords": "bioinformatics, seq, qc metrics",
            "docker_base_image": "pegi3s/fastqc:0.11.9",
            "container_registry": "ghcr.io",
            "registry_account": f"{project.repo_account}",
            "dependencies": "",
            "devDependencies": "",
        })
    elif pkg_type == 'workflow':
        defaults.update({
            "pkg_description": "FastQC workflow",
            "keywords": "bioinformatics, seq, qc metrics",
            "dependencies": "github.com/icgc-argo/demo-wfpkgs/demo-utils@1.3.0, "
                            "github.com/icgc-tcga-pancancer/awesome-wfpkgs1/demo-fastqc@0.2.0",
            "devDependencies": "",
        })
    elif pkg_type == 'function':
        defaults.update({
            "pkg_description": "Awesome functions",
            "keywords": "bioinformatics",
            "dependencies": "",
            "devDependencies": "",
        })

    answers_1 = questionary.form(
        full_name=questionary.text(f"Your name [{defaults['full_name']}]:", default=""),
        email=questionary.text(f"Your email [{defaults['email']}]:", default=""),
        pkg_version=questionary.text(f"Package version [{defaults['pkg_version']}]:", default=""),
        pkg_description=questionary.text(f"Package description [{defaults['pkg_description']}]:", default=""),
        keywords=questionary.text(f"Keywords (use ',' to separate keywords) [{defaults['keywords']}]:", default=""),
    ).ask()

    if not answers_1:
        sys.exit(1)

    if answers_1.get('pkg_version') and not re.match(PKG_VER_REGEX, answers_1['pkg_version']):
        echo(f"Error: '{answers_1['pkg_version']}' is not a valid package version. "
             f"Expected pattern: '{PKG_VER_REGEX}'")
        sys.exit(1)

    if pkg_type == 'tool':
        tool_only_answers = questionary.form(
            docker_base_image=questionary.text(
                f"Docker base image [{defaults.get('docker_base_image', '')}]:", default=""),
            container_registry=questionary.text(
                f"Container registory [{defaults.get('container_registry', '')}]:", default=""),
            registry_account=questionary.text(
                f"Container registory account [{defaults.get('registry_account', '')}]:", default=""),
        ).ask()

        if not tool_only_answers:
            sys.exit(1)

        if tool_only_answers.get('registry_account') and \
                not re.match(CONTAINER_REG_ACCT_REGEX, tool_only_answers['registry_account']):
            echo(f"Error: '{tool_only_answers['registry_account']}' is not a valid container registry account. "
                 f"Expected pattern: '{CONTAINER_REG_ACCT_REGEX}'")
            sys.exit(1)

    else:
        tool_only_answers = {}

    dependencies = questionary.text(
            f"Dependencies (enter 'n' to indicate no dependency; use ',' to separate dependencies) [{defaults['dependencies']}]:", default=""
        ).ask()

    if dependencies is None:
        sys.exit(1)
    elif dependencies.lower() == 'n':
        dependencies = ""
    elif dependencies == '':
        dependencies = defaults['dependencies']

    devDependencies = questionary.text(
            f"devDependencies (enter 'n' to indicate no dependency; use ',' to separate devDependencies) [{defaults['devDependencies']}]:", default=""
        ).ask()

    if devDependencies is None:
        sys.exit(1)
    elif devDependencies.lower() == 'n':
        devDependencies = ""
    elif devDependencies == '':
        devDependencies = defaults['devDependencies']

    answers = {
        **answers_1,
        **tool_only_answers
    }

    for q in answers:
        if answers[q] == "" and defaults.get(q):
            answers[q] = defaults[q]

    answers.update({
        'dependencies': dependencies,
        'devDependencies': devDependencies
    })

    echo(json.dumps(answers, indent=4))
    res = questionary.confirm("Please confirm the information and continue:", default=True).ask()

    if not res:
        sys.exit(1)

    return answers


def update_wf_pkg_scripts_nf(
    main_script: str = None,
    checker_script: str = None,
    package: Package = None,
    deps: List[Package] = [],
    deps_installed_dir: str = None
) -> None:
    with open(main_script, 'r') as f:
        main_script_str = f.read()

    # let's set up a convention here, packages whose name starts with 'demo-fastqc' and 'demo-utils'
    # are reserved for demonstration purposes. We expect them to have fixed processes and their
    # interfaces, ie, input and output params and types etc. With this we will be able to generate
    # workflow parts: take (input), main (body) and emit (output)
    # Here are the specific rules:
    #   - replace 'demoCopyFile' by workflow/process name from 'demo-fastqc*' if it's a dependency
    #   - add 'cleanupWorkdir' in main section when 'demo-utils' is a dependency

    dep_names = [dep.name for dep in deps if dep.pkg_uri in package.dependencies]
    has_demo_fastqc_dep = len([dname for dname in dep_names if dname.startswith('demo-fastqc')]) > 0

    # hardcode test job files for now
    test_file_names = ['test-job-1.json', 'test-job-2.json']
    for test_file_name in test_file_names:
        test_job_file = os.path.join(Path(checker_script).parent, test_file_name)

        if os.path.isfile(test_job_file) and not has_demo_fastqc_dep:
            job_dict = json.load(
                open(test_job_file),
                object_pairs_hook=OrderedDict
            )
            job_dict['expected_output'] = 'expected/expected.test_rg_3.bam'

            with open(test_job_file, 'w') as j:
                j.write(json.dumps(job_dict, indent=4))

    main_call = 'demoCopyFile'

    # include section
    include_statements = []
    for dep in deps:
        if dep.pkg_uri not in package.dependencies:  # only include direct deps
            continue

        import_path = os.path.join('.', 'wfpr_modules', dep.pkg_uri, dep.main)
        import_script_file = os.path.join(deps_installed_dir, import_path)

        import_items = get_export_items(
            pkg_name=dep.name,
            script_file=(import_script_file if import_script_file.endswith('.nf') else f"{import_script_file}.nf")
        )

        if dep.name.startswith('demo-fastqc'):
            main_call = import_items[0]

        include_statements.append(
                                    "include { " +
                                    '; '.join(import_items) + " } " +
                                    f"from '{import_path}' " +
                                    "params([*:params, 'cleanup': false])"
                                 )

    main_script_str = script_section_replacement(
        script_str=main_script_str,
        section='include',
        fragments=include_statements,
        keep_original=not has_demo_fastqc_dep
    )

    # input section
    input_statements = []
    main_script_str = script_section_replacement(
        script_str=main_script_str,
        section='input',
        fragments=input_statements,
        keep_original=True
    )

    # main section
    main_statements = []
    if has_demo_fastqc_dep:
        main_statements.append(
            f'{main_call}(input_file)'
        )

    if 'demo-utils' in dep_names:
        main_statements.append(
            "if (params.cleanup) { " + f"cleanupWorkdir({main_call}.out, true)" + " }"
        )

    main_script_str = script_section_replacement(
        script_str=main_script_str,
        section='main',
        fragments=main_statements,
        keep_original=not has_demo_fastqc_dep
    )

    # output section
    output_statements = []
    if has_demo_fastqc_dep:
        output_statements.append(
            f"output_file = {main_call}.out.output_file"
        )

    main_script_str = script_section_replacement(
        script_str=main_script_str,
        section='output',
        fragments=output_statements,
        keep_original=not has_demo_fastqc_dep
    )

    with open(main_script, 'w') as f:
        f.write(main_script_str)


def script_section_replacement(
    script_str: str = None,
    section: str = None,
    fragments: str = None,
    keep_original: bool = False
) -> str:
    if section not in ('include', 'input', 'main', 'output'):
        raise Exception(f"Unknown section name: {section}. Allowed sections: include, input, main, output")

    start_line_pattern = re.compile(f"(\\s*)// {section} section starts")
    end_line_pattern = re.compile(f"(\\s*)// {section} section ends")

    updated_script_str = ''

    in_section = False
    leading_space = ''
    original_lines = []
    replacement_lines = []
    for line in script_str.split('\n'):
        sec_start = re.match(start_line_pattern, line)
        sec_end = re.match(end_line_pattern, line)

        if sec_start:
            in_section = True
            leading_space = sec_start.groups()[0]
            replacement_lines = [f"{leading_space}{frag}" for frag in fragments]
            continue

        elif sec_end:
            in_section = False
            if keep_original:
                line = '\n'.join(original_lines) + '\n'
            else:
                line = ''

            if replacement_lines:
                line = line + '\n'.join(replacement_lines)

        if in_section:
            original_lines.append(line)
        else:
            updated_script_str = updated_script_str + line + '\n'

    return updated_script_str.strip()


def get_export_items(pkg_name=None, script_file=None):
    export_items = []
    # hardcode for demo-utils
    if pkg_name == 'demo-utils':
        # this is an imported (as opposite to defined) item in demo-utils.nf
        export_items.append('cleanupWorkdir')

    # this is a very rudimentary implementation of finding exportable names
    with open(script_file, 'r') as f:
        for line in f:
            workflow_name = re.match(r'^workflow\s+([A-Z][0-9a-zA-Z]+)\s*\{', line)
            if workflow_name:
                export_items.append(workflow_name.groups()[0])

            process_name = re.match(r'^process\s+([a-z][0-9a-zA-Z]+)\s*\{', line)
            if process_name:
                export_items.append(process_name.groups()[0])

            function_name = re.match(r'^def\s+([a-z][0-9a-zA-Z]+)\s*\(', line)
            if function_name:
                export_items.append(function_name.groups()[0])

    return export_items


def update_tool_pkg_scripts_nf(main_script=None):
    # first detect base docker image, if it's not 'fastqc', then swap out `fastqc` command
    # call with a simple `cp` command in the <main>.py file. Also need to update test job
    # json files to replace expected file to a copy of input file
    tool_dir = Path(main_script).parent
    dockerfile = os.path.join(tool_dir, 'Dockerfile')
    main_py_script = os.path.splitext(main_script)[0] + '.py'
    test_dir = os.path.join(tool_dir, 'tests')

    with open(dockerfile, 'r') as d:
        for line in d:
            line = line.strip()
            if line.startswith('FROM ') and ('/fastqc:' in line or line.endswith('/fastqc')):
                return  # done, do nothing

    # update main_py_script, replace 'fastqc -o {args.output_dir} {args.input_file}' by 'cp {args.input_file} {args.output_dir}/'
    with open(main_py_script, 'r') as f:
        main_py_script_str = f.read()

    updated_py_script_str = ''
    for line in main_py_script_str.split('\n'):
        if line.strip().startswith('subprocess.run'):
            line = line.replace('fastqc -o {args.output_dir} {args.input_file}', 'cp {args.input_file} {args.output_dir}/', 1)

        updated_py_script_str = updated_py_script_str + line + '\n'

    with open(main_py_script, 'w') as f:
        f.write(updated_py_script_str)

    # hardcode test job files for now, a bit duplicated code with update_wf_pkg_scripts_nf
    test_file_names = ['test-job-1.json', 'test-job-2.json']
    for test_file_name in test_file_names:
        test_job_file = os.path.join(test_dir, test_file_name)

        if os.path.isfile(test_job_file):
            job_dict = json.load(
                open(test_job_file),
                object_pairs_hook=OrderedDict
            )
            job_dict['expected_output'] = 'expected/expected.test_rg_3.bam'

            with open(test_job_file, 'w') as j:
                j.write(json.dumps(job_dict, indent=4))
