import re
import sys


MODULE_REGEX = r'^[a-z][a-z0-9-]+[a-z0-9]$'

module_name = '{{ cookiecutter.package_name }}'

if not re.match(MODULE_REGEX, module_name):
    print('ERROR: %s is not a valid tool name! Regex: \'^[a-z][_a-z0-9]+$\'' % module_name)

    # exits with status 1 to indicate failure
    sys.exit(1)
