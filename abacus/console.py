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

from abc import abstractmethod, ABCMeta
from typing import (
    Dict, TypeVar, Callable, Any, List, Mapping, Union
)
from . import __version__, __version_info__

CodeObj = TypeVar('CodeObj')

class ConsoleExtension:
    def __init__(self):
        self._registered = False

    def register(self):
        self._registered = True

        return self

    def unregister(self):
        self._registered = False

    def register_toggle(self, state: bool=None):
        if state is None:
            self.register_toggle(not self.is_registered())
        elif state == True:
            if not self.is_registered():
                self.register()
        else:
            if self.is_registered():
                self.unregister()

    def is_registered(self) -> bool:
        return self._registered

class StringTransformer(metaclass=ABCMeta):
    @abstractmethod
    def transform(self, line: str) -> str:
        pass

    def transform_lines(self, lines: List[str]) -> List[str]:
        result = []
        for line in lines:
            result.append(self.transform(line))

        return result

    def __call__(self, lines: List[str]) -> List[str]:
        return self.transform_lines(lines)

class IConsole(metaclass=ABCMeta):
    def __init__(self):
        # importing here so there is no circular import
        from abacus.transformations.auto_symbol import AutoSymbolTransformer
        from abacus.transformations.implied_multiplication import ImplMulTransformer

        # NOTE: making instances not registering them!
        self.ext_auto_symbol = AutoSymbolTransformer(self)
        self.ext_impl_multi = ImplMulTransformer(self)

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
    def console_type() -> str:
        """Returns string for which type of console it is"""
        pass

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

    def set_impl_multi(self, state: bool):
        self.ext_impl_multi.register_toggle(state)

    def set_auto_symbol(self, state: bool):
        self.ext_auto_symbol.register_toggle(state)

    @classmethod
    def title(cls) -> str:
        """Window title"""

        return f"""Abacus {__version__} ({cls.console_type()})"""

    @classmethod
    def welcome_message(cls) -> str:
        """Greet message shown on startup of abacus"""

        return f"""\t:: Abacus {__version__} ({cls.console_type()}) ::"""

    def push(self, _locals: Mapping[str, Any]) -> 'IConsole':
        """Set locals in the user namespace"""

        self.user_ns.update(_locals)

        return self

    def init_ns(self, _locals: Mapping[str, Any]={}) -> 'IConsole':
        """Initializes the namespace with default values"""

        self.push({
            **_locals,
            '__version__': __version__,
            '__version_info__': __version_info__,
            '__abacus__': self.console_type(),
            'abacus': self,
        })

        self.execute('import sympy')
        self.execute('sympy.init_printing(use_unicode=True)')

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
