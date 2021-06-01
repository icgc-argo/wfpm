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

__version__ = "0.7.8"

PRJ_NAME_REGEX = r'^[a-z][0-9a-z\-]*[0-9a-z]+$'
PKG_NAME_REGEX = r'^[a-z][0-9a-z\-]*[0-9a-z]+$'
PKG_VER_REGEX = r'^[0-9]+\.[0-9]+\.[0-9]+(?:\.[0-9]+)?(?:-[0-9a-z\.]+)?$'
GIT_ACCT_REGEX = r'^[a-zA-Z]+[0-9a-zA-Z_-]*$'
CONTAINER_REG_ACCT_REGEX = r'^[a-z]+[0-9a-z_-]*$'
