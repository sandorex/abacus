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
import code

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from ..shell import CodeObj, ShellBase


class BasicShell(ShellBase):
    """Basic shell that does basic input cleanup and managing, made for testing
    and for other shells to be based on top of it"""

    def __init__(self):
        super().__init__()

        self._ns = {}
        self._str_transformers = []
        self._ast_transformers = []
        self._event_callbacks = {}
        self.interpreter = code.InteractiveInterpreter(self.user_ns)

        self.load()

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
        return "basic"

    # NOTE: ShellBase.run can only be used with a string
    def run(self, code: Union[str, ast.Module, ast.Expression, CodeObj]):
        """Evaluates the code inside the namespace after ast and string
        transformations and then triggers `post_execute` event

        Do note that not all transformations can be done on all types of input:
            `str`: All transformations are performed
            `ast.Module` or `ast.Expression`: Only AST transformation will be performed
            `CodeObj`: No transformation is done"""

        # TODO: rework this whole thing, it's a mess

        if isinstance(code, str):
            code = self.str_transform(code.strip().splitlines(keepends=True))

            code = ast.parse("".join(code), filename="<input>", mode="exec")

        if isinstance(code, ast.AST):
            self.ast_transform(code)

        (stmt, module) = self.compile_ast(code)

        if module is not None:
            self.interpreter.runcode(module)

        # TODO: experiment with manually printing instead of single eval, that
        # way i can control how everything is printed and for example single
        # value inside an array can be extracted
        self.interpreter.runcode(stmt)

        self.trigger_event(self.EVENT_POST_EXECUTE)

    def compile_ast(
        self, node: ast.Module
    ) -> Tuple[CodeObj, Optional[CodeObj]]:
        """Compiles the node and returns the last statement as `ast.Interactive`
        and if there are more than one statements then rest of the module is
        also returned

        Returns last statements, rest of statements"""

        stmt = node.body.pop(-1)
        ast.fix_missing_locations(stmt)
        stmt = compile(
            ast.Interactive(body=[stmt]), filename="<input>", mode="single"
        )

        module = None
        if len(node.body) >= 1:
            module = compile(node, filename="<input>", mode="exec")

        return stmt, module

    def ast_transform(self, node: ast.AST) -> ast.AST:
        """Performs AST transformation on the node

        WARNING: the input `node` may be modified in the process"""

        i: ast.NodeTransformer
        for i in self.ast_transformers:
            i.visit(node)

        return node

    def str_transform(self, code: List[str]) -> List[str]:
        """Performs string transformation on the code

        WARNING: the input `code` may be modified in the process"""

        i: Callable[[str], str]
        for i in self.str_transformers:
            code = i(code)

        return code
