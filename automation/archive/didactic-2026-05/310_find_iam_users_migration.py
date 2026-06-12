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

files = glob.glob('/tmp/extracted_migrations/*.sql')
matches = []
for fpath in files:
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        if 'iam.users' in content or 'CREATE VIEW' in content or 'CREATE OR REPLACE VIEW' in content:
            # We want to see if they refer to iam.users
            if 'users' in content.lower():
                matches.append((os.path.basename(fpath), content))

for name, content in sorted(matches):
    print(f"\\n=================== {name} ===================")
    print(content)
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/search_users.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/search_users.py")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/search_users.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
