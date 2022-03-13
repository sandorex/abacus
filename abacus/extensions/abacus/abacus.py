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
#

import sympy, sympy.physics.units, platform

from ... import __version__, extensions
from .magic import AbacusMagics

# extensions that come enabled by default
default_extensions = [
    extensions.basic_prompt.__name__,
    extensions.inferred_multi.__name__,
]

def init_env(ipy):
    # add non user globals
    ipy.push({
        'sy': sympy, # TODO: i do not know how to import stuff at startup in
                     # ipython extension
        'u': sympy.physics.units,
    }, False)

def init_aliases(ipy):
    # magic aliases
    for i, j in [
        ('var', 'who'),
        ('val', 'whos'),
    ]:
        ipy.magics_manager.register_alias(i, j)

    # cmd aliases
    if platform.system().lower() == 'windows':
        ipy.alias_manager.define_alias('clear', 'cls') # TODO: check on linux

def load_ipython_extension(ipy):
    init_aliases(ipy)
    init_env(ipy)

    ipy.register_magics(AbacusMagics)

    # load default extensions
    for i in default_extensions:
        ipy.extension_manager.load_extension(i)

    ipy.true_color = True # TODO: idk if this is doing anything at all

def unload_ipython_extension(ipy):
    print('All abacus extensions will be unloaded')

    # TODO try to clean env and aliases

    del ipy.magics_manager.registry[AbacusMagics.__name__] # FIXME: dirty
