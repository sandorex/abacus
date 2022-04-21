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

import tokenize

from tokenize import TokenInfo
from ..shell import StringTransformer
from ..tokenizer import shift_tokens, insert_token

def test_tokenize_untokenize():
    """Tests if tokenizing and untokenizing text does not change the result"""
    # TODO: improve this test with more complex code

    INPUT = '''a b c d () {} def 12 12.12 "" '' ? @ + / *'''

    tokens = StringTransformer._tokenize(INPUT)

    untokenized = StringTransformer._untokenize(tokens)

    assert INPUT == untokenized, 'Untokenization does not match original input'

def test_shift_tokens():
    # TODO: is this proper way of testing this?

    INCR = 2
    INDEX = 2

    TOKENS_INPUT = [
        TokenInfo(tokenize.NAME, 'def', (1, 0), (1, 3), 'def x():\n'),
        TokenInfo(tokenize.NAME, 'x', (1, 4), (1, 5), 'def x():\n'),
        TokenInfo(tokenize.OP, '(', (1, 5), (1, 6), 'def x():\n'),
        TokenInfo(tokenize.OP, ')', (1, 6), (1, 7), 'def x():\n'),
        TokenInfo(tokenize.OP, ':', (1, 7), (1, 8), 'def x():\n'),
        TokenInfo(tokenize.NEWLINE, '\n', (1, 8), (1, 9), 'def x():\n'),

        TokenInfo(tokenize.INDENT, '    ', (2, 0), (2, 4), '    pass'),
        TokenInfo(tokenize.NAME, 'pass', (2, 4), (2, 8), '    pass'),
        TokenInfo(tokenize.NEWLINE, '', (2, 8), (2, 9), ''),
        TokenInfo(tokenize.DEDENT, '', (3, 0), (3, 0), ''),
        TokenInfo(tokenize.ENDMARKER, '', (3, 0), (3, 0), ''),
    ]

    TOKENS_OUTPUT = TOKENS_INPUT[:INDEX] + [
        TokenInfo(tokenize.OP, '(', (1, 5 + INCR), (1, 6 + INCR), 'def x():\n'),
        TokenInfo(tokenize.OP, ')', (1, 6 + INCR), (1, 7 + INCR), 'def x():\n'),
        TokenInfo(tokenize.OP, ':', (1, 7 + INCR), (1, 8 + INCR), 'def x():\n'),
        TokenInfo(tokenize.NEWLINE, '\n', (1, 8 + INCR), (1, 9 + INCR), 'def x():\n'),

        TokenInfo(tokenize.INDENT, '    ', (2, 0), (2, 4), '    pass'),
        TokenInfo(tokenize.NAME, 'pass', (2, 4), (2, 8), '    pass'),
        TokenInfo(tokenize.NEWLINE, '', (2, 8), (2, 9), ''),
        TokenInfo(tokenize.DEDENT, '', (3, 0), (3, 0), ''),
        TokenInfo(tokenize.ENDMARKER, '', (3, 0), (3, 0), ''),
    ]

    shift_tokens(TOKENS_INPUT, INDEX, INCR)

    assert TOKENS_INPUT == TOKENS_OUTPUT, 'Tokens arent shifted properly'
