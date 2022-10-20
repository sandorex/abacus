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
import importlib.resources

from abc import ABCMeta, abstractmethod
from io import StringIO, TextIOBase
from tokenize import TokenInfo
from tokenize import generate_tokens as _generate_tokens
from tokenize import untokenize as _untokenize
from types import CodeType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    TextIO,
    Tuple,
    Union,
)

from . import __version__, __version_info__, ns

if TYPE_CHECKING:
    from pathlib import Path

# TODO: config
class ShellBase(metaclass=ABCMeta):
    EVENT_POST_EXECUTE = "post_execute"

    FILENAME='<input>'

    def __init__(self):
        self.str_transformers: List[Callable[[str], str]] = []
        self.ast_transformers: List[Callable[[str], str]] = []
        self.event_callbacks: Mapping[str, List[Callable[['ShellBase', Any]]]]
        self.user_ns: Mapping[str, Any] = {
            "__version__": __version__,
            "__version_info__": __version_info__,
            "__abacus__": self.shell_type(),
            "abacus": self,
        }

        # add the transformer
        from .transformer import AbacusTransformer
        AbacusTransformer(self)

        self.run_package_file("init.pyi", ns.__package__)

    @staticmethod
    @abstractmethod
    def shell_type() -> str:
        """Returns string for which type of shell it is"""
        pass

    @abstractmethod
    def start_eval_loop():
        pass

    def title(cls) -> str:
        """Window title"""

        return f"""Abacus {__version__} ({cls.shell_type()})"""

    def greeting(cls) -> str:
        """Greet message that should be shown on startup of abacus"""

        return f"""\t:: Abacus {__version__} ({cls.shell_type()}) ::"""

    def _transform(self, code: str) -> str:
        """Performs string transformation on the code"""

        i: Callable[[str], str]
        for i in self.str_transformers:
            code = i(code)

        return code

    def _ast_transform(self, node: ast.AST):
        """Performs AST transformations on the node"""

        i: ast.NodeTransformer
        for i in self.ast_transformers:
            i.visit(node)

    def _parse_ast(self, code: str, filename=FILENAME) -> ast.Module:
        return ast.parse(code, filename=filename, mode="exec")

    def _compile_interactive(self, node: ast.Module, filename=FILENAME) -> Tuple[CodeType, Optional[CodeType]]:
        """Compiles the node and returns the last statement as `ast.Interactive`
        and if there are more than one statements then rest of the module is
        also returned

        Returns last statement, rest of statements"""

        stmt = node.body.pop(-1)
        ast.fix_missing_locations(stmt)
        stmt = compile(
            ast.Interactive(body=[stmt]), filename=filename, mode="single"
        )

        module = None
        if len(node.body) >= 1:
            module = compile(node, filename=filename, mode="exec")

        return stmt, module

    def run(self, code: Union[str, ast.Module]):
        """Evaluates the code inside the namespace after all transformations

        Triggers `self.EVENT_POST_EXECUTE`"""

        if isinstance(code, str):
            code = self._transform(code)
            code = self._parse_ast(code)

        self._ast_transform(code)

        (stmt, module) = self._compile_interactive(code)

        if module is not None:
            self.interpreter.runcode(module)

        # # TODO: experiment with manually printing instead of single eval, that
        # # way i can control how everything is printed and for example single
        # # value inside an array can be extracted
        self.interpreter.runcode(stmt)

        self._trigger_event(self.EVENT_POST_EXECUTE)

    def run_file(self, file: Union[str, 'Path', TextIO]):
        """Runs whole file using `self.run`"""

        if not isinstance(file, TextIOBase):
            file = open(file, "r")

        with file:
            self.run(file.read())

    def run_in_package_file(self, file: str, package: str):
        """Run file from package `package`"""
        fp = importlib.resources.open_text(package, file)
        self.run_file(fp)

    # TODO: bring back debug enable

    def _load(self) -> "ShellBase":
        """Loads user config files, should be called by the shell after initalization"""

        # TODO: run the user init file somewhere on the system

        return self

    def push(self, _locals: Mapping[str, Any]) -> "ShellBase":
        """Set locals in the user namespace"""

        self.user_ns.update(_locals)

        return self

    def execute(
        self, code: Union[str, ast.Module, CodeType], *, filename="<input>"
    ):
        """Executes the code inside the namespace verbatim

        No events are triggered"""

        # NOTE: exec can handle both `CodeType` and `str` but not `ast.AST`
        if isinstance(code, ast.Module):
            code = compile(code, filename=filename, mode="exec")

        exec(code, self.user_ns)

    def evaluate(
        self,
        code: Union[str, ast.Module, ast.Expression, CodeType],
        *,
        filename="<input>",
    ) -> Any:
        """Evaluates the code inside namespace verbatim and returns result of
        the last statement

        `filename` is passed to compile and will be in tracebacks when an
        exception occurs

        No events are triggered"""

        if isinstance(code, ast.Module):
            # remove last statement
            last_stmt = code.body.pop()
            ast.fix_missing_locations(code)

            # execute the rest
            self.execute(code, filename=filename)

            # compile the last statement
            code = compile(last_stmt, filename=filename, mode="eval")
        elif isinstance(code, ast.Expression):
            code = compile(code, filename=filename, mode="eval")

        return eval(code, self.user_ns)

    def register_event(self, event: str, handler):
        self.event_callbacks.setdefault(event, []).append(handler)

    def unregister_event(self, event: str, handler):
        self.event_callbacks.setdefault(event, []).remove(handler)

    def _trigger_event(self, event, *args, **kwargs):
        for fn in self.event_callbacks.get(event, []):
            fn(self, *args, **kwargs)
