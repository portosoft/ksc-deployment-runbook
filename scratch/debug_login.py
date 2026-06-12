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

    print("=== ksc-web-console logs ===")
    stdin, stdout, stderr = client.exec_command("sudo -S journalctl -u ksc-web-console -n 30 --no-pager")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode('utf-8'))

    print("\n=== kliam_srv logs ===")
    stdin, stdout, stderr = client.exec_command("sudo -S journalctl -u kliam_srv -n 30 --no-pager")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode('utf-8'))

    print("\n=== kladminserver_srv logs ===")
    stdin, stdout, stderr = client.exec_command("sudo -S journalctl -u kladminserver_srv -n 30 --no-pager")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode('utf-8'))

    client.close()

if __name__ == "__main__":
    main()
