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

# this may not work for zipped lib, but let's worry about it later
tmplt_path = os.path.join(os.path.dirname(__file__))

project_tmplt = os.path.join(tmplt_path, 'project')
tool_tmplt = os.path.join(tmplt_path, 'tool')
workflow_tmplt = os.path.join(tmplt_path, 'workflow')
function_tmplt = os.path.join(tmplt_path, 'function')
