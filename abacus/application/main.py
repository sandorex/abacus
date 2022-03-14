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
#
"""Main for the application"""

import IPython, sys

from .. import __version__
from traitlets.config.loader import Config as IPythonConfig

def main():
    config = IPythonConfig()
    config.TerminalIPythonApp.display_banner = False # TODO: im disabling it for
                                                     # now as i do not know how
                                                     # im going to handle configs
                                                     # and you couldn't disable
                                                     # it otherwise
    # config.TerminalInteractiveShell.banner1 = f'''Abacus {__version__} running on IPython {IPython.__version__}'''

    config.InteractiveShellApp.extensions = ['abacus']

    IPython.start_ipython(argv=sys.argv[1:], config=config)

def main_gui():
    raise NotImplementedError()
