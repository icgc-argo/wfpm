# -*- coding: utf-8 -*-

import re
import sys
from wfpm import PRJ_NAME_REGEX

project_name = '{{ cookiecutter.project_slug }}'

if not re.match(PRJ_NAME_REGEX, project_name):
    print(f"Error: '{project_name}' is not a valid project name (project_slug), expected name pattern: {PRJ_NAME_REGEX}")

    # exits with status 1 to indicate failure
    sys.exit(1)
