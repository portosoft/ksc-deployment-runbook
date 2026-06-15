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
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        remote_script = """
import re

with open('/opt/kaspersky/ksc64/sbin/kliam', 'rb') as f:
    data = f.read()

# Find migration files
matches = re.findall(rb'migrations/postgres/[a-zA-Z0-9_.-]+', data)
unique_matches = sorted(list(set(m.decode("ascii", errors="ignore") for m in matches)))
print(f"Total files: {len(unique_matches)}")
for idx, m in enumerate(unique_matches):
    print(f"{idx+1:03d}: {m}")
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/list_unique.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/list_unique.py")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/list_unique.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
