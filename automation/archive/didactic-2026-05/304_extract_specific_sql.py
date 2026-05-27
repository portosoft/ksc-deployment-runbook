import paramiko
import os
import sys
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        remote_script = """
import sys

with open('/opt/kaspersky/ksc64/sbin/kliam', 'rb') as f:
    data = f.read()

for target in [
    '1651676285_add_created_at_column_iam_users.up.sql',
    '1651676285_add_created_at_column_iam_users.down.sql',
    '1683058390_add_login_and_idpaccess_columns_iam_users.up.sql',
    '1683058390_add_login_and_idpaccess_columns_iam_users.down.sql',
    '1647868891_database_schema.up.sql',
    '1647868891_database_schema.down.sql'
]:
    target_bytes = target.encode('ascii')
    idx = data.find(target_bytes)
    if idx == -1:
        print(f"Target '{target}' not found.")
        continue
    print(f"=== Target '{target}' at index {idx} ===")

    # Go embed typically groups files. Let's find the SQL statements in the binary.
    # We can also walk forward from the index to see if there is any SQL code.
    # Let's search the binary for BEGIN; or ALTER or CREATE within 1MB of the target filename.
    # Actually, let's print 500 bytes directly after the target string first.
    chunk = data[idx:idx+1500]
    printable = "".join(chr(b) if (32 <= b < 127 or b in (10, 13)) else "." for b in chunk)
    print(printable)
    print("*" * 60)
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/extract_specific_sql.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/extract_specific_sql.py")
        print(stdout.read().decode("utf-8", errors="replace"))

        client.exec_command("rm -f /tmp/extract_specific_sql.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
