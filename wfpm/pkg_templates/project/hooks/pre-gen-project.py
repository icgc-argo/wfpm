import re
import sys


PJ_REGEX = r'^[a-z][a-z0-9_-]+[a-z0-9]$'

project_name = '{{ cookiecutter.project_name }}'

if not re.match(PJ_REGEX, project_name):
    print('ERROR: %s is not a valid project name! Regex: \'^[a-z][a-z0-9_-]+[a-z0-9]$\'' % project_name)

    # exits with status 1 to indicate failure
    sys.exit(1)
