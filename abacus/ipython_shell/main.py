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

import sys

import IPython

from traitlets.config import Config as IPythonConfig

from .ipython_shell import IPythonShell


def load_ipython_extension(ipy):
    """This function is loaded inside IPython environment"""
    IPythonShell(ipy)


def main_ipython(*, pyinstaller=False):
    """Starting point of IPython version of abacus"""
    cfg = IPythonConfig()
    cfg.TerminalIPythonApp.display_banner = False
    cfg.TerminalIPythonApp.quick = True
    cfg.InteractiveShellApp.pylab_import_all = False
    cfg.TerminalInteractiveShell.term_title_format = IPythonShell.title()

    # load abacus directly so it isn't an extension
    cfg.InteractiveShellApp.exec_lines = [
        f"from {__package__} import load_ipython_extension",
        "load_ipython_extension(get_ipython()); del load_ipython_extension",
    ]

    IPython.start_ipython(sys.argv[1:], config=cfg)


if __name__ == "__main__":
    main_ipython()
