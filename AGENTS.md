Sentinel Security Invariants TOCTOU
## 2024-05-15 - SQL Injection in Role Deletion
**Vulnerability:** SQL Injection in 'rollback.py' when executing DROP ROLE via psql.
**Learning:** Dynamic identifiers (like usernames) used directly in formatted SQL strings passed to the psql command-line tool can lead to SQL injection if not properly escaped, even when enclosed in double quotes.
**Prevention:** Always escape double quotes by doubling them ('"' -> '""') for identifiers or use parameterized queries where supported, to prevent malicious configurations from terminating the identifier early and injecting arbitrary SQL.
