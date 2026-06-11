import paramiko
import os
import re
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        remote_script = """
import re

with open('/opt/kaspersky/ksc64/sbin/kliam', 'rb') as f:
    data = f.read()

# We look for strings that contain CREATE, ALTER, DROP, or SELECT inside SQL-like contexts
# Let's find all printable ASCII segments that look like SQL statements
# Migrations typically start with BEGIN; or contain CREATE TABLE/VIEW
sql_patterns = [
    rb'CREATE\s+VIEW\s+[a-zA-Z0-9_.]+',
    rb'CREATE\s+OR\s+REPLACE\s+VIEW\s+[a-zA-Z0-9_.]+',
    rb'CREATE\s+TABLE\s+[a-zA-Z0-9_.]+',
    rb'CREATE\s+UNIQUE\s+INDEX\s+[a-zA-Z0-9_.]+',
    rb'ALTER\s+TABLE\s+[a-zA-Z0-9_.]+',
    rb'DROP\s+VIEW\s+[a-zA-Z0-9_.]+',
    rb'DROP\s+TABLE\s+[a-zA-Z0-9_.]+',
]

for pat in sql_patterns:
    for match in re.finditer(pat, data, re.IGNORECASE):
        start = max(0, match.start() - 100)
        end = min(len(data), match.end() + 300)
        chunk = data[start:end]
        printable = "".join(chr(b) if 32 <= b < 127 or b in (10, 13) else "." for b in chunk)
        print(f"Matched {match.group(0).decode('ascii', errors='ignore')} at {match.start()}:")
        print(printable)
        print("="*80)
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/extract_sql.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/extract_sql.py")
        print("--- Extracted SQL statements ---")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/extract_sql.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
