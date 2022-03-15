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

from . import extensions

default_config = {
    # should sympy session be started automatically
    'start_session': True,

    # refer to `sympy.init_session` for details # TODO: ignored currently
    'auto_symbols': True,
    'auto_integers': True,

    # extensions that come enabled by default
    'extensions': {
        extensions.inferred_multi.__name__,
    },

    # default extensions that load only in interactive sessions
    'interactive_ext': {
        extensions.aliases.__name__,
        extensions.basic_prompt.__name__,
    }
}

def get_config(ipy):
    return { **default_config, **ipy.config.get('abacus', {}) }
