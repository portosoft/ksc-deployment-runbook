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

    print("=== Searching for ksciam in installer logs ===")
    cmd = "sudo grep -ri 'ksciam' /var/log/kaspersky/ /opt/kaspersky/ksc64/ /var/opt/kaspersky/ | head -n 50"
    stdin, stdout, stderr = client.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode('utf-8'))

    print("\n=== Searching for kladduser in installer logs ===")
    cmd2 = "sudo grep -ri 'kladduser' /var/log/kaspersky/ /opt/kaspersky/ksc64/ /var/opt/kaspersky/ | head -n 50"
    stdin, stdout, stderr = client.exec_command(cmd2)
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode('utf-8'))

    client.close()

if __name__ == "__main__":
    main()
