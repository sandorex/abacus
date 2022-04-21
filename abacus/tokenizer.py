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

from tokenize import TokenInfo
from typing import List


def shift_tokens(tokens: List[TokenInfo], index: int, amount: int):
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


def insert_token(
    tokens: List[TokenInfo], index: int, token: TokenInfo, *, padding=True
):
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
        token = token._replace(
            end=(token.end[0], token.start[1] + len(token.string))
        )

    if token.line is None:
        if prev is not None:
            token = token._replace(line=prev.line)
        else:
            token = token._replace(line="")

    if token.start[0] != token.end[0]:
        raise NotImplementedError("multi line tokens are not supported yet")

    token_length = token.end[1] - token.start[1]
    if padding:
        token_length += 2

        # so that there is one empty space to the left
        token = token._replace(
            start=(token.start[0], token.start[1] + 1),
            end=(token.end[0], token.end[1] + 2),
        )

    shift_tokens(tokens, index, token_length)
    tokens.insert(index, token)
