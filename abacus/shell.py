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
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    CodeType,
    Dict,
    List,
    Mapping,
    TextIO,
    Union,
)

from . import __version__, __version_info__, ns

if TYPE_CHECKING:
    from pathlib import Path


class StringTransformer(metaclass=ABCMeta):
    @classmethod
    def _tokenize(cls, input: str) -> List[TokenInfo]:
        return list(_generate_tokens(StringIO(input).readline))

    @classmethod
    def _untokenize(cls, tokens: List[TokenInfo]) -> str:
        return _untokenize(tokens)

    def transform(self, lines: List[str]) -> List[str]:
        return lines

    def transform_tokens(self, tokens: List[TokenInfo]) -> List[TokenInfo]:
        return []

    def __call__(self, lines: List[str]) -> List[str]:
        lines = self.transform(lines)

        tokens = self._tokenize("".join(lines))
        tokens = self.transform_tokens(tokens)

        if not tokens:
            return lines
        else:
            # NOTE: the NL characters are required and it wont run properly
            # without them
            return self._untokenize(tokens).splitlines(keepends=True)


# TODO: config
class ShellBase(metaclass=ABCMeta):
    EVENT_POST_EXECUTE = "post_execute"

    def __init__(self):
        self.transformer = None

    @property
    @abstractmethod
    def user_ns(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def event_callbacks(self) -> Dict[str, List[Callable]]:
        pass

    @property
    @abstractmethod
    def ast_transformers(self) -> List[ast.NodeTransformer]:
        pass

    @property
    @abstractmethod
    def str_transformers(self) -> List[Callable]:
        pass

    @staticmethod
    @abstractmethod
    def shell_type() -> str:
        """Returns string for which type of shell it is"""
        pass

    @classmethod
    def title(cls) -> str:
        """Window title"""

        return f"""Abacus {__version__} ({cls.shell_type()})"""

    @classmethod
    def welcome_message(cls) -> str:
        """Greet message shown on startup of abacus"""

        return f"""\t:: Abacus {__version__} ({cls.shell_type()}) ::"""

    @abstractmethod
    def run(self, code: str):
        """Evaluates the code inside the namespace after all transformations

        Triggers `self.EVENT_POST_EXECUTE`"""
        pass

    def run_file(self, file: Union[str, "Path", TextIO]):
        """Runs whole file using `self.run`"""

        # TODO: file should be TextIO but isinstance fails
        if not isinstance(file, TextIOBase):
            file = open(file, "r")

        with file:
            self.run(file.read())

    def run_package_file(self, file: str, package: str):
        """Run file from package `package`"""
        fp = importlib.resources.open_text(package, file)
        self.run_file(fp)

    # TODO: bring back debug enable

    def load(self, _locals: Dict[str, Any] = {}) -> "ShellBase":
        """Sets things up like namespace, transformer and config and stuff"""

        self.push(
            {
                **_locals,
                "__version__": __version__,
                "__version_info__": __version_info__,
                "__abacus__": self.shell_type(),
                "abacus": self,
            }
        )

        # NOTE: importing sympy using execute cause transformer needs it and
        # execute does not do any transformation
        self.execute("import sympy")

        from .transformer import AbacusTransformer

        self.transformer = AbacusTransformer(self)

        self.run_package_file("init.pyi", ns.__package__)

        # TODO: run the real init file somewhere on the system

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

    def trigger_event(self, event, *args, **kwargs):
        for fn in self.event_callbacks.get(event, []):
            fn(*args, **kwargs)
