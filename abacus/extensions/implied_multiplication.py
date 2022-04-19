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
from tokenize import TokenInfo
from typing import List
from ..shell import ShellExtension, ShellBase, StringTransformer

def _token_good(tok: TokenInfo):
    if tok.type == token.NUMBER:
        return True
    elif tok.type == token.NAME:
        return not iskeyword(tok.string)

    return False

def _shift_tokens(tokens: List[TokenInfo], index: int, amount: int):
    line = tokens[index].start[0]
    end_index = 0

    for i in range(index, len(tokens)):
        tok = tokens[i]

        if tok.start[0] != line:
            # if the token does not start at the line it shouldn't be touched
            end_index = i - 1
            break

        if tok.end[0] != line:
            end_index = i
            break

    for i in range(index, end_index + 1):
        tok = tokens[i]

        end = tok.end
        if end[0] == line:
            end = (end[0], end[1] + amount)

        tokens[i] = tok._replace(
            start=(tok.start[0], tok.start[1] + amount),
            end=end,
        )

def _insert_token(tokens: List[TokenInfo],
                  index: int,
                  token: TokenInfo,
                  *,
                  padding=True):
    """Inserts token and moved tokens after it so the tokens can be untokenized

    If `token.start` or `token.end` are `None` then they are automatically set
    by taking line from prev token and length is same as `token.string`

    `token.line` is set to same as prev token if it exists

    `padding` if true add space on either side of the token

    TODO: multi line tokens are not supported"""

    prev = None
    if index > 0:
        prev = tokens[index - 1]

    if token.start is None:
        token = token._replace(start=(None, None))

    if token.start[0] is None:
        if prev is not None:
            token = token._replace(start=(prev.end[0], token.start[1]))
        else:
            # NOTE: tokens start at line 1 not 0, except the encoding token
            token = token._replace(start=(1, token.start[1]))

    # set start position
    if token.start[1] is None:
        if prev is not None:
            token = token._replace(start=(token.start[0], prev.end[1]))
        else:
            token = token._replace(start=(token.start[0], 0))

    if token.end is None:
        token = token._replace(end=(None, None))

    # set end line
    if token.end[0] is None:
        token = token._replace(end=(token.start[0], token.end[1]))

    # set end position
    if token.end[1] is None:
        token = token._replace(end=(token.end[0], token.start[1] + len(token.string)))

    if token.line is None:
        if prev is not None:
            token = token._replace(line=prev.line)
        else:
            token = token._replace(line='')

    if token.start[0] != token.end[0]:
        raise Exception('multi line tokens are not supported')

    token_length = token.end[1] - token.start[1]
    if padding:
        token_length += 2

        # so that there is one empty space to the left
        token = token._replace(
            start=(token.start[0], token.start[1] + 1),
            end=(token.end[0], token.end[1] + 2)
        )

    _shift_tokens(tokens, index, token_length)
    tokens.insert(index, token)

def _insert_mul(tokens: List[TokenInfo], index: int):
    _insert_token(tokens, index, TokenInfo(token.OP, '*', None, None, None))

class ImpliedMultiplication(ast.NodeTransformer, StringTransformer, ShellExtension):
    def __init__(self, shell: ShellBase):
        ShellExtension.__init__(self)

        self.shell = shell

    def register(self):
        # needs to run after auto symbol
        self.shell.str_transformers.insert(1, self)
        self.shell.ast_transformers.insert(1, self)

        return super().register()

    def unregister(self):
        self.shell.str_transformers.remove(self)
        self.shell.ast_transformers.remove(self)

        super().unregister()

    def transform_tokens(self, tokens: List[TokenInfo]) -> List[TokenInfo]:
        # i am doing this with recursion, is it the best solution? probably not
        def do(tokens):
            prev = tokens[0]
            for i in range(1, len(tokens)):
                cur = tokens[i]
                if _token_good(cur) \
                    and (_token_good(prev) or prev.exact_type == token.RPAR):
                        _insert_mul(tokens, i)
                        do(tokens)
                        break

                prev = cur

        do(tokens)

        return tokens

    def visit_Call(self, node: ast.Call):
        # turns calls into multiplication if name called is not callable
        try:
            result = None
            try:
                result = self.shell.evaluate(ast.Expression(body=node.func))
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
