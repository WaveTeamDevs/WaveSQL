# This file was automatically generated by WaveSQL.
# You are free to modify this file as needed.
#
# Copyright 2025 eelus1ve and the WaveTeam
# GitHub: https://github.com/eelus1ve
# Repo: https://github.com/WaveTeamDevs/WaveSQL
# License: Apache-2.0 (see https://www.apache.org/licenses/LICENSE-2.0)

from wavesql.sync import WaveSQL
from typing import Literal
from datetime import datetime
from pathlib import Path


class DataBase(WaveSQL):
    def __init__(
        self, config: dict | str | None = None, path_to_sql: Path | str | None = None, is_dictionary: bool = False,
        is_console_log: bool = False, is_log_backtrace: bool = False, raise_log_on_fail: bool = False,
        is_pprint: bool = False, is_protected: bool = True, is_auto_start: bool = False, is_try_update_db: bool = False,
        is_create_python_bridge: bool = False, is_try_update_python_bridge: bool = True, default_log_sep: str = " ",
        default_log_module: str = "DATABASE", default_log_level: int | Literal[1, 2, 3, 4, 5, 6, 7, 8, 9] = 1
    ) -> None:
        super().__init__(
            config=config, path_to_sql=path_to_sql, is_dictionary=is_dictionary,
            is_console_log=is_console_log, is_log_backtrace=is_log_backtrace, raise_log_on_fail=raise_log_on_fail,
            is_pprint=is_pprint, is_protected=is_protected, is_auto_start=is_auto_start,
            is_try_update_db=is_try_update_db, is_create_python_bridge=is_create_python_bridge,
            is_try_update_python_bridge=is_try_update_python_bridge, default_log_sep=default_log_sep,
            default_log_module=default_log_module, default_log_level=default_log_level
        )
