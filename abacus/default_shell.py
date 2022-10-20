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

import code

from typing import Any, List, Optional, Tuple
from math import floor
from code import compile_command
from pygments.lexers.python import PythonLexer
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.buffer import Buffer

from .shell import ShellBase

class Shell(ShellBase):
    """TODO"""

    HISTORY_FILE = 'abacus.hist'

    def __init__(self):
        super().__init__()

        self.interpreter = code.InteractiveInterpreter(self.user_ns)
        self.bindings = KeyBindings()
        self.history = FileHistory(self.HISTORY_FILE)
        self.prompt_session = PromptSession(self._prompt,
            lexer=PygmentsLexer(PythonLexer),
            completer=WordCompleter(self._get_completer_list),
            complete_while_typing=False,
            complete_in_thread=True,
            key_bindings=self.bindings,
            history=self.history,
            prompt_continuation=self._prompt_continuation,
        )

        # override enter key for "smart" multiline editor like ipython
        @self.bindings.add(Keys.Enter, eager=True)
        def _(event):
            buffer: Buffer = event.current_buffer

            if not buffer.text.strip():
                return

            # TODO: clean this up and make it a method in shellbase
            input_code_lines = buffer.text.splitlines()
            cobj = compile_command('\n'.join(self.str_transform(input_code_lines)), '<input>', 'exec')
            if cobj is None:
                indent_level = self._get_indent_level(buffer.text.splitlines()[-1])
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

        self._load()

    @staticmethod
    def shell_type() -> str:
        return "default"

    def _prompt(self) -> Any:
        # TODO: red prompt on error?
        return HTML('<green>::</green> ')

    @staticmethod
    def _prompt_continuation(width, line_number: int, soft_wrap: bool):
        if not soft_wrap:
            return '.' * width
        else:
            return ''

    @staticmethod
    def _get_indent_level(input: str, indent=3) -> int:
        count = 0
        for i in input:
            if not i == ' ':
                break

            count += 1

        return floor(count / indent)

    # @staticmethod
    # def _is_input_complete(input: str) -> Tuple[Optional[bool], Optional[Exception]]:
    #     """Checks if input is complete python code
    #     TODO
    #     """
    #     try:
    #         return compile_command(input, '<input>', 'exec') is not None
    #     except (SyntaxError, ValueError, OverflowError) as ex:
    #         return None, ex

    def _get_completer_list(self) -> List[str]:
        return [x for x in self.user_ns.keys() if not x.startswith('_')]

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
