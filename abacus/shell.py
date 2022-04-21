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

import ast, importlib.resources

from abc import abstractmethod, ABCMeta
from io import StringIO
from tokenize import (
    TokenInfo,
    untokenize as _untokenize,
    generate_tokens as _generate_tokens
)
from . import ns, __version__, __version_info__
from typing import (
    TYPE_CHECKING, Dict, Optional, TypeVar, Callable, Any, List, Mapping, Union
)

if TYPE_CHECKING:
    from pathlib import Path

CodeObj = TypeVar('CodeObj')

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

        tokens = self._tokenize(''.join(lines))
        tokens = self.transform_tokens(tokens)

        if not tokens:
            return lines
        else:
            # NOTE: the NL characters are required and it wont run properly
            # without them
            return self._untokenize(tokens).splitlines(keepends=True)

# TODO: config
# TODO: add str and ast transformers to a list in base and then one function
# in the python shell runs over all them
class ShellBase(metaclass=ABCMeta):
    EVENT_POST_EXECUTE = 'post_execute'

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

    # TODO: make this str only but BasicShell can support multiple input types
    # do i even need this to be common between all shells?
    @abstractmethod
    def run(self, code: Union[str, ast.Module, ast.Expression, CodeObj]):
        """Evaluates the code inside the namespace after ast and string
        transformations and then triggers `post_execute` event

        Do note that not all transformations can be done on all types of input:
            `str`: All transformations are performed
            `ast.Module` or `ast.Expression`: Only AST transformation will be performed
            `CodeObj`: No transformation is done"""
        pass

    def run_file(self, file: Union[str, 'Path'], *, package=None):
        """Runs whole file interactively

        `file` is either `str` or `pathlib.Path`
        `package` look for the file inside python package `package`"""

        if package is not None:
            fp = importlib.resources.open_text(package, str(file))
        else:
            fp = open(file, 'r')

        with fp:
            self.run(fp.read())

    # TODO: bring back debug enable

    def load(self, _locals: Dict[str, Any]={}) -> 'ShellBase':
        """Sets things up like namespace, transformer and config and stuff"""

        self.push({
            **_locals,
            '__version__': __version__,
            '__version_info__': __version_info__,
            '__abacus__': self.shell_type(),
            'abacus': self,
        })

        # NOTE: importing sympy using execute cause transformer needs it and
        # execute does not do any transformation
        self.execute('import sympy')

        from .transformer import AbacusTransformer
        self.transformer = AbacusTransformer(self)

        self.run_file('init.pyi', package=ns.__package__)

        # TODO: run the real init file somewhere on the system

        return self

    def push(self, _locals: Mapping[str, Any]) -> 'ShellBase':
        """Set locals in the user namespace"""

        self.user_ns.update(_locals)

        return self

    def execute(self,
                code: Union[str, ast.Module, CodeObj],
                *,
                filename='<input>'):
        """Executes the code inside the namespace verbatim

        No events are triggered"""

        if isinstance(code, ast.Module):
            code = compile(code, filename=filename, mode='exec')

        exec(code, self.user_ns)

    def evaluate(self,
                 code: Union[str, ast.Module, ast.Expression, CodeObj],
                 *,
                 filename='<input>') -> Any:
        """Evaluates the code inside namespace verbatim and returns result of
        the last statement

        `filename` is passed to compile and will be in tracebacks when an
        exception occurs

        No events are triggered"""

        if isinstance(code, ast.Module):
            # remove last statement
            last_stmt = code.body.pop()

            # execute the rest
            self.execute(code, filename=filename)

            # compile the last statement
            code = compile(last_stmt, filename=filename, mode='eval')
        elif isinstance(code, ast.Expression):
            code = compile(code, filename=filename, mode='eval')

        return eval(code, self.user_ns)

    def register_event(self, event: str, handler):
        self.event_callbacks.setdefault(event, []).append(handler)

    def unregister_event(self, event: str, handler):
        self.event_callbacks.setdefault(event, []).remove(handler)

    def trigger_event(self, event, *args, **kwargs) -> Optional[Any]:
        if fn := self.event_callbacks.get(event, None) is not None:
            return fn(*args, **kwargs)

        return None

    # # TODO: this does not need to be in the ShellBase
    # def ast_transform(self, node: ast.AST) -> ast.AST:
    #     """Performs AST transformation on the node

    #     WARNING: the input `node` may be modified in the process"""

    #     i: ast.NodeTransformer
    #     for i in self.ast_transformers:
    #         i.visit(node)

    #     return node

    # def str_transform(self, code: List[str]) -> List[str]:
    #     """Performs string transformation on the code

    #     WARNING: the input `code` may be modified in the process"""

    #     i: Callable[[str], str]
    #     for i in self.str_transformers:
    #         code = i(code)

    #     return code
