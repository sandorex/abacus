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
#
"""Main for the application"""

import IPython, sys

from .. import __version__
from traitlets.config import Config as IPythonConfig

def main():
    config = IPythonConfig()
    # config.TerminalIPythonApp.display_banner = False # TODO: im disabling it for
                                                     # now as i do not know how
                                                     # im going to handle configs
                                                     # and you couldn't disable
                                                     # it otherwise
    # config.TerminalInteractiveShell.banner1 = f'''Abacus {__version__} running on IPython {IPython.__version__}'''

    config.InteractiveShellApp.extensions = ['abacus']
    # config.Completer.use_jedi = False
    # config.InteractiveShellApp.pylab_import_all = False
    # config.IPCompleter.jedi_compute_type_timeout = 0
    config.TerminalIPythonApp.quick = True
    config.InteractiveShell.debug = True

    IPython.start_ipython(argv=sys.argv[1:], config=config)

def main_gui():
    raise NotImplementedError()
