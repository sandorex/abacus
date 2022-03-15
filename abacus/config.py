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

from email.policy import default
from . import extensions

default_config = {
    # should sympy session be started automatically
    'start_session': True,

    # refer to `sympy.init_session` for details # TODO: ignored currently
    'auto_symbols': True,
    'auto_integers': True,

    # extensions that come enabled by default
    'extensions': {
        extensions.inferred_multi.__name__,
    },

    # default extensions that load only in interactive sessions
    'interactive_ext': {
        extensions.aliases.__name__,
        extensions.basic_prompt.__name__,
    }
}

def get_config(ipy):
    return { **default_config, **ipy.config.get('abacus', {}) }
