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
