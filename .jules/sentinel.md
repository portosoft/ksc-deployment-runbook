## 2024-05-18 - Fix SQL injection in rollback role drop
**Vulnerability:** Unescaped database user variable (`config.db_user`) was used in a dynamically constructed `DROP ROLE` SQL query in `automation/python/rollback.py`.
**Learning:** Even administrative operations like `DROP ROLE` can be vulnerable to SQL injection if user-provided configuration values are not properly escaped when constructing raw SQL commands via command-line tools like `psql`.
**Prevention:** Always escape variables used in raw SQL strings, especially for identifiers like usernames where standard parameterization isn't typically available. For PostgreSQL identifiers, replace `"` with `""`.
