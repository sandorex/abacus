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

import ast, sympy

from ..console import ConsoleExtension, IConsole

class AutoSymbolTransformer(ast.NodeTransformer, ConsoleExtension):
    def __init__(self, console: IConsole):
        ConsoleExtension.__init__(self)

        self.console = console
        self.symbols = []

    def register(self):
        # auto symbol needs to be ran before the impl multiplication
        self.console.ast_transformers.insert(0, self)
        self.console._register_event('post_execute', self.post_execute)

        return super().register()

    def unregister(self):
        self.console.ast_transformers.remove(self)
        self.console._unregister_event('post_execute', self.post_execute)

        super().unregister()

    def post_execute(self):
        """Deletes symbols found while parsing AST"""
        for i in self.symbols:
            self.console.execute(f'del {i}')

        # remove old symbols
        self.symbols = []

    def _is_symbol(self, expr: ast.Expr):
        """Checks if expr is a defined symbol in user namespace, used after
        all undefined names are defined as symbols"""
        if isinstance(expr, ast.Name):
            return isinstance(self.console.user_ns.get(expr.id), sympy.Symbol)

        return False

    # TODO: if i disable attributes then auto symbols does not work inside
    # functions that are inside an attribute but otherwise it will cause weird
    # confusing errors when using attribute of undefined var
    # def visit_Attribute(self, node: ast.Attribute):
    #     return node

    def visit_Constant(self, node: ast.Constant):
        # wrap integers in `sympy.Integer`
        if isinstance(node.value, int):
            return ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id='sympy', ctx=ast.Load()),
                    attr='Integer',
                    ctx=ast.Load()
                ),
                args=[node],
                keywords=[]
            )

        return node

    def visit_Name(self, node: ast.Name):
        # there is no need to modify assignments or deletion
        if not isinstance(node.ctx, ast.Load):
            return node

        # create names as symbols if not already created
        if node.id not in self.console.user_ns \
            and node.id not in self.symbols \
            and node.id not in __builtins__:
            self.symbols.append(node.id)
            self.console.execute(f'{node.id} = sympy.Symbol("{node.id}")')

        return node

    def _has_symbol(self, node: ast.AST) -> bool:
        """Checks if node is a symbol or contains one"""
        if isinstance(node, ast.BinOp):
            return self._has_symbol(node.left) or self._has_symbol(node.right)
        elif isinstance(node, ast.UnaryOp):
            return self._has_symbol(node.operand)
        elif isinstance(node, ast.Compare):
            return self._has_symbol(node.left) or any(self._has_symbol(x) for x in node.comparators)

        return self._is_symbol(node)

    def visit_Compare(self, node: ast.Compare):
        # run on children so symbols are made
        self.generic_visit(node)

        # TODO: make it work for any number of comparisons..
        if len(node.ops) == 1 and (self._has_symbol(node.left) or self._has_symbol(node.comparators[0])):
            if isinstance(node.ops[0], ast.Eq):
                return ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id='sympy', ctx=ast.Load()),
                        attr='Eq',
                        ctx=ast.Load()
                    ),
                    args=[
                        node.left,
                        node.comparators[0],
                    ],
                    keywords=[]
                )
            elif isinstance(node.ops[0], ast.NotEq):
                return ast.Call(
                    func=ast.Attribute(
                        value=ast.Name(id='sympy', ctx=ast.Load()),
                        attr='Ne',
                        ctx=ast.Load()
                    ),
                    args=[
                        node.left,
                        node.comparators[0],
                    ],
                    keywords=[]
                )

        return node
