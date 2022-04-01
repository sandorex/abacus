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
