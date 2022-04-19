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
from typing import  Dict, TypeVar, Callable, Any, List, Mapping, Union
from . import ns, __version__, __version_info__

CodeObj = TypeVar('CodeObj')

class ShellExtension:
    def __init__(self):
        self._registered = False

    def register(self):
        self._registered = True

        return self

    def unregister(self):
        self._registered = False

    def register_set(self, state: bool=None):
        if state is None:
            self.register_set(not self.is_registered())
        elif state == True:
            if not self.is_registered():
                self.register()
        else:
            if self.is_registered():
                self.unregister()

    def is_registered(self) -> bool:
        return self._registered

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

class ShellBase(metaclass=ABCMeta):
    def __init__(self):
        # importing here so there is no circular import
        from .extensions.auto_symbol import AutoSymbol
        from .extensions.implied_multiplication import ImpliedMultiplication
        from .extensions.debug import Debugger

        # NOTE: making instances not registering them!
        self.ext_auto_symbol = AutoSymbol(self)
        self.ext_impl_multi = ImpliedMultiplication(self)
        self.ext_debug = Debugger(self)

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

    def run_file(self, file: Union[str, Any], *, package=None):
        """Runs whole file interactively

        `package` look for the file inside python package `package`"""

        if package is not None:
            fp = importlib.resources.open_text(package, str(file))
        else:
            fp = open(file, 'r')


        with fp:
            self.run_interactive(fp.read())

    @abstractmethod
    def run_interactive(self,
                        code: Union[str, List[ast.AST], CodeObj],
                        transform=True,
                        imitate_user_input=False):
        """Evaluates the code inside the namespace after ast and string
        transformations and then triggers `post_execute` event

        `transform`: Should input be transformed, do note that not all
        transformations can be done on all types of input:
            `str`: All transformations are performed
            `ast.AST`: Only AST transformation will be performed
            `CodeObj`: No transformation is done"""
        pass

    def set_debug(self, state: bool):
        self.ext_debug.register_set(state)

    def set_impl_multi(self, state: bool):
        self.ext_impl_multi.register_set(state)

    def set_auto_symbol(self, state: bool):
        self.ext_auto_symbol.register_set(state)

    @classmethod
    def title(cls) -> str:
        """Window title"""

        return f"""Abacus {__version__} ({cls.shell_type()})"""

    @classmethod
    def welcome_message(cls) -> str:
        """Greet message shown on startup of abacus"""

        return f"""\t:: Abacus {__version__} ({cls.shell_type()}) ::"""

    def push(self, _locals: Mapping[str, Any]) -> 'ShellBase':
        """Set locals in the user namespace"""

        self.user_ns.update(_locals)

        return self

    def init_ns(self, _locals: Mapping[str, Any]={}) -> 'ShellBase':
        """Initializes the namespace with default values"""

        self.push({
            **_locals,
            '__version__': __version__,
            '__version_info__': __version_info__,
            '__abacus__': self.shell_type(),
            'abacus': self,
        })

        # NOTE: importing sympy using execute cause transformers need it and
        # execute does not do any transformation
        self.execute('import sympy')

        self.set_auto_symbol(True)
        self.set_impl_multi(True)

        # run the init file and let it take care of everything
        self.run_file('init.pyi', package=ns.__package__)

        return self

    def execute(self, code: Union[str, List[ast.AST], CodeObj]):
        """Executes the code inside the namespace verbatim"""

        if isinstance(code, ast.AST):
            code = compile(code, filename='<input>', mode='exec')

        exec(code, self.user_ns)

    def evaluate(self, code: Union[str, ast.AST, CodeObj]) -> Any:
        """Evaluates the code inside namespace verbatim and returns result of
        the last statement

        Does not print anything"""

        if isinstance(code, ast.AST):
            code = compile(code, filename='<input>', mode='eval')

        return eval(code, self.user_ns)

    def _register_event(self, event: str, handler):
        self.event_callbacks.setdefault(event, []).append(handler)

    def _unregister_event(self, event: str, handler):
        self.event_callbacks.setdefault(event, []).remove(handler)

    def ast_transform(self, node: ast.AST) -> ast.AST:
        """Performs AST transformation on the node

        WARNING: the input `node` may be modified in the process"""

        i: ast.NodeTransformer
        for i in self.ast_transformers:
            i.visit(node)

        return node

    def str_transform(self, code: Union[str, List[str]]) -> Union[str, List[str]]:
        """Performs string transformation on the code"""

        got_str = False

        if isinstance(code, str):
            code = [code]
            got_str = True

        result = code

        i: Callable[[str], str]
        for i in self.str_transformers:
            result = i(result)

        if got_str:
            return result[0]

        return result
