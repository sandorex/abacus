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


from typing import Any, List
from pygments.lexers.python import PythonLexer
from prompt_toolkit.shortcuts import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.keys import Keys

from .shell import ShellBase

class Shell(ShellBase):
    """Default shell for abacus, based on prompt_toolkit library"""

    HISTORY_FILE = 'abacus.hist'

    def __init__(self):
        super().__init__()

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
            rprompt=self._rprompt,
            multiline=True,
        )

        # toggle for multiline input mode
        self._multiline = False

        @self.bindings.add(Keys.Enter)
        def _(event: KeyPressEvent):
            if self._multiline:
                event.current_buffer.newline()
            else:
                event.app.exit(result=event.current_buffer.text)

        @self.bindings.add(Keys.Escape, eager=True)
        def _(event: KeyPressEvent):
            self._multiline = not self._multiline

        self._load()

    @staticmethod
    def shell_type() -> str:
        return "default"

    def _rprompt(self) -> str:
        if self._multiline:
            return HTML('<green>M</green>')
        else:
            return ''

    def _prompt(self) -> Any:
        # TODO: red prompt on error?
        return HTML('<green>::</green> ')

    @staticmethod
    def _prompt_continuation(width, line_number: int, soft_wrap: bool):
        if not soft_wrap:
            return '.' * width
        else:
            return ''

    def _get_completer_list(self) -> List[str]:
        return [x for x in self.user_ns.keys() if not x.startswith('_')]

    def start_eval_loop(self):
        while True:
            text: str = None
            try:
                text = self.prompt_session.prompt()
                if text.strip():
                    try:
                        self.run(text)
                    except Exception:
                        self.interpreter.showtraceback()
            except KeyboardInterrupt: # ctrl c
                pass # just ignore it
            except EOFError: # ctrl d
                break # quit
