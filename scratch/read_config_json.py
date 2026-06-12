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

    print("=== config.json size ===")
    cmd = "sudo -S ls -la /var/opt/kaspersky/ksc-web-console/server/config.json"
    stdin, stdout, stderr = client.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))

    print("\n=== config.json content ===")
    cmd2 = "sudo -S cat /var/opt/kaspersky/ksc-web-console/server/config.json"
    stdin2, stdout2, stderr2 = client.exec_command(cmd2)
    stdin2.write(password + "\n")
    stdin2.flush()
    print(stdout2.read().decode('utf-8'))

    client.close()

if __name__ == "__main__":
    main()
