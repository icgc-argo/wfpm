import re
import sys


PKG_REGEX = r'^[a-z][a-z0-9-]+[a-z0-9]$'

package_name = '{{ cookiecutter.package_name }}'

if not re.match(PKG_REGEX, package_name):
    print('ERROR: %s is not a valid package name! Regex: \'^[a-z][a-z0-9]+$\'' % package_name)

    # exits with status 1 to indicate failure
    sys.exit(1)
