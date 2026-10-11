## 2024-10-11 - [SQL Injection in DO Blocks and Nested Queries]
**Vulnerability:** SQL injection in PostgreSQL `DO $$ BEGIN` blocks via interpolated variables and in nested `\gexec` statements due to unescaped single quotes and identifiers.
**Learning:** Hardcoded `$$` allows malicious payloads containing `$$` to break out of anonymous code blocks. Further, escaping nested `SELECT` strings must happen on the entire inner query before wrapping it in single quotes.
**Prevention:** Use randomized alphanumeric tags (e.g., `$q<uuid>$`) for `DO` blocks, and apply explicit identifier/literal escaping via `.replace("'", "''")` and `.replace('"', '""')` respectively.
