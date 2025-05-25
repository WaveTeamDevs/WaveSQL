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

from mysql.connector import connect
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

colorama.init()


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
                print(f"File read: {file_path.name}")

    return file_contents


class WaveSQL:
    """Example:\n
        db = WaveDataBase(is_dictionary=True, is_console_log=True, is_log_backtrace=True, is_auto_start=True)\n
        db.log(level=3, data="All is good!")
    """
    def __init__(
        self, config: dict | str | None = None, path_to_sql: Path | str | None = None, is_dictionary: bool = False,
        is_console_log: bool = False, is_log_backtrace: bool = False, raise_log_on_fail: bool = False,
        is_pprint: bool = False, is_protected: bool = True, is_auto_start: bool = False, is_try_update_db: bool = False,
        is_create_python_bridge: bool = False, is_try_update_python_bridge: bool = True
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
        self.is_try_update_python_bridge = is_try_update_python_bridge
        
        self.__db_init_succsess = False

        self.run_path: Path = pathlib.Path("/".join(str(sys.argv[0]).replace("\\", "/").split("/")[:-1])).resolve()
        self.local_dir: Path = Path(__file__).parent
        
        self.settings = {"dbname": self.config["MYSQL"]["database"]}
        
        # * autorun
        if is_auto_start:
            self.start()
    
    @staticmethod
    def __protected(method):
        def wrapper(self, *args, **kwargs):
            if self.is_protected:
                caller_frame = inspect.stack()[1].frame
                caller_self = caller_frame.f_locals.get('self')

                if caller_self is not None and isinstance(caller_self, self.__class__):
                    return method(self, *args, **kwargs)

                raise PermissionError(f"Async method '{method.__name__}' is protected and cannot be called from outside")
            
            return method(self, *args, **kwargs)
        
        return wrapper
    
    def start(self) -> None:
        all_sql_paths = sorted(self.path_to_sql.rglob("*_init_*.sql"), key=lambda x: int(Path(x).name.split("_")[0]))
        # required_files = {"0_init_db.sql", "1_init_logs.sql"}
        # print(f"local dir = {self.local_dir}")
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
                print(f"Copied file {file_name} from local folder to {dest_file}")
        else:
            print("All required SQL files found in the user path.")
            
        all_sql_paths = sorted(self.path_to_sql.rglob("*_init_*.sql"), key=lambda x: int(Path(x).name.split("_")[0]))
        sql_file_objects.extend([SqlFileObject(path=i, dict_of_values=self.settings) for i in all_sql_paths])
        
        try:
            cnx = connect(**self.config["MYSQL"])
            if self.is_try_update_db:
                # TODO write db update
                pass
            cnx.close()
            
            self.log(level=1, data="Initializing skipped!")
        except mysql.connector.Error as err:
            if err.errno == ER_BAD_DB_ERROR:
                try:
                    connection = connect(
                        host=self.config["MYSQL"]["host"],
                        user=self.config["MYSQL"]["user"],
                        password=self.config["MYSQL"]["password"]
                    )
                    cursor = connection.cursor()
                    for sql_file_object in sql_file_objects:
                        for sql_command in sql_file_object.sql_objects:
                            try:
                                cursor.execute(sql_command.code)
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
                                    self.log(level=8, data=msg, err=ex, is_console_log=True, is_log_backtrace=False, is_raise_on_fail=True)
                                except Exception:
                                    self.__print_log(backtrace=ex, def_module="DATABASE", def_msg=msg, is_raise_on_fail=True)
                                quit(0)
                                
                    connection.commit()
                    cursor.close()
                    connection.close()
                except Exception as ex:
                    try:
                        self.log(level=8, data="Error initializing the database:", err=ex, is_console_log=True, is_log_backtrace=True, is_raise_on_fail=True)
                    except Exception:
                        self.__print_log(backtrace=ex, def_module="DATABASE", def_msg="Error initializing the database:", is_raise_on_fail=True)
                self.log(level=3, data="Database initialized!")
                
        if self.is_create_python_bridge:
            queries_path = self.path_to_sql / "queries.sql"
            if os.path.exists(queries_path):
                files = read_files_to_vars(directory=self.local_dir / "python")
                
                query_file = SqlFileQueries(path=queries_path, create_python=self.is_create_python_bridge, is_dictionary_default=self.is_dictionary, dict_of_values=self.settings)
                
                sql_queries_sync_lst = []
                sql_queries_async_lst = []
                
                for sql_query in query_file.sql_queries:
                    if sql_query.can_python:
                        sql_queries_sync_lst.append(sql_query.sync_python_code)
                        sql_queries_async_lst.append(sql_query.async_python_code)
                        
                files["database.py"] += "\n" + "\n\n".join(sql_queries_sync_lst) + "\n\n\n" + 'db = WaveSQL(is_dictionary=True, is_console_log=True, is_log_backtrace=True, is_auto_start=True)\ndb.log(level=3, data="All is good!")\n'
                files["asyncdatabase.py"] += "\n" + "\n\n".join(sql_queries_async_lst) + "\n\n\n" + 'async_db = AsyncWaveSQL(is_dictionary=True, is_console_log=True, is_log_backtrace=True, is_auto_start=True)\nasync_db.log(level=3, data="All is good!")\n'
                
                for filename, content in files.items():
                    file_path = self.run_path / filename
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

        self.log(level=3, data="All is good !")

    def __db_connect(
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

            connection = connect(**mysql_config, use_unicode=True)
            cursor = connection.cursor(buffered=True, dictionary=is_dictionary)
            
            self.__db_init_succsess = True

            return connection, cursor
        except Exception as err:
            if database is not None:
                if self.__db_init_succsess:
                    self.log(
                        level=8,
                        module="DATABASE",
                        data=f"DB_CONNECT: {database}",
                        err=err,
                        is_console_log=True
                    )
                else:
                    print(LOG_COLORS["LIGHTRED"] + f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [ERROR] [DATABASE] DB_CONNECT: {database}")
            raise err

    @__protected
    def _db_query(
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
        connection, cursor = self.__db_connect(database, is_dictionary)
        result = None

        try:
            if not isinstance(inputs, tuple):
                inputs = (inputs,)

            cursor.execute(query, inputs)

            if fetch == 1:
                result = cursor.fetchone()
            elif fetch == 2:
                result = cursor.fetchall()

            connection.commit()
        except Exception as err:
            self.log(
                level=8,
                module="DATABASE",
                data=f"DB_QUERY: {query}",
                err=err,
                is_console_log=True
            )
            raise err
        finally:
            cursor.close()
            connection.close()
            return result

    @__protected
    def _db_call_procedure(
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
        connection, cursor = self.__db_connect(database=database, is_dictionary=is_dictionary)
        result = None
        
        try:
            if not isinstance(inputs, tuple):
                inputs = (inputs,)

            cursor.callproc(procedure_name, inputs)

            for result_cursor in cursor.stored_results():
                if fetch == 1:
                    result = result_cursor.fetchone()
                elif fetch == 2:
                    result = result_cursor.fetchall()

            connection.commit()
        except Exception as err:
            self.log(
                level=8,
                module="DATABASE",
                data=f"DB_PROCEDURE: {procedure_name}",
                err=err,
                is_console_log=True
            )
            raise err
        finally:
            cursor.close()
            connection.close()
            return result

    def __save_log_query(
        self, *, level: int, module: str,
        msg: str, backtrace: str
    ) -> dict:
        return self._db_call_procedure(
            "insert_log",
            (
                level,
                module,
                msg,
                backtrace
            ), fetch=1,
            is_dictionary=True
        )

    def log(
        self, data: str | Exception | Any = "", *args, level: int = 1,
        sep: str = " ", module: str = "DATABASE", err: Exception | None = None,
        is_console_log: bool | None = None, is_log_backtrace: bool | None = None,
        is_raise_on_fail: bool | None = None, **kwargs
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

        data : Any, optional
            Message to log or exception object. Default is an empty string.

        module : str, optional
            Name of the module from which the log is sent. Default is "database".

        err : Exception, optional
            Exception to log (if passed separately from `data`). Default is None.

        is_console_log : bool, optional
            Explicitly indicates whether to output the log to the console. If None, uses the value of `self.is_console_log`.

        Behavior
        --------
        - Converts `data` to a string for logging.
        - If an exception is passed (`err` or `data` is an `Exception`), formats the stack trace.
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

        parts = [str(data)] if data != "" else []
        parts.extend(str(a) for a in args)
        if kwargs:
            # Опционально: можно форматировать kwargs как "key=value"
            kwargs_str = sep.join(f"{k}={v}" for k, v in kwargs.items())
            parts.append(kwargs_str)

        msg = sep.join(parts)

        if isinstance(err, Exception):
            backtrace = "".join(traceback.format_exception(type(err), err, err.__traceback__))
        elif isinstance(data, Exception):
            backtrace = "".join(traceback.format_exception(type(data), data, data.__traceback__))
        else:
            backtrace = ""
        try:
            db_log: dict = self.__save_log_query(level=level, module=module, msg=msg, backtrace=backtrace)
            new_backtrace = None
        except Exception as ex:
            new_backtrace = ex
            db_log: dict = {}
            is_console_log = True
        if is_console_log:
            if db_log == {} or db_log is None:
                new_backtrace = (new_backtrace if new_backtrace else backtrace)
                return self.__print_log(log=db_log, backtrace=new_backtrace, def_msg=msg, is_raise_on_fail=is_raise_on_fail)
            else:
                return self.__print_log(log=db_log, backtrace=(backtrace if is_log_backtrace and backtrace else None), is_raise_on_fail=is_raise_on_fail)
        
    def __print_log(
        self, log: dict | None = None, backtrace: str | None = None, def_level: str | None = "ERROR",
        def_module: str | None = "logs", def_color: str | None = "RED",
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
            print_mes = f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] [ERROR] [logs] {def_msg}"
            color = LOG_COLORS["LIGHTRED"]
            
        if backtrace is not None:
            print_mes = f"{print_mes}\n{backtrace}"
            
            # print(color)
            # print(print_mes)
            
        if is_pprint:
            pprint(color + print_mes)
        else:
            print(color + print_mes)


if __name__ == "__main__":
    db = WaveSQL(is_dictionary=True, is_console_log=True, is_log_backtrace=True, is_auto_start=True)
    db.log(level=3, data="All is good!")
