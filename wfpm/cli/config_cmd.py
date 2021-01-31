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
from click import echo
from wfpm.utils import auto_config


def config_cmd(ctx, set=False, force=False):
    conf_file = os.path.join(os.getenv('HOME'), '.wfpmconfig')

    if set:
        if os.path.isfile(conf_file) and not force:
            echo(f"Global config file already exists: {conf_file}, will not overwrite without force option '-f'.")
            ctx.abort()

        try:
            auto_config(conf_file)
        except Exception as ex:
            echo(f"Unable to complete auto-config.\n{ex}")

    if os.path.isfile(conf_file):
        with open(conf_file, 'r') as c:
            echo(c.read())
    else:
        echo("Global config file does not exist, please run 'wfpm config --set'")
