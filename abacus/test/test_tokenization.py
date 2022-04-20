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
from ..extensions.implied_multiplication import _shift_tokens, _insert_token, _insert_mul

def test_tokenize_untokenize():
    """Tests if tokenizing and untokenizing text does not change the result"""
    # TODO: improve this test with more complex code

    INPUT = '''a b c d () {} def 12 12.12 "" '' ? @ + / *'''

    tokens = StringTransformer._tokenize(INPUT)

    untokenized = StringTransformer._untokenize(tokens)

    assert INPUT == untokenized, 'Untokenization does not match original input'

