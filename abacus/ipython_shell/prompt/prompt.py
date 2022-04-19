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

from IPython.terminal.prompts import Prompts, Token

class BasicPrompt(Prompts):
    def in_prompt_tokens(self, cli=None):
        return [(Token.Prompt, ':: ')]

    def out_prompt_tokens(self):
       return []

    def continuation_prompt_tokens(self, cli=None, width=None):
        # NOTE: two dots cause its the same length as the in token, it keeps the
        # indentation same between the first line and the rest
        return [(Token.PromptNum, '.. ')]

def load_ipython_extension(ipy):
    prompt = BasicPrompt(ipy)
    prompt.old = ipy.prompts
    ipy.prompts = prompt

def unload_ipython_extension(ipy):
    if hasattr(ipy.prompts, 'old'):
        ipy.prompts = ipy.prompts.old
    else:
        print('Unable to unload prompt for some reason, maybe it was not loaded?')
