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

    print("=== Checking ksciam users ===")
    query = "SELECT * FROM iam.users LIMIT 10;"
    cmd = f'sudo -S -u postgres psql -d ksciam -c "{query}"'
    stdin, stdout, stderr = client.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))

    client.close()

if __name__ == "__main__":
    main()
