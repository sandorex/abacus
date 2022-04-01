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

import IPython, sys, ast

from traitlets.config import Config as IPythonConfig
from typing import Any, Callable, Dict, List, Union
from ..console import CodeObj, IConsole
from . import prompt, aliases

class IPythonConsole(IConsole):
    def __init__(self, /, ipy):
        super().__init__()

        self.ipython = ipy

        print(self.welcome_message())

        # TODO: config stuff

        self.set_auto_symbol(True)
        self.set_impl_multi(True)

        self.ipython.extension_manager.load_extension(prompt.__name__)
        self.ipython.extension_manager.load_extension(aliases.__name__)

        self.init_ns()

    @property
    def user_ns(self) -> Dict[str, Any]:
        return self.ipython.user_ns

    @property
    def event_callbacks(self) -> Dict[str, List[Callable]]:
        return self.ipython.events.callbacks

    @property
    def ast_transformers(self) -> List[ast.NodeTransformer]:
        return self.ipython.ast_transformers

    @property
    def str_transformers(self) -> List[Callable]:
        return self.ipython.input_transformers_post

    @staticmethod
    def console_type() -> str:
        return 'ipython'

    # TODO:
    def run_interactive(self, code: Union[str, List[ast.AST], CodeObj]) -> Any:
        if isinstance(code, str):
            self.ipython.run_cell(code)
        else:
            raise NotImplementedError()

    def ast_transform(self, node: ast.AST) -> ast.AST:
        return self.ipython.transform_ast(node)

    def str_transform(self, code: str) -> str:
        return self.ipython.transform_cell(code)

def load_ipython_extension(ipy):
    IPythonConsole(ipy)

def main_ipython():
    """Starting point of IPython version of abacus"""
    cfg = IPythonConfig()
    cfg.TerminalIPythonApp.display_banner = False
    cfg.TerminalIPythonApp.quick = True
    cfg.InteractiveShellApp.pylab_import_all = False

    # load abacus directly so it isn't an extension
    cfg.InteractiveShellApp.exec_lines = [
        'from abacus.ipython import load_ipython_extension',
        'load_ipython_extension(get_ipython())',
        'del load_ipython_extension'
    ]

    IPython.start_ipython(sys.argv[1:], config=cfg)

if __name__ == '__main__':
    main_ipython()
