#!/usr/bin/env python3
# abacus
#
# Copyright 2022 Aleksandar Radivojevic
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from IPython.terminal.prompts import Prompts, Token

class BasicPrompt(Prompts):
    def in_prompt_tokens(self, cli=None):
        return [(Token.Prompt, ':: ')]

    def out_prompt_tokens(self):
       return [(Token.ZeroWidthEscape, '')]

    def continuation_prompt_tokens(self, cli=None, width=None):
        return [(Token.PromptNum, '... ')]

def load_ipython_extension(ipy):
    prompt = BasicPrompt(ipy)
    prompt.old = ipy.prompts
    ipy.prompts = prompt

def unload_ipython_extension(ipy):
    if hasattr(ipy.prompts, 'old'):
        ipy.prompts = ipy.prompts.old
    else:
        print('Unable to unload prompt for some reason, maybe it was not loaded?')
