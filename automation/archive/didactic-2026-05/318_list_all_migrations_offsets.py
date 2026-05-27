import paramiko
import os
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
import re

with open('/opt/kaspersky/ksc64/sbin/kliam', 'rb') as f:
    data = f.read()

# We look for all migration file names
matches = re.finditer(rb'migrations/postgres/[a-zA-Z0-9_.-]+', data)
for m in matches:
    print(f"{m.start()}: {m.group(0).decode('ascii')}")
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/list_all_migrations_offsets.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/list_all_migrations_offsets.py")
        print(stdout.read().decode("utf-8", errors="replace"))

        client.exec_command("rm -f /tmp/list_all_migrations_offsets.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
