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

import sympy

from IPython.core.magic import Magics, magics_class, line_magic

@magics_class
class AbacusMagics(Magics):
    @line_magic
    def init(self, line):
        init_session()

        if line != 'quiet':
            print('Sympy session started')

def init_session():
    """Calls `sympy.init_session` with default options"""
    # TODO: respect config when doing this
    sympy.init_session(
        quiet=True,
        use_unicode=True,
        auto_symbols=True,
        auto_int_to_Integer=True,
    )
