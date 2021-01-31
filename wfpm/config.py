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
import yaml
from .utils import auto_config


class Config(object):
    debug: bool = False
    git_user_name: str = None
    git_user_email: str = None
    default_license: str = None

    def __init__(self, debug=False) -> None:
        self.debug = debug

        # find and parse system-wide wfpm config file: $HOME/.wfpmconfig
        home_dir = os.getenv('HOME')
        if not home_dir:
            raise Exception("Environment variable 'HOME' not set.")
        if not os.path.isdir(home_dir):
            raise Exception(f"'HOME' dir ({home_dir}) not exists or not accessible")

        config_file = os.path.join(home_dir, '.wfpmconfig')

        if not os.path.isfile(config_file):
            auto_config(config_file)

        with open(config_file, 'r') as c:
            conf_dict = yaml.safe_load(c)

        if not conf_dict:
            conf_dict = dict()

        fields = ['git_user_name', 'git_user_email']
        if set(fields) - set(conf_dict.keys()):
            raise Exception(
                f"Incomplete config file: {config_file}, required fields: {', '.join(fields)}\n" +
                "Please run 'wfpm config --set' command to generate valid config file."
            )

        else:
            self.git_user_name = conf_dict.get('git_user_name', '')
            self.git_user_email = conf_dict.get('git_user_email', '')
            self.default_license = conf_dict.get('default_license', '')
