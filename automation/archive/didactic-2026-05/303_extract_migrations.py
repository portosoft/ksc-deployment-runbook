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
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Read the binary via Python running on the remote host (more efficient and handles binary safely)
        remote_script = """
import re
with open('/opt/kaspersky/ksc64/sbin/kliam', 'rb') as f:
    data = f.read()

# Search for migrations/postgres/ pattern
matches = re.findall(rb'migrations/postgres/[a-zA-Z0-9_.-]+', data)
unique_matches = sorted(list(set(m.decode("ascii", errors="ignore") for m in matches)))
for m in unique_matches:
    print(m)
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/extract.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/extract.py")
        print("--- Embedded Migrations ---")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/extract.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
