# 📄 Changelog

## [1.0.1] - 2025-06-01
### Added
- Generation of `__init__.py` and `aio.py` when using Python Bridge. Now the asynchronous database version is located in `wavesql.aio`.
- The `log` method now works similarly to `print` for more convenient logging.
- New default settings added to the database class, such as `default_log_sep`, `default_log_module`, `default_log_level`.
- Added automatic procedure recognition.
- The default variable was renamed from `async_db` to `adb`.
- All library templates now use negative numbers. Users can start writing their own templates beginning from 0.


### Fixed
- Fixed an issue where console coloring remained set to the last log’s color.
- Fixed class naming to match the import.
- Fixed an error when generating Python code.

## [1.0.0] - 2025-05-27
### Added
- Basic synchronous and asynchronous API.
- Generation of SQL bridges from `queries.sql`.
- Database initialization from `*_init_*.sql` files.