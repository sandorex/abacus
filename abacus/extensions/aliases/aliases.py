#!/usr/bin/env python3
# abacus
#
# Copyright 2022 Aleksandar Radivojevic
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import platform

def load_ipython_extension(ipy):
    # magic aliases
    for i, j in [
        ('var', 'who'),
        ('val', 'whos'),
    ]:
        ipy.magics_manager.register_alias(i, j)

    # cmd aliases
    if platform.system().lower() == 'windows':
        ipy.alias_manager.define_alias('clear', 'cls') # TODO: check on linux

# def unload_ipython_extension(ipy):
#     pass
