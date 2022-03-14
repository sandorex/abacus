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

import token

from io import BytesIO
from tokenize import TokenInfo, untokenize, tokenize as tokenize_io
from typing import List
from keyword import iskeyword

def tokenize(input: str):
    return list(tokenize_io(BytesIO(input.encode('utf-8')).readline))

def insert_token(tokens: List[TokenInfo], index, token_type, token_str):
    """Inserts token into position at index and returns new changed tokens list

    NOTE: this function can only insert single line tokens, inserting multi line
    tokens WILL break it
    """
    result = tokens[:index]
    token_length = len(token_str)
    replaced_token: TokenInfo = tokens[index]
    token_line = replaced_token.end[0]

    result.append(TokenInfo(
        token_type,
        token_str,
        (replaced_token.start[0], replaced_token.start[1]),
        (replaced_token.start[0], replaced_token.start[1] + token_length - 1),
        line=replaced_token.line
    ))

    i: TokenInfo
    for i in tokens[index:]:
        if i.start[0] != token_line:
            break

        if i.end[0] == token_line:
            end = (i.end[0], i.end[1] + token_length)
        else:
            end = i.end

        result.append(TokenInfo(
            i.type,
            i.string,
            (i.start[0], i.start[1] + token_length),
            end,
            i.line,
        ))

    return result

def transform_inferred_mul(lines: List[str]):
    # filters tokens for those that should have multiplication between them,
    # it rejects keywords
    def token_good(t: TokenInfo):
        if t is None:
            return False

        if t.type == token.NUMBER:
            return True
        elif t.type == token.NAME:
            return not iskeyword(t.string)

        return False

    result: List[str] = []
    for line in lines:
        token_insert_index: List[int] = []
        tokens = tokenize(line)
        prev: TokenInfo = None
        for i, j in enumerate(tokens):
            if token_good(prev) and token_good(j):
                token_insert_index.append(i)

            prev = j

        # insert all new operator tokens
        # NOTE: the number of tokens is incremented each time one is inserted so..
        for count, index in enumerate(token_insert_index):
            tokens = insert_token(tokens, index + count, token.OP, '*')

        result.append(untokenize(tokens).decode('utf-8'))

    return result

def load_ipython_extension(ipy):
    # TODO: print this only the first time somehow? it is annoying and disctracting
#     print(f"""\nWARNING: inferred_multi extension is highly experimental and may break pure python code
# please unload with `%unload_ext {__package__}` if you encounter problems""")

    if transform_inferred_mul not in ipy.input_transformers_post:
        ipy.input_transformers_post.append(transform_inferred_mul)
    else:
        print('inferred_multi extension is already loaded')

def unload_ipython_extension(ipy):
    ipy.input_transformers_post.remove(transform_inferred_mul)
