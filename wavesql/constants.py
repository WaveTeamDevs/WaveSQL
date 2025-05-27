# Copyright 2025 eelus1ve and the WaveTeam
#
# GitHub (author): https://github.com/eelus1ve
# GitHub (organization): https://github.com/WaveTeamDevs
# Repository: https://github.com/WaveTeamDevs/WaveSQL
# Website: https://waveteam.net
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path
import os
from colorama import Fore

CUR_PATH: Path = Path(os.path.dirname(os.path.realpath(__file__)))
PATH_DB_INIT_SCRIPTS = CUR_PATH / "sql"
CONFIG_PATH = CUR_PATH / "config.ini"


LOG_COLORS = {
    "GREEN": Fore.GREEN,
    "LIGHTGREEN": Fore.LIGHTGREEN_EX,
    "YELLOW": Fore.YELLOW,
    "LIGHTYELLOW": Fore.LIGHTYELLOW_EX,
    "RED": Fore.RED,
    "LIGHTRED": Fore.LIGHTRED_EX,
    "CYAN": Fore.CYAN,
    "LIGHTCYAN": Fore.LIGHTCYAN_EX,
    "BLUE": Fore.BLUE,
    "LIGHTBLUE": Fore.LIGHTBLUE_EX,
    "MAGENTA": Fore.MAGENTA,
    "LIGHTMAGENTA": Fore.LIGHTMAGENTA_EX,
    "WHITE": Fore.WHITE,
    "LIGHTWHITE": Fore.LIGHTWHITE_EX,
    "BLACK": Fore.BLACK,
    "LIGHTBLACK": Fore.LIGHTBLACK_EX,
}

no_python_names = ["insert_log"]
