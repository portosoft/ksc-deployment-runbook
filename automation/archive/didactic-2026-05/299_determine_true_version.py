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

        remote_script = """
import glob
import os
import re

# Let's get all tables and columns from the database
import json

def get_db_schema():
    import subprocess
    cmd = "sudo -u postgres psql -d ksciam -t -A -c \\"SELECT table_schema, table_name, column_name FROM information_schema.columns ORDER BY table_schema, table_name, column_name;\\""
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    schema = {}
    for line in res.stdout.strip().split('\\n'):
        if not line:
            continue
        parts = line.split('|')
        if len(parts) == 3:
            s, t, c = parts[0], parts[1], parts[2]
            full_table = f"{s}.{t}"
            if full_table not in schema:
                schema[full_table] = set()
            schema[full_table].add(c)
    return schema

schema = get_db_schema()
print(f"Database has {len(schema)} tables.")

files = sorted(glob.glob('/tmp/extracted_migrations/*.up.sql'))
print(f"Found {len(files)} UP migrations.")

for fpath in files:
    v_str = os.path.basename(fpath).split('_')[0]
    version = int(v_str)

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all table creations: CREATE TABLE schema.name or CREATE TABLE IF NOT EXISTS schema.name
    # We also check for ALTER TABLE schema.name ADD COLUMN name
    tables_created = re.findall(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_.]+)', content, re.IGNORECASE)
    columns_added = re.findall(r'ALTER\s+TABLE\s+([a-zA-Z0-9_.]+)\s+ADD\s+(?:COLUMN\s+)?([a-zA-Z0-9_]+)', content, re.IGNORECASE)

    all_created_exist = True
    for t in tables_created:
        if '.' not in t:
            t = 'public.' + t
        if t not in schema:
            all_created_exist = False

    all_added_exist = True
    for t, c in columns_added:
        if '.' not in t:
            t = 'public.' + t
        if t not in schema or c not in schema[t]:
            all_added_exist = False

    print(f"Migration {version:11d} ({os.path.basename(fpath)[:35]}): tables_created={tables_created} | exist={all_created_exist} | columns_added={columns_added} | exist={all_added_exist}")
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/det_version.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/det_version.py")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/det_version.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
