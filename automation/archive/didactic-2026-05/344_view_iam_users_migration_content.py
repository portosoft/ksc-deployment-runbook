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

files = glob.glob('/tmp/extracted_migrations/*iam_users*')
print(f"Total matching files: {len(files)}")
for fpath in sorted(files):
    print(f"\\n=================== FILE: {os.path.basename(fpath)} ===================")
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        print(f.read())
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/view_iam_users_migrations.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command(
            "python3 /tmp/view_iam_users_migrations.py"
        )
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/view_iam_users_migrations.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
