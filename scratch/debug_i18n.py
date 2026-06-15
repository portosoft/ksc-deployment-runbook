import os
import paramiko
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host, username=user, password=password)

    print("=== Searching for languages in setup.js ===")
    stdin, stdout, stderr = client.exec_command("grep -i -A 5 'defaultLanguage' /var/opt/kaspersky/ksc-web-console/setup.js")
    print(stdout.read().decode('utf-8'))

    client.close()

if __name__ == "__main__":
    main()
