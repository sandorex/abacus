#!/usr/bin/env python3
# abacus
#
# Copyright (C) 2022 Aleksandar Radivojevic
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
