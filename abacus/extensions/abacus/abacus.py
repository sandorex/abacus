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

import sys

from ... import config
from .magic import AbacusMagics

def load_ipython_extension(ipy):
    ipy.register_magics(AbacusMagics)
    ipy.ex('import sympy')

    cfg = config.get_config(ipy)

    # load extensions
    for i in cfg.get('extensions'):
        ipy.extension_manager.load_extension(i)

    if hasattr(sys, 'ps1'):
        # load interactive only extensions
        for i in cfg.get('interactive_ext'):
            ipy.extension_manager.load_extension(i)

    if cfg.get('start_session') == True:
        ipy.run_line_magic('init', 'quiet')

def unload_ipython_extension(ipy):
    del ipy.magics_manager.registry[AbacusMagics.__name__] # FIXME: dirty
