"""Abacus is an interactive calculator, can be used as an extension in ipython"""
__version__ = '0.1.0-beta'
__version_info__ = (0, 1, 0)

from .extensions.abacus.abacus import load_ipython_extension, unload_ipython_extension
