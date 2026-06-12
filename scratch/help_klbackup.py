import os
import paramiko
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    client.connect(host, username=user, password=password)

    print("=== klbackup help ===")
    cmd = "sudo -S LD_LIBRARY_PATH=/opt/kaspersky/ksc64/lib /opt/kaspersky/ksc64/sbin/klbackup -help"
    stdin, stdout, stderr = client.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))

    client.close()

if __name__ == "__main__":
    main()
