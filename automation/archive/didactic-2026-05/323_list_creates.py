import paramiko
import os
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
import glob
import os
import re

files = glob.glob('/tmp/extracted_migrations/*.sql')
print(f"Total SQL files found: {len(files)}")
matches = []
for fpath in sorted(files):
    if not fpath.endswith('.up.sql'):
        continue
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        # Find CREATE TABLE
        tbls = re.findall(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9._]+)', content, re.IGNORECASE)
        # Find CREATE VIEW
        views = re.findall(r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+([a-zA-Z0-9._]+)', content, re.IGNORECASE)
        if tbls or views:
            matches.append((os.path.basename(fpath), tbls, views))

print("Created tables/views in migrations:")
for name, tbls, views in matches:
    print(f" - {name}: tables={tbls}, views={views}")
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/list_creates.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/list_creates.py")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/list_creates.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
