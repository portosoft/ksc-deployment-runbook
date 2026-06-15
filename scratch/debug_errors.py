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

    print("=== Journalctl Errors for ksc-web-console ===")
    stdin, stdout, stderr = client.exec_command("sudo -S journalctl -u ksc-web-console --no-pager | grep -i error | tail -n 50")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode('utf-8'))

    client.close()

if __name__ == "__main__":
    main()
