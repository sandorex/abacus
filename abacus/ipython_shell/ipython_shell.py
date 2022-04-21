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

from typing import Any, Callable, Dict, List
from ..shell import ShellBase
from . import prompt, aliases

# TODO: override ipythonshell class to better get debug stuff and maybe directly
# transform stuff?
class IPythonShell(ShellBase):
    def __init__(self, /, ipy):
        super().__init__()

        self.ipython = ipy

        # TODO: don't show if ran in its own window as its own application?
        print(self.welcome_message())

        # TODO: config stuff

        self.ipython.extension_manager.load_extension(prompt.__name__)
        self.ipython.extension_manager.load_extension(aliases.__name__)

        self.load()

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
    def shell_type() -> str:
        return 'ipython'

    @classmethod
    def title(cls) -> str:
        # add current directory to the title
        return super().title() + ' [{cwd}]'

    def run(self, code: str):
        self.ipython.run_cell(code)
