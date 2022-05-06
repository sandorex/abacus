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
# this file sets all the defaults for abacus
# type: ignore

sympy.init_printing(use_unicode=False)

from sympy import solve

# SI prefixes
yocto = 10 ** -24
zepto = 10 ** -21
atto  = 10 ** -18
femto = 10 ** -15
pico  = 10 ** -12
nano  = 10 ** -9
micro = 10 ** -6
milli = 10 ** -3
centi = 10 ** -2
deci  = 10 ** -1

deka  = 10 ** 1
hecto = 10 ** 2
kilo  = 10 ** 3
mega  = 10 ** 6
giga  = 10 ** 9
tera  = 10 ** 12
peta  = 10 ** 15
exa   = 10 ** 18
zetta = 10 ** 21
yotta = 10 ** 24

# easter eggs :)
this = cool
