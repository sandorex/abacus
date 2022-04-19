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

import ast
from typing import Any, List

from ..shell import ShellExtension, ShellBase, StringTransformer

# TODO: logging into logfile as an option
# TODO: auto reload on extension or after every statement so it keeps working
# properly? may need custom ipython shell?
class Debugger(ast.NodeTransformer, StringTransformer, ShellExtension):
    def __init__(self, shell: ShellBase):
        ShellExtension.__init__(self)

        self.shell = shell

    def register(self):
        # has to be the last!
        self.shell.str_transformers.append(self)
        self.shell.ast_transformers.append(self)

        print('DEBUGGING ENABLED\n'
            + 'LOADING EXTENSIONS WILL BREAK THINGS CURRENTLY')

        return super().register()

    def unregister(self):
        self.shell.str_transformers.remove(self)
        self.shell.ast_transformers.remove(self)

        super().unregister()

    def transform(self, lines: List[str]) -> List[str]:
        print(f'[DEBUG] string transformation result:')
        for i in lines:
            print('> ', i.rstrip())

        return lines

    def visit(self, node: ast.AST) -> Any:
        print(f'[DEBUG] ast transformation result:\n{ast.dump(node, indent=4)}')

        return node
