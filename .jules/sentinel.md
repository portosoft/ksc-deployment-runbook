## 2024-10-24 - SQL Injection in Database Rollback
**Vulnerability:** SQL Injection in `automation/python/rollback.py`. User input `config.db_user` was interpolated directly into a `DROP ROLE IF EXISTS` SQL command without escaping.
**Learning:** Even internal automation scripts that run high-privilege administrative tasks can be vectors for SQL injection if user configurations aren't properly escaped, especially when managing database roles directly via raw SQL strings passed through subprocess calls.
**Prevention:** Always escape user input when interpolating strings to be executed as SQL commands. For PostgreSQL identifiers, replace `"` with `""`. Alternatively, prefer parameterized queries where the driver handles escaping securely.
