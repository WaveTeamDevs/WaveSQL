# 🌊 WaveSQL

[`Read this in Russian`](README.ru.md)

**WaveSQL** is a lightweight yet powerful Python library for secure, synchronous and asynchronous interaction with MySQL and MariaDB.

> Developed by [`WaveTeam`](https://github.com/WaveTeamDevs) under the leadership of [`eelus1ve`](https://github.com/eelus1ve)

---

## 🚀 Features

- 🔌 Easy database connection via config.ini or dictionary
- ⚙️ Automatic database schema initialization on first run
- 🧠 Support for calling stored procedures (CALL)
- 🪝 Protected methods (via @protected) — prevent direct calls to critical ftextions
- 🐍 Asynchronous version with the same API
- 🪵 Built-in logging to database + colored console output (colorama)
- 🧠 Automatic generation of Python code (Python Bridge) from SQL files
- 🧩 Flexible configuration: dictionary=True, colored output, pprint, backtrace control
- 🛡️ Error catching and logging with traceback
- 🧪 Protection against missing or incomplete SQL files

---

## 📦 Installation

```bash
pip install wavesql
```

## 🧰 Usage

🔹 Simple example
```python
from wavesql import WaveSQL

db = WaveSQL(
    is_dictionary=True,
    is_console_log=True,
    is_log_backtrace=True,
    is_auto_start=True
)

db.log(level=3, text="All is good!")

```

---


## 🌀 Asynchronous version

```python
from wavesql.aio import AsyncWaveSQL

adb = AsyncWaveSQL(
    is_dictionary=True,
    is_console_log=True,
    is_log_backtrace=True,
    is_auto_start=True
)

await adb.log(level=3, text="Async logging works!")
```

# All methods and behavior are identical to the synchronous version.
# Just use await and import AsyncWaveSQL from wavesql.aio.

---


## 🧠 Generating Python code from SQL


If your SQL directory contains a `queries.sql` file, WaveSQL can automatically generate Python code to call the SQL queries defined in it.

Example content of `queries.sql`:

```sql
create get_user with query SELECT * FROM users WHERE id = {% extend user_id : int %} LIMIT 1;
```

Explanation of syntax:

- `create get_user` — declares the function/method name to be generated.

- `with query` — keyword indicating the following is the SQL query.

- Inside the query, `{% extend user_id : int %}` means the generated method will have a parameter `user_id` of type `int`.

- The SQL query safely substitutes this parameter (with `%s` or equivalent) to prevent SQL injection.


Simply enable the flag `is_create_python_bridge=True` during initialization:

```python

db = WaveSQL(
    is_create_python_bridge=True,
    ...
)

```

The following files will be created:

- `database.py` — synchronous interface

- `asyncdatabase.py` — asynchronous interface

- `aio.py` — entry point for async API

- `__init__.py` — entry point for sync API

- library SQL files that initialize the database and create minimal necessary tables for proper module operation

---


## 🧰 Usage with is_create_python_bridge=True

📁 Project structure (before running `run.py`):
```bash
database/
├── sql/
│   ├── 2_init_users.sql
│   └── queries.sql
├── run.py
```

🐍 run.py file:
```python
from wavesql import WaveSQL

db = WaveSQL(
    config="path_to_my_settings.ini", path_to_sql="database/sql", is_console_log=True,
    is_log_backtrace=True, is_auto_start=True, is_create_python_bridge=True
)
```

Files with names containing `_init_` and a numeric prefix (e.g., `0_init_users.sql`) are initialized in the database in ascending order of this number.
The prefix must be a non-negative integer — negative values are reserved by the library.

The `queries.sql` file is used for automatic generation of query methods that create two bridges (sync and async).

Example `queries.sql`:
```sql
create get_user with query SELECT * FROM users WHERE id = {% extend user_id : int %} LIMIT 1;
```

Output:
```python
# database.py
def get_user(self, user_id: int) -> dict | None:
    return self._db_query("SELECT * FROM users WHERE id = %s LIMIT 1", (user_id, ), fetch=1)

# asyncdatabase.py
async def get_user(self, user_id: int) -> dict | None:
    return await self._db_query("SELECT * FROM users WHERE id = %s LIMIT 1", (user_id, ), fetch=1)
```

📁 Project structure (after running `run.py`):
```bash
database/
├── sql/
│   ├── 0_init_db.sql
│   ├── 1_init_logs.sql
│   ├── 2_init_users.sql
│   └── queries.sql
├── __init__.py
├── asyncdatabase.py
├── database.py
├── run.py
```

---


## 🧾 Requirements

- Python 3.12.10+
- mysql-connector-python=9.3.0
- colorama=0.4.6

---

## 📁 Project structure
```bash
WaveSQL/
├── wavesql/
│   ├── __init__.py
│   ├── aio.py
│   ├── sqlFileObject.py
│   ├── constants.py
│   ├── asyncdatabase.py
│   ├── database.py
│   ├── errors.py
│   ├── config.ini
│   ├── sql/
│   │   ├── 0_init_db.sql
│   │   └── 1_init_logs.sql
│   ├── python/
│   │   ├── __init__.py
│   │   ├── aio.py
│   │   ├── asyncdatabase.py
│   │   └── database.py
├── README.md
├── NOTICE
├── LICENSE
├── pyproject.toml
└── requirements.txt
```

---

## 📜 Changelog

See [`CHANGELOG.md`](./CHANGELOG.md) for the detailed version history.

---

## 🔮 Planned Features / Roadmap

- [ ] SQLite support
- [ ] Automatic SQL syntax validation
- [ ] Automatic type mapping from SQL tables to Python code
- [ ] Procedure output recognition
- [ ] PostgreSQL support

---

## 👤 Author
- Darov Alexander (eelus1ve)
- Email: darov-alexander@outlook.com
- GitHub: [`@eelus1ve`](https://github.com/eelus1ve)
- Developed as part of [`WaveTeam`](https://github.com/WaveTeamDevs)

---

## 🔗 Links
- 🌍 Repository: [`github.com/WaveTeamDevs/WaveSQL`](https://github.com/WaveTeamDevs/WaveSQL)
- 🧠 Organization: [`WaveTeamDevs`](https://github.com/WaveTeamDevs)

---
