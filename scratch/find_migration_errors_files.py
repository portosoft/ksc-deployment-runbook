import paramiko
import os
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
import glob
import os

keywords = [
    'ui_locales',
    'resources_schedule_pkey',
    'ksc_directory_object_uniq_idx',
    'workspace_id',
    'deleting_outbox'
]

files = glob.glob('/tmp/extracted_migrations/*.sql')
print(f"Searching in {len(files)} SQL files...")

for kw in keywords:
    print(f"\\nKeyword: {kw}")
    matches = []
    for fpath in files:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if kw in content:
                matches.append(os.path.basename(fpath))
    for m in sorted(matches):
        print(f"  - {m}")
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/find_errors_files.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/find_errors_files.py")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/find_errors_files.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
