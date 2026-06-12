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

files_to_print = [
    '1756292212_client.up.sql',
    '1756292274_oauth2.up.sql'
]

for f in files_to_print:
    print(f"\\n=================== FILE: {f} ===================")
    try:
        with open(f'/tmp/extracted_migrations/{f}', 'r', encoding='utf-8') as file_obj:
            print(file_obj.read())
    except Exception as e:
        print(f"Error reading file: {e}")
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/view_hydra.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/view_hydra.py")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/view_hydra.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
