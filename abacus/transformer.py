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

import ast
import token
import traceback

from keyword import iskeyword
from tokenize import TokenInfo
from typing import List

import sympy

from .shell import ShellBase, StringTransformer
from .tokenizer import insert_token


def _token_good(tok: TokenInfo):
    if tok.type == token.NUMBER:
        return True
    elif tok.type == token.NAME:
        return not iskeyword(tok.string)

    return False


def _insert_mul(tokens: List[TokenInfo], index: int):
    insert_token(tokens, index, TokenInfo(token.OP, "*", None, None, None))


class AbacusTransformer(ast.NodeTransformer, StringTransformer):
    def __init__(self, shell: ShellBase):
        self.shell = shell
        self.symbols = []

        self.shell.str_transformers.append(self)
        self.shell.ast_transformers.append(self)
        self.shell.register_event(
            ShellBase.EVENT_POST_EXECUTE, self.post_execute
        )

    # impl multi #

    def transform_tokens(self, tokens: List[TokenInfo]) -> List[TokenInfo]:
        # i am doing this with recursion, is it the best solution? probably not
        def do(tokens):
            prev = tokens[0]
            for i in range(1, len(tokens)):
                cur = tokens[i]
                if (
                    _token_good(cur)
                    and (_token_good(prev) or prev.exact_type == token.RPAR)
                ) or (
                    prev.exact_type == token.RPAR
                    and cur.exact_type == token.LPAR
                ):
                    _insert_mul(tokens, i)
                    do(tokens)
                    break

                prev = cur

        do(tokens)

        return tokens

    def visit_Call(self, node: ast.Call):
        # run on children so that symbols are made
        self.generic_visit(node)

        # turns calls into multiplication if name called is not callable
        try:
            result = None
            try:
                result = self.shell.evaluate(ast.Expression(body=node.func))
            except NameError:
                # it does not exist
                pass
            except Exception as ex:
                # something else is wrong so just let it be
                return node

            # skip if it's callable, empty function call or with just keywords
            if callable(result) or len(node.args) == 0:
                return node

            # treat multi argument calls of non callable name as a tuple
            # NOTE: keywords are ignored
            if len(node.args) > 1:
                right = ast.Tuple(elts=node.args, ctx=ast.Load())
            else:
                right = node.args[0]

            return ast.BinOp(left=node.func, op=ast.Mult(), right=right)
        except Exception:
            print(
                "AbacusTransformer: Error while parsing AST:\n",
                traceback.format_exc(),
            )
            return node

    # auto symbol #

    def post_execute(self):
        """Deletes symbols created during parsing"""
        for i in self.symbols:
            # TODO: FIXME: execute AST not raw code!
            self.shell.execute(f"del {i}")

        # remove old symbols
        self.symbols = []

    def _is_symbol(self, expr: ast.Expr):
        """Checks if expr is a defined symbol in user namespace, used after
        all undefined names are defined as symbols"""
        if isinstance(expr, ast.Name):
            return isinstance(self.shell.user_ns.get(expr.id), sympy.Symbol)

        return False

    def _has_symbol(self, node: ast.AST) -> bool:
        """Checks if node is a symbol or contains one"""
        if isinstance(node, ast.BinOp):
            return self._has_symbol(node.left) or self._has_symbol(node.right)
        elif isinstance(node, ast.UnaryOp):
            return self._has_symbol(node.operand)
        elif isinstance(node, ast.Compare):
            return self._has_symbol(node.left) or any(
                self._has_symbol(x) for x in node.comparators
            )

        return self._is_symbol(node)

    def visit_Constant(self, node: ast.Constant):
        # wrap integers in `sympy.Integer`, imitates sympy's auto integer

        # run on children so symbols are made
        self.generic_visit(node)

        # NOTE: for some reason bool is also an int?
        if isinstance(node.value, int) and not isinstance(node.value, bool):
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="sympy", ctx=ast.Load()),
                    attr="Integer",
                    ctx=ast.Load(),
                ),
                args=[node],
                keywords=[],
            )

        return node

    def visit_Name(self, node: ast.Name):
        # there is no need to modify assignments or deletion
        if not isinstance(node.ctx, ast.Load):
            return node

        # create names as symbols if not already created
        if (
            node.id not in self.shell.user_ns
            and node.id not in self.symbols
            and node.id not in __builtins__
        ):
            self.symbols.append(node.id)

            # TODO: FIXME: execute AST not raw code!
            self.shell.execute(f'{node.id} = sympy.Symbol("{node.id}")')

        return node

    def visit_Compare(self, node: ast.Compare):
        # run on children so symbols are made
        self.generic_visit(node)

        # TODO: make it work for any number of comparisons..
        if len(node.ops) == 1 and (
            self._has_symbol(node.left) or self._has_symbol(node.comparators[0])
        ):
            if isinstance(node.ops[0], ast.Eq):
                return ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="sympy", ctx=ast.Load()),
                        attr="Eq",
                        ctx=ast.Load(),
                    ),
                    args=[
                        node.left,
                        node.comparators[0],
                    ],
                    keywords=[],
                )
            elif isinstance(node.ops[0], ast.NotEq):
                return ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id="sympy", ctx=ast.Load()),
                        attr="Ne",
                        ctx=ast.Load(),
                    ),
                    args=[
                        node.left,
                        node.comparators[0],
                    ],
                    keywords=[],
                )

        return node
