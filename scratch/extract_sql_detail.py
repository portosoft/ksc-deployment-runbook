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
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Remote script to search the binary and print contents for a specific migration path
        remote_script = """
import sys
import re

target = sys.argv[1] if len(sys.argv) > 1 else "1750417290_database_schema.up.sql"

with open('/opt/kaspersky/ksc64/sbin/kliam', 'rb') as f:
    data = f.read()

# Find occurrences of the target filename
target_bytes = target.encode('ascii')
idx = data.find(target_bytes)
if idx == -1:
    print(f"Target '{target}' not found in binary.")
    sys.exit(1)

print(f"Found target '{target}' at index {idx}.")
# Let's print some bytes after the filename.
# Usually, Go embed stores filename followed by file content (possibly with some header/metadata or null bytes, or direct mapping).
# Let's print the next 5000 bytes, printing printable ascii characters.
chunk = data[idx:idx+10000]
printable = "".join(chr(b) if (32 <= b < 127 or b in (10, 13)) else "." for b in chunk)
print("=== PRINTABLE CHUNK ===")
print(printable)
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/extract_sql_detail.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        target = sys.argv[1] if len(sys.argv) > 1 else "1750417290_database_schema.up.sql"
        print(f"Extracting content for: {target}")
        stdin, stdout, stderr = client.exec_command(f"python3 /tmp/extract_sql_detail.py '{target}'")
        print(stdout.read().decode("utf-8", errors="replace"))

        client.exec_command("rm -f /tmp/extract_sql_detail.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
