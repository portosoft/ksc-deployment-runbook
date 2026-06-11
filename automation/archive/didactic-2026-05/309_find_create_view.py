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

# Let's search for CREATE VIEW (case-insensitive)
matches = list(re.finditer(rb'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW', data, re.IGNORECASE))
print(f"Total CREATE VIEW matches: {len(matches)}")
for m in matches:
    start = max(0, m.start() - 50)
    end = min(len(data), m.end() + 300)
    chunk = data[start:end]
    printable = "".join(chr(b) if 32 <= b < 127 or b in (10, 13) else "." for b in chunk)
    print(f"Match at {m.start()}:")
    print(printable)
    print("-" * 80)
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/find_create_view.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/find_create_view.py")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/find_create_view.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
