"""Module that lazily loads sympy"""

from importlib import import_module
from typing import Any

sympy: Any = None

def __deferred_load():
    global sympy

    if sympy is None:
        sympy = import_module('sympy')

def __getattr__(name) -> Any:
    __deferred_load()

    return getattr(sympy, name)

def __dir__() -> Any:
    __deferred_load()

    return sympy.__dir__()
