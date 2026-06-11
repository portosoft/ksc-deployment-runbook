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

        remote_script = """
import re

with open('/opt/kaspersky/ksc64/sbin/kliam', 'rb') as f:
    data = f.read()

# Find strings matching target
for target in [b'iam.users', b'CREATE VIEW', b'create view', b'iam_users']:
    print(f"=== Matches for {target} ===")
    matches = list(re.finditer(re.escape(target), data, re.IGNORECASE))
    print(f"Total: {len(matches)}")
    for m in matches[:10]:
        start = max(0, m.start() - 150)
        end = min(len(data), m.end() + 250)
        chunk = data[start:end]
        printable = "".join(chr(b) if (32 <= b < 127 or b in (10, 13)) else "." for b in chunk)
        print(f"At {m.start()}:")
        print(printable)
        print("-" * 60)
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/search_binary_strings.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command(
            "python3 /tmp/search_binary_strings.py"
        )
        print(stdout.read().decode("utf-8", errors="replace"))

        client.exec_command("rm -f /tmp/search_binary_strings.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
