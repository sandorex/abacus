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

import ast, token, traceback

from keyword import iskeyword
from tokenize import (
    TokenInfo,
    untokenize as _untokenize,
    generate_tokens as _generate_tokens
)
from io import StringIO
from typing import List
from ..console import ConsoleExtension, IConsole, StringTransformer

class ImplMulTransformer(ast.NodeTransformer, StringTransformer, ConsoleExtension):
    def __init__(self, console: IConsole):
        ConsoleExtension.__init__(self)

        self.console = console

    def register(self):
        # needs to run after auto symbol
        self.console.str_transformers.insert(1, self) # TODO: what happens if there is no transformers?
        self.console.ast_transformers.insert(1, self)

        return super().register()

    def unregister(self):
        self.console.str_transformers.remove(self)
        self.console.ast_transformers.remove(self)

        super().unregister()

    @staticmethod
    def _tokenize(input: str) -> List[TokenInfo]:
        return list(_generate_tokens(StringIO(input).readline))

    @staticmethod
    def _token_good(tok: TokenInfo):
        if tok.type == token.NUMBER:
            return True
        elif tok.type == token.NAME:
            return not iskeyword(tok.string)

        return False

    def transform(self, line: str) -> str:
        tokens = self._tokenize(line)

        count = 0 # number of added tokens
        prev = tokens[0]
        for i, cur in enumerate(list(tokens[1:]), 1):
            if self._token_good(cur):
                if self._token_good(prev) or prev.exact_type == token.RPAR:
                    # TODO: it works but includes whitespace which makes the
                    # output weird sometimes
                    tokens.insert(i + count, (token.OP, ' * '))
                    count += 1

            prev = cur

        return _untokenize(tokens)

    def visit_Call(self, node: ast.Call):
        # turns calls into multiplication if name called is not callable
        try:
            result = None
            try:
                result = self.console.evaluate(ast.Expression(body=node.func))
            except NameError:
                # it does not exist
                pass
            except Exception as ex:
                return node

            # if it's callable then do nothing
            if (
                    # skip functions
                    callable(result) \

                    # there is nothing in the function, or just keywords so skip it
                    or len(node.args) == 0
                ):
                return node

            # if there are multiple 'arguments' in the function call then treat
            # it as a tuple
            # NOTE: keywords are ignored
            if len(node.args) > 1:
                right = ast.Tuple(
                    elts=node.args,
                    ctx=ast.Load()
                )
            else:
                right = node.args[0]

            return ast.BinOp(
                left=node.func,
                op=ast.Mult(),
                right=right
            )
        except Exception:
            print('ImplMulTransformer: Error while parsing AST:\n', traceback.format_exc())
            return node
