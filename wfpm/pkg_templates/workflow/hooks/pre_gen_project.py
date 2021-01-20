# -*- coding: utf-8 -*-

import re
import sys
from wfpm import PKG_NAME_REGEX

pkg_name = '{{ cookiecutter._pkg_name }}'

if not re.match(PKG_NAME_REGEX, pkg_name):
    print(f"Error: '{pkg_name}' is not a valid package name, expected name pattern: '{PKG_NAME_REGEX}'")

    # exits with status 1 to indicate failure
    sys.exit(1)
