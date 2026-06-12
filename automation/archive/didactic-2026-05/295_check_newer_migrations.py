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
matches = re.findall(rb'migrations/postgres/([0-9]+)_[a-zA-Z0-9_.-]+', data)
unique_versions = sorted(list(set(int(m.decode('ascii')) for m in matches)))
greater = [v for v in unique_versions if v > 1770629073]
print('Total migrations:', len(unique_versions))
print('Migrations > 1770629073:', greater)
"""
        sftp = client.open_sftp()
        f = sftp.file("/tmp/check_newer.py", "w")
        f.write(remote_script)
        f.close()
        sftp.close()

        stdin, stdout, stderr = client.exec_command("python3 /tmp/check_newer.py")
        print(stdout.read().decode("utf-8"))

        client.exec_command("rm -f /tmp/check_newer.py")
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
