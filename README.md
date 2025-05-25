# 🌊 WaveSQL

**WaveSQL** — лёгкая, но мощная Python-библиотека для безопасной, асинхронной и удобной работы с MySQL и MariaDB.

> Разработано [`WaveTeam`](https://github.com/WaveTeamDevs) под руководством [`eelus1ve`](https://github.com/eelus1ve)

---

## 🚀 Возможности

- 🔌 Простое подключение к базе данных через config.ini или словарь
- ⚙️ Автоматическая инициализация структуры БД при первом запуске
- 🧠 Поддержка вызова хранимых процедур (CALL)
- 🪝 Защищённые методы (через @protected) — предотвращают прямой вызов критичных функций
- 🐍 Асинхронная версия с аналогичным API
- 🪵 Встроенное логирование в базу данных + цветной вывод в консоль (colorama)
- 🧠 Автоматическая генерация Python-кода (Python Bridge) из SQL-файла
- 🧩 Гибкая конфигурация: dictionary=True, цветной вывод, pprint, контроль backtrace
- 🛡️ Отлавливание и логирование ошибок с трассировкой (traceback)
- 🧪 Защита от неполных или отсутствующих SQL-файлов

---

## 📦 Установка

```bash
pip install wavesql
```

## 🧰 Использование

🔹 Простой пример
```python
from wavesql import WaveSQL

db = WaveSQL(
    is_dictionary=True,
    is_console_log=True,
    is_log_backtrace=True,
    is_auto_start=True
)

db.log(level=3, data="All is good!")

```

---


## 🌀 Асинхронная версия

```python
from wavesql.async_version import AsyncWaveSQL

async_db = AsyncWaveSQL(
    is_dictionary=True,
    is_console_log=True,
    is_log_backtrace=True,
    is_auto_start=True
)

await async_db.log(level=3, data="Async logging works!")
```

# Все методы и поведение идентичны синхронной версии
# Просто используйте await, и импортируйте из wavesql.async_version

---


## 🧠 Генерация Python-кода из SQL


Если в вашей SQL-директории есть файл queries.sql, содержащий блоки -- name: some_query_name, WaveSQL может автоматически сгенерировать Python-код для вызова этих SQL-запросов.

Просто установите флаг is_create_python_bridge=True при инициализации:

```python

db = WaveSQL(
    is_create_python_bridge=True,
    ...
)

```

В результате будут созданы файлы:

database.py – синхронный интерфейс

asyncdatabase.py – асинхронный интерфейс

---


## 🧰 Использование c is_create_python_bridge=True

📁 Структура проекта (До запуска run.py)
```bash
database/
├── sql/
│   ├── 2_init_users.sql
│   └── queries.sql
├── run.py
```

🐍 Файл run.py
```python
from wavesql import WaveSQL

db = WaveSQL(
    config="path_to_my_settings.ini", path_to_sql="database/sql", is_console_log=True,
    is_log_backtrace=True, is_auto_start=True, is_create_python_bridge=True
)
```

Файлы *_init_* инициализирются в базу данных в порядке возврастания цифры

Файл queries.sql используется для автонаписания запросов на 2 моста

Пример queries.sql:
```sql
create get_user with query SELECT * FROM users WHERE id = {% extend user_id : int %} LIMIT 1;
```

Вывод:
```python
def get_user(self, user_id: int):
    return self._db_query("SELECT * FROM users WHERE id = %s LIMIT 1", (user_id, ), fetch=1)
```

📁 Структура проекта (После запуска run.py)
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


## 🧾 Требования

- Python 3.12.10+
- mysql-connector-python
- colorama

---

## 📁 Структура проекта
```bash
WaveSQL/
├── wavesql/
│   ├── __init__.py
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
│   │   ├── asyncdatabase.py
│   │   └── database.py
├── README.md
├── NOTICE
├── LICENSE
├── pyproject.toml
└── requirements.txt
```

---


## 👤 Автор
- Darov Alexander (eelus1ve)
- Email: darov-alexander@outlook.com
- GitHub: @eelus1ve
- Разработано в рамках WaveTeam

---

## 🔗 Ссылки
- 🌍 Репозиторий: github.com/WaveTeamDevs/WaveSQL
- 🧠 Организация: WaveTeamDevs

---
