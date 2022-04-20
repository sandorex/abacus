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

import ast, code

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from ..shell import CodeObj, ShellBase

# TODO: basic shell is kinda borked, StringTransformer changes messed it up
class BasicShell(ShellBase):
    def __init__(self):
        super().__init__()

        self._ns = {}
        self._str_transformers = []
        self._ast_transformers = []
        self._event_callbacks = {}
        self.interpreter = code.InteractiveInterpreter(self.user_ns)

        self.init_ns()

    @property
    def user_ns(self) -> Dict[str, Any]:
        return self._ns

    @property
    def event_callbacks(self) -> Dict[str, List[Callable]]:
        return self._event_callbacks

    @property
    def ast_transformers(self) -> List[ast.NodeTransformer]:
        return self._ast_transformers

    @property
    def str_transformers(self) -> List[Callable]:
        return self._str_transformers

    @staticmethod
    def shell_type() -> str:
        return 'basic'

    def run_interactive(self,
                        code: Union[str, ast.Module, CodeObj],
                        transform=True):
        # TODO: rework this whole thing, it's a mess
        # maybe even change the function into multiple per type supplied

        if isinstance(code, str):
            if transform:
                code = self.str_transform(code.splitlines(keepends=True))

            code = ast.parse(''.join(code), filename='<input>', mode='exec')

        if isinstance(code, ast.AST):
            if transform:
                self.ast_transform(code)

        (stmt, module) = self.compile_ast(code)

        if module is not None:
            self.interpreter.runcode(module)

        self.interpreter.runcode(stmt)

    def compile_ast(self, node: ast.Module) -> Tuple[CodeObj, Optional[CodeObj]]:
        """Compiles the node and returns the last statement as `ast.Interactive`
        and if there are more than one statements then rest of the module is
        also returned

        Returns last statements, rest of statements"""

        stmt = node.body.pop(-1)
        ast.fix_missing_locations(stmt)
        stmt = compile(ast.Interactive(body=[stmt]), filename='<input>', mode='single')

        module = None
        if len(node.body) >= 1:
            module = compile(node, filename='<input>', mode='exec')

        return stmt, module
