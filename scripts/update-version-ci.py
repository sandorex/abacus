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
"""Script that appends git info to package version"""

import subprocess

FILE = 'abacus/__init__.py'

CMD_GIT_GET_COMMIT = [
    'git', 'rev-parse', '--short=8', 'HEAD'
]

def run(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

version_info = f'+{run(CMD_GIT_GET_COMMIT)}'

contents = ''
with open(FILE, 'r') as file:
    contents = file.readlines()

for i, line in enumerate(contents):
    if line.strip().startswith('__version__'):
        contents[i] = contents[i].strip()[:-1] + version_info + "'\n"
        break

with open(FILE, 'w') as file:
    file.writelines(contents)
