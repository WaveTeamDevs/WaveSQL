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

import mysql
import colorama
import os
import traceback
import configparser
import copy
import inspect
import shutil
import pathlib
import sys
import pprint
import functools
import asyncio

from mysql.connector.aio import connect
from mysql.connector.errorcode import ER_BAD_DB_ERROR
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from typing import Literal, Any
from datetime import datetime
from colorama import Fore
from pathlib import Path


if __name__ == "__main__":
    from constants import PATH_DB_INIT_SCRIPTS, CONFIG_PATH, LOG_COLORS
    from sqlFileObject import SqlFileObject, SqlFileQueries
else:
    from .constants import PATH_DB_INIT_SCRIPTS, CONFIG_PATH, LOG_COLORS
    from .sqlFileObject import SqlFileObject, SqlFileQueries

colorama.init(autoreset=True)


def read_files_to_vars(directory: str):
    dir_path = Path(directory)
    file_contents = {}
    
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Folder {directory} not found")

    for file_path in dir_path.iterdir():
        if file_path.is_file():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                file_contents[file_path.name] = content

    return file_contents


class AsyncWaveSQL:
    """Example:\n
        adb = AsyncWaveSQL(is_dictionary=True, is_console_log=True, is_log_backtrace=True, is_auto_start=True)
        adb.sync_log(level=3, text="All is good!")
        
    default_log_level : int, optional
            Logging level indicating the type of message. Default is 1 (INFO).

            Available levels:
            - 1: INFO — general information (color: CYAN)
            - 2: DEBUG — debug information (color: MAGENTA)
            - 3: OK — successful operation (color: GREEN)
            - 4: WARNING — warning that does not affect execution (color: YELLOW)
            - 5: FAILURE — logic or business error (color: RED)
            - 6: EXPECTED ERROR — an expected error (color: RED)
            - 7: UNEXPECTED ERROR — an unexpected error (color: RED)
            - 8: ERROR — general error (color: RED)
            - 9: FATAL ERROR — critical error requiring immediate attention (color: LIGHTRED)
    """
    def __init__(
        self, config: dict | str | None = None, path_to_sql: Path | str | None = None, is_dictionary: bool = False,
        is_console_log: bool = False, is_log_backtrace: bool = False, raise_log_on_fail: bool = False,
        is_pprint: bool = False, is_protected: bool = True, is_auto_start: bool = False, is_try_update_db: bool = False,
        is_create_python_bridge: bool = False, is_try_update_python_bridge: bool = True, default_log_sep: str = " ",
        default_log_module: str = "DATABASE", default_log_level: int | Literal[1, 2, 3, 4, 5, 6, 7, 8, 9] = 1
    ) -> None:
        if not isinstance(config, dict):
            if config is None:
                config = CONFIG_PATH
            self.config = configparser.ConfigParser()
            self.config.read(config, encoding="utf-8")
        else:
            self.config = config
        if path_to_sql is None:
            self.path_to_sql = PATH_DB_INIT_SCRIPTS
        else:
            if not isinstance(path_to_sql, (Path, str)):
                raise TypeError(f"Expected 'path_to_sql' to be of type Path (Path or str), but got: {type(path_to_sql).__name__}")
            self.path_to_sql = path_to_sql if isinstance(path_to_sql, Path) else Path(path_to_sql)
        if not isinstance(is_dictionary, bool):
            raise TypeError(f"Expected 'is_dictionary' to be of type bool (True or False), but got: {type(is_dictionary).__name__}")
        self.is_dictionary = is_dictionary
        if not isinstance(is_console_log, bool):
            raise TypeError(f"Expected 'is_console_log' to be of type bool (True or False), but got: {type(is_console_log).__name__}")
        self.is_console_log = is_console_log
        if not isinstance(is_log_backtrace, bool):
            raise TypeError(f"Expected 'is_log_backtrace' to be of type bool (True or False), but got: {type(is_log_backtrace).__name__}")
        self.is_log_backtrace = is_log_backtrace
        if not isinstance(raise_log_on_fail, bool):
            raise TypeError(f"Expected 'raise_log_on_fail' to be of type bool (True or False), but got: {type(raise_log_on_fail).__name__}")
        self.raise_log_on_fail = raise_log_on_fail
        if not isinstance(is_pprint, bool):
            raise TypeError(f"Expected 'is_pprint' to be of type bool (True or False), but got: {type(is_pprint).__name__}")
        self.is_pprint = is_pprint
        if not isinstance(is_protected, bool):
            raise TypeError(f"Expected 'is_protected' to be of type bool (True or False), but got: {type(is_protected).__name__}")
        self.is_protected = is_protected
        if not isinstance(is_try_update_db, bool):
            raise TypeError(f"Expected 'is_try_update_db' to be of type bool (True or False), but got: {type(is_try_update_db).__name__}")
        self.is_try_update_db = is_try_update_db
        if not isinstance(is_create_python_bridge, bool):
            raise TypeError(f"Expected 'is_create_python_bridge' to be of type bool (True or False), but got: {type(is_create_python_bridge).__name__}")
        self.is_create_python_bridge = is_create_python_bridge
        if not isinstance(is_try_update_python_bridge, bool):
            raise TypeError(f"Expected 'is_try_update_python_bridge' to be of type bool (True or False), but got: {type(is_try_update_python_bridge).__name__}")
        self.__is_try_update_python_bridge = is_try_update_python_bridge
        if not isinstance(default_log_sep, str):
            self.default_log_sep = str(default_log_sep)
        self.default_log_sep = default_log_sep
        if not isinstance(default_log_module, str):
            self.default_log_module = str(default_log_module)
        self.default_log_module = default_log_module
        if not isinstance(default_log_level, int):
            raise TypeError(f"Expected 'default_log_level' to be of type int (worked examples in (1, 2, 3, 4, 5, 6, 7, 8, 9)), but got: {type(default_log_level).__name__}")
        self.default_log_level = default_log_level
        
        self.__db_init_succsess = False

        self.run_path: Path = pathlib.Path("/".join(str(sys.argv[0]).replace("\\", "/").split("/")[:-1])).resolve()
        self.local_dir: Path = Path(__file__).parent
        
        self.settings = {"dbname": self.config["MYSQL"]["database"]}
        
        # * autorun
        if is_auto_start:
            self.sync_start()
    
    def run_async(self, coro):
        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(coro)
            return asyncio.run_coroutine_threadsafe(task, loop).result()
        except RuntimeError:
            return asyncio.run(coro)
    
    @staticmethod
    def __protected(method):
        @functools.wraps(method)
        async def wrapper(self, *args, **kwargs):
            caller_frame = inspect.stack()[1].frame
            caller_self = caller_frame.f_locals.get('self')

            if caller_self is not None and isinstance(caller_self, self.__class__):
                return await method(self, *args, **kwargs)

            raise PermissionError(f"Async method '{method.__name__}' is protected and cannot be called from outside")
        
        return wrapper
    
    async def start(self) -> None:
        all_sql_paths = sorted(self.path_to_sql.rglob("*_init_*.sql"), key=lambda x: int(Path(x).name.split("_")[0]))
        # required_files = {"0_init_db.sql", "1_init_logs.sql"}
        dir_path = self.local_dir / "sql"
        required_files = {f.name for f in dir_path.rglob('*') if f.is_file()}
        
        found_filenames = {p.name for p in all_sql_paths}
        missing_files = required_files - found_filenames
        sql_file_objects = []
        if missing_files:
            local_sql_dir = self.local_dir / "sql"
            if not local_sql_dir.exists():
                raise FileNotFoundError(f"Local folder with default SQL files not found: {local_sql_dir}")
            for file_name in missing_files:
                src_file = local_sql_dir / file_name
                dest_file = self.path_to_sql / file_name
                if not src_file.exists():
                    raise FileNotFoundError(f"Local file missing: {src_file}")
                
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src_file, dest_file)
                await self.__print_log(backtrace=None, def_level="INFO", def_color="CYAN", def_module="DATABASE", def_msg=f"Copied file {file_name} from local folder to {dest_file}", is_raise_on_fail=False)
        else:
            await self.__print_log(backtrace=None, def_level="INFO", def_color="CYAN", def_module="DATABASE", def_msg="All required SQL files found in the user path.", is_raise_on_fail=False)
            
        all_sql_paths = sorted(self.path_to_sql.rglob("*_init_*.sql"), key=lambda x: int(Path(x).name.split("_")[0]))
        sql_file_objects.extend([SqlFileObject(path=i, dict_of_values=self.settings) for i in all_sql_paths])
        
        try:
            cnx = await connect(**self.config["MYSQL"])
            if self.is_try_update_db:
                # TODO write db update
                pass
            await cnx.close()
            
            await self.log(level=1, text="Initializing skipped!")
        except mysql.connector.Error as err:
            if err.errno == ER_BAD_DB_ERROR:
                try:
                    connection = await connect(
                        host=self.config["MYSQL"]["host"],
                        user=self.config["MYSQL"]["user"],
                        password=self.config["MYSQL"]["password"]
                    )
                    cursor = await connection.cursor()
                    for sql_file_object in sql_file_objects:
                        for sql_command in sql_file_object.sql_objects:
                            try:
                                await cursor.execute(sql_command.code)
                            except Exception as ex:
                                error_text = str(ex)
                                msg = (
                                    f"[SQL INIT ERROR]\n"
                                    f"File: {sql_file_object.file_path}\n"
                                    f"Object: {sql_command.name}\n"
                                    f"SQL Code:\n"
                                    f"{sql_command.code.strip()}\n"
                                    f"{error_text}\n"
                                )
                                try:
                                    await self.log(level=8, text=msg, err=ex, is_console_log=True, is_log_backtrace=False, is_raise_on_fail=True)
                                except Exception:
                                    await self.__print_log(backtrace=ex, def_module="DATABASE", def_msg=msg, is_raise_on_fail=True)
                                quit(0)
                                
                    await connection.commit()
                    await cursor.close()
                    await connection.close()
                except Exception as ex:
                    try:
                        await self.log(level=8, text="Error initializing the database:", err=ex, is_console_log=True, is_log_backtrace=True, is_raise_on_fail=True)
                    except Exception:
                        await self.__print_log(backtrace=ex, def_module="DATABASE", def_msg="Error initializing the database:", is_raise_on_fail=True)
                await self.log(level=3, text="Database initialized!")
                
        if self.is_create_python_bridge:
            queries_path = self.path_to_sql / "queries.sql"
            if os.path.exists(queries_path):
                files = read_files_to_vars(directory=self.local_dir / "python")
                
                query_file = SqlFileQueries(path=queries_path, create_python=self.is_create_python_bridge, is_dictionary_default=self.is_dictionary, dict_of_values=self.settings)
                
                sql_queries_sync_lst = []
                sql_queries_async_lst = []
                
                for sql_file in sql_file_objects:
                    for sql_object in sql_file.sql_objects:
                        if sql_object.can_python:
                            sql_queries_sync_lst.append(sql_object.sync_python_code)
                            sql_queries_async_lst.append(sql_object.async_python_code)
                
                for sql_query in query_file.sql_queries:
                    if sql_query.can_python:
                        sql_queries_sync_lst.append(sql_query.sync_python_code)
                        sql_queries_async_lst.append(sql_query.async_python_code)
                        
                files["database.py"] += "\n" + "\n\n".join(sql_queries_sync_lst) + "\n\n\n" + 'db = WaveSQL(is_dictionary=True, is_console_log=True, is_log_backtrace=True, is_auto_start=True)\ndb.log(level=3, text="All is good!")\n'
                files["asyncdatabase.py"] += "\n" + "\n\n".join(sql_queries_async_lst) + "\n\n\n" + 'async_db = AsyncWaveSQL(is_dictionary=True, is_console_log=True, is_log_backtrace=True, is_auto_start=True)\nasync_db.sync_log(level=3, text="All is good!")\n'
                
                for filename, content in files.items():
                    file_path = self.run_path / filename
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

        await self.log(level=3, text="All is good !")

    def sync_start(self) -> None:
        self.run_async(self.start())

    async def __db_connect(
        self,
        database: str | None = None,
        is_dictionary: bool | None = None
    ) -> tuple[MySQLConnection, MySQLCursor]:
        """
        Establishes a connection to the MySQL database and returns a connection and cursor.

        Args:
            database (str, optional): Name of the target database. If None, the default from config is used.
            is_dictionary (bool, optional): If True, returns rows as dictionaries. If None, uses instance default.

        Returns:
            tuple[MySQLConnection, MySQLCursor]:
                A tuple containing the database connection and a cursor object.

        Raises:
            TypeError: If 'database' is provided but not a string.
            Exception: Any connection error is re-raised after logging.
        """
        if is_dictionary is None:
            is_dictionary = self.is_dictionary
            
        try:
            if database is not None:
                if not isinstance(database, str):
                    raise TypeError

                mysql_config = copy.deepcopy(self.config["MYSQL"])
                mysql_config["database"] = database
            else:
                mysql_config = self.config["MYSQL"]

            connection = await connect(**mysql_config, use_unicode=True)
            cursor = await connection.cursor(buffered=True, dictionary=is_dictionary)
            
            self.__db_init_succsess = True

            return connection, cursor
        except Exception as err:
            if database is not None:
                if self.__db_init_succsess:
                    await self.log(
                        level=8,
                        module="DATABASE",
                        text=f"DB_CONNECT: {database}",
                        err=err,
                        is_console_log=True
                    )
                else:
                    print(LOG_COLORS["LIGHTRED"] + f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [ERROR] [DATABASE] DB_CONNECT: {database}")
            raise err

    @__protected
    async def _db_query(
        self,
        query: str,
        inputs: tuple | Any = (),
        fetch: Literal[0, 1, 2] = 0,
        database: str | None = None,
        is_dictionary: bool | None = None
    ) -> None | list[tuple] | list[dict] | tuple | dict:
        """
        Executes a SQL query with optional input parameters and fetch mode.

        Args:
            query (str): SQL query string to be executed.
            inputs (tuple or Any, optional): Parameters to pass with the query. Defaults to ().
            fetch (Literal[0, 1, 2], optional) Result retrieval mode
            - 0: Return None (no data expected).
            - 1: Return a single row.
            - 2: Return all rows.
            ---------------------
            database (str, optional): Target database name. Defaults to config value.
            is_dictionary (bool, optional): If True, results are returned as dicts. If False, as tuples. If None using default value `self.is_dictionary`.

        Returns
        ------------------
        None | tuple | dict | list[tuple] | list[dict]:
            - None: if fetch = 0,
            - tuple/dict: if fetch = 1,
            - list of tuple/dict: if fetch = 2

        Raises:
            Exception: Any error raised during SQL execution, re-raised after logging.
        """
        connection, cursor = await self.__db_connect(database, is_dictionary)
        result = None

        try:
            if not isinstance(inputs, tuple):
                inputs = (inputs,)

            await cursor.execute(query, inputs)

            if fetch == 1:
                result = await cursor.fetchone()
            elif fetch == 2:
                result = await cursor.fetchall()

            await connection.commit()
        except Exception as err:
            await self.log(
                level=8,
                module="DATABASE",
                text=f"DB_QUERY: {query}",
                err=err,
                is_console_log=True
            )
            raise err
        finally:
            await cursor.close()
            await connection.close()
            return result

    @__protected
    async def _db_call_procedure(
        self,
        procedure_name: str,
        inputs: tuple | Any = (),
        fetch: Literal[0, 1, 2] = 0,
        database: str | None = None,
        is_dictionary: bool | None = None
    ) -> None | list[tuple] | list[dict] | tuple | dict:
        """
        Calls a stored procedure in the MySQL database and optionally fetches results.

        Args:
            procedure_name (str): The name of the stored procedure to call.
            inputs (tuple or Any, optional): Parameters for the procedure. Defaults to ().
            fetch (Literal[0, 1, 2], optional): Result retrieval mode:
                - 0: Return None.
                - 1: Return a single row.
                - 2: Return all rows.
            database (str, optional): Target database name. Defaults to config value.
            is_dictionary (bool, optional): If True, results are returned as dicts. If False, as tuples. If None using default value `self.is_dictionary`.

        Returns:
            None | tuple | dict | list[tuple] | list[dict]:
                - None: if fetch = 0,
                - tuple/dict: if fetch = 1,
                - list of tuple/dict: if fetch = 2

        Raises:
            Exception: Any error during procedure execution is re-raised after logging.
        """
        connection, cursor = await self.__db_connect(database=database, is_dictionary=is_dictionary)
        result = None
        
        try:
            if not isinstance(inputs, tuple):
                inputs = (inputs,)

            await cursor.callproc(procedure_name, inputs)

            for result_cursor in cursor.stored_results():
                if fetch == 1:
                    result = await result_cursor.fetchone()
                elif fetch == 2:
                    result = await result_cursor.fetchall()

            await connection.commit()
        except Exception as err:
            await self.log(
                level=8,
                module="DATABASE",
                text=f"DB_PROCEDURE: {procedure_name}",
                err=err,
                is_console_log=True
            )
            raise err
        finally:
            await cursor.close()
            await connection.close()
            return result

    async def __save_log_query(
        self, *, level: int, module: str,
        msg: str, backtrace: str
    ) -> dict:
        return await self._db_call_procedure(
            "insert_log",
            (
                level,
                module,
                msg,
                backtrace
            ), fetch=1,
            is_dictionary=True
        )

    async def log(
        self, text: str | Exception | Any = "", *args, level: int = None,
        sep: str = " ", module: str = None, err: Exception | None = None,
        is_console_log: bool | None = None, is_log_backtrace: bool | None = None,
        is_raise_on_fail: bool | None = None, is_pprint: bool | None = None, **kwargs
    ) -> None | Exception:
        """
        Logs a message or exception to the database and, if necessary, to the console.

        Parameters
        ----------
        level : int, optional
            Logging level that determines the type of message. Default is 1 (INFO).
            
            Available levels:
            
            - 1: INFO — general information (color: CYAN)
            - 2: DEBUG — debugging information (color: MAGENTA)
            - 3: OK — successful operation completion (color: GREEN)
            - 4: WARNING — warning not affecting execution (color: YELLOW)
            - 5: FAILURE — logic or business error (color: RED)
            - 6: EXPECTED ERROR — expected error (color: RED)
            - 7: UNEXPECTED ERROR — unexpected error (color: RED)
            - 8: ERROR — standard error (color: RED)
            - 9: FATAL ERROR — critical error requiring immediate attention (color: LIGHTRED)

        text : Any, optional
            Message to log or exception object. Default is an empty string.

        module : str, optional
            Name of the module from which the log is sent. Default is "database".

        err : Exception, optional
            Exception to log (if passed separately from `text`). Default is None.

        is_console_log : bool, optional
            Explicitly indicates whether to output the log to the console. If None, uses the value of `self.is_console_log`.

        Behavior
        --------
        - Converts `text` to a string for logging.
        - If an exception is passed (`err` or `text` is an `Exception`), formats the stack trace.
        - If `is_console_log=True`, additionally outputs the log to the console via `self.__print_log(...)`.

        Notes
        -----
        The method uses `traceback.format_exception` to obtain the exception traceback string.
        """
        if is_console_log is None:
            is_console_log = self.is_console_log
        if is_log_backtrace is None:
            is_log_backtrace = self.is_log_backtrace
        if is_raise_on_fail is None:
            is_raise_on_fail = self.raise_log_on_fail
        if sep is None:
            sep = self.default_log_sep
        if level is None:
            level = self.default_log_level
        if module is None:
            module = self.default_log_module

        parts = [str(text)] if text != "" else []
        parts.extend(str(a) for a in args)
        if kwargs:
            kwargs_str = sep.join(f"{k}={v}" for k, v in kwargs.items())
            parts.append(kwargs_str)

        msg = sep.join(parts)

        if isinstance(err, Exception):
            backtrace = "".join(traceback.format_exception(type(err), err, err.__traceback__))
        elif isinstance(text, Exception):
            backtrace = "".join(traceback.format_exception(type(text), text, text.__traceback__))
        else:
            backtrace = ""
        try:
            db_log: dict = await self.__save_log_query(level=level, module=module, msg=msg, backtrace=backtrace)
            new_backtrace = None
        except Exception as ex:
            new_backtrace = ex
            db_log: dict = {}
            is_console_log = True
        if is_console_log:
            if db_log == {} or db_log is None:
                new_backtrace = (new_backtrace if new_backtrace else backtrace)
                return await self.__print_log(log=db_log, backtrace=new_backtrace, def_msg=msg, is_raise_on_fail=is_raise_on_fail, is_pprint=is_pprint)
            else:
                return await self.__print_log(log=db_log, backtrace=(backtrace if is_log_backtrace and backtrace else None), is_raise_on_fail=is_raise_on_fail, is_pprint=is_pprint)
    
    def sync_log(
        self, text: str | Exception | Any = "", *args, level: int | None = None,
        sep: str = " ", module: str | None = None, err: Exception | None = None,
        is_console_log: bool | None = None, is_log_backtrace: bool | None = None,
        is_raise_on_fail: bool | None = None, is_pprint: bool | None = None, **kwargs
    ) -> None | Exception:
        """
        Logs a message or exception to the database and, optionally, to the console.

        Parameters
        ----------
        level : int, optional
            Logging level indicating the type of message. Default is 1 (INFO).

            Available levels:
            - 1: INFO — general information (color: CYAN)
            - 2: DEBUG — debug information (color: MAGENTA)
            - 3: OK — successful operation (color: GREEN)
            - 4: WARNING — warning that does not affect execution (color: YELLOW)
            - 5: FAILURE — logic or business error (color: RED)
            - 6: EXPECTED ERROR — an expected error (color: RED)
            - 7: UNEXPECTED ERROR — an unexpected error (color: RED)
            - 8: ERROR — general error (color: RED)
            - 9: FATAL ERROR — critical error requiring immediate attention (color: LIGHTRED)

        text : Any, optional
            The message to log or an exception object. Defaults to an empty string.

        module : str, optional
            The name of the module from which the log is sent. Defaults to "DataBase".

        err : Exception, optional
            Exception to be logged (if passed separately from `text`). Defaults to None.

        console_log : bool, optional
            Explicitly determines whether to output the log to the console.
            If None, uses the value from `self.console_log`.

        Behavior
        --------
        - Converts `text` to a string for logging.
        - If an exception is passed (`err` or `text` is an Exception), formats the traceback.
        - If `console_log` is True, also prints the log using `self.__print_log(...)`.

        Notes
        -----
        This method uses `traceback.format_exception` to extract the stack trace from the exception.
        """
        return self.run_async(self.log(text, *args, level=level, sep=sep, module=module, err=err, is_console_log=is_console_log, is_log_backtrace=is_log_backtrace, is_raise_on_fail=is_raise_on_fail, is_pprint=is_pprint, **kwargs))
        
    async def __print_log(
        self, log: dict | None = None, backtrace: str | None = None, def_level: str | None = "ERROR",
        def_module: str | None = "logs", def_color: str | None = "LIGHTRED",
        def_time: datetime | None = datetime.now(), def_msg: str | None = "Unloggable error !!!",
        is_raise_on_fail: bool | None = None, is_pprint: bool | None = None
    ) -> None | Exception:
        if is_raise_on_fail is None:
            is_raise_on_fail = self.raise_log_on_fail
            
        if is_pprint is None:
            is_pprint = self.is_pprint
            
        if log is not None:
            color = LOG_COLORS.get(log.get("log_level_color_name", def_color), Fore.RED)
            log_time_str = log.get("log_date", def_time).strftime("%d-%m-%Y %H:%M:%S")
            log_level = log.get("log_level_name", def_level)
            module = log.get("log_module", def_module)
            msg = log.get("log_message", def_msg)
            # backtrace = log.get("", backtrace)
            print_mes = f"[{log_time_str}] [{log_level}] [{module}] {msg}"
        else:
            print_mes = f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [{def_level}] [{def_module}] {def_msg}"
            color = LOG_COLORS[f"{def_color}"]
            
        if backtrace is not None:
            print_mes = f"{print_mes}\n{backtrace}"
            
            # print(color)
            # print(print_mes)
            
        if is_pprint:
            pprint(color + print_mes)
        else:
            print(color + print_mes)


if __name__ == "__main__":
    adb = AsyncWaveSQL(is_dictionary=True, is_console_log=True, is_log_backtrace=True, is_auto_start=True)
    adb.sync_log(level=3, text="All is good!")
