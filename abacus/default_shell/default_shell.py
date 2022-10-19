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
from math import floor
from code import compile_command
from pygments.lexers.python import PythonLexer
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.application import Application

from ..shell import CodeType, ShellBase

def prompt_continuation(width, line_number, is_soft_wrap):
    return '.' * width

def get_indent_level(input: str) -> int:
    count = 0
    for i in input:
        if not i == ' ':
            break

        count += 1

    return floor(count / 3) # 3 spaces per indent

def is_complete(cls, input: str) -> Tuple[Optional[bool], Optional[Exception]]:
    """Checks if input is complete python code
    TODO
    """
    try:
        return compile_command(input, '<input>', 'exec') is not None
    except (SyntaxError, ValueError, OverflowError) as ex:
        return None, ex

class DefaultShell(ShellBase):
    """TODO"""

    HISTORY_FILE = 'abacus.hist'

    def __init__(self):
        super().__init__()

        self._ns = {}
        self._str_transformers = []
        self._ast_transformers = []
        self._event_callbacks = {}
        self.interpreter = code.InteractiveInterpreter(self.user_ns)

        self.bindings = KeyBindings()
        self.history = FileHistory(self.HISTORY_FILE)
        self.prompt_session = PromptSession(HTML('<green>::</green> '),
            lexer=PygmentsLexer(PythonLexer),
            completer=WordCompleter(self.get_completer_list),
            complete_while_typing=False,
            complete_in_thread=True,
            key_bindings=self.bindings,
            history=self.history,
            prompt_continuation=prompt_continuation,
        )

        # override enter key for "smart" multiline editor like ipython
        @self.bindings.add(Keys.Enter, eager=True)
        def _(event):
            buffer: Buffer = event.current_buffer
            app: Application = event.app

            if not buffer.text.strip():
                return

            # TODO: this is incredibly hacky as the multiline prediction is working
            # using AST trees and abacus has to modify the input, try to clean it up
            input_code_lines = buffer.text.splitlines()
            cobj = compile_command('\n'.join(self.str_transform(input_code_lines)), '<userinput>', 'exec')
            if cobj is None:
                indent_level = get_indent_level(buffer.text.splitlines()[-1])
                buffer.newline(copy_margin=False)
                # copy indent level from last line
                buffer.insert_text(' ' * (3 * indent_level + 3), fire_event=False)
            else:
                if '\n' in buffer.text:
                    # accept only on empty line
                    if buffer.text.splitlines()[-1].strip() == '':
                        buffer.validate_and_handle()
                    else:
                        buffer.newline()
                else:
                    buffer.validate_and_handle()

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
        return "default"

    def get_completer_list(self) -> List[str]:
        return [x for x in self.user_ns.keys() if not x.startswith('_')]

    # NOTE: ShellBase.run can only be used with a string
    def run(self, code: Union[str, ast.Module, ast.Expression, CodeType]):
        """Evaluates the code inside the namespace after ast and string
        transformations and then triggers `post_execute` event

        Do note that not all transformations can be done on all types of input:
            `str`: All transformations are performed
            `ast.Module` or `ast.Expression`: Only AST transformation will be performed
            `CodeType`: No transformation is done"""

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
    ) -> Tuple[CodeType, Optional[CodeType]]:
        """Compiles the node and returns the last statement as `ast.Interactive`
        and if there are more than one statements then rest of the module is
        also returned

        Returns last statement, rest of statements"""

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

    def start_eval_loop(self):
        while True:
            text: str = None
            try:
                text = self.prompt_session.prompt()
                self.run(text)
            except KeyboardInterrupt: # ctrl c
                pass # just ignore it
            except EOFError: # ctrl d
                break # quit
