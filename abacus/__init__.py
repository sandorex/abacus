"""Abacus is an interactive calculator using IPython"""
__version__ = '0.1.0'
__version_info__ = (0, 1, 0)

from .extensions.abacus.abacus import load_ipython_extension, unload_ipython_extension
from .application.main import main, main_gui
