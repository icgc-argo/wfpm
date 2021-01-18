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

import re
import sys
from wfpm import PRJ_NAME_REGEX

project_name = '{{ cookiecutter.project_slug }}'

if not re.match(PRJ_NAME_REGEX, project_name):
    print(f"Error: '{project_name}' is not a valid project name (project_slug), expected name pattern: {PRJ_NAME_REGEX}")

    # exits with status 1 to indicate failure
    sys.exit(1)
