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

    print("=== Checking rows in ksciam ===")
    queries = [
        "SELECT COUNT(*) FROM iam.accounts;",
        "SELECT COUNT(*) FROM iam.service_accounts;",
        "SELECT COUNT(*) FROM iam.external_accounts;"
    ]
    for q in queries:
        cmd = f'sudo -S -u postgres psql -d ksciam -c "{q}"'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + "\n")
        stdin.flush()
        print(f"Query: {q} | Output: {stdout.read().decode().strip()}")

    client.close()

if __name__ == "__main__":
    main()
