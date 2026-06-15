import os
import paramiko
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    admin_pass = os.getenv("KSC_ADMIN_PASS")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(host, username=user, password=password)

    print("=== Testing API Login ===")

    api_cmd = f"""ADMIN_PASS_B64=$(echo -n "{admin_pass}" | base64)
ADMIN_USER_B64=$(echo -n "KLAdmins" | base64)
curl -sk -o /dev/null -w "%{{http_code}}" \\
  -X POST https://127.0.0.1:13299/api/v1.0/login \\
  -H "Content-Type: application/json" \\
  -H "Authorization: KSCBasic user=\\"$ADMIN_USER_B64\\", pass=\\"$ADMIN_PASS_B64\\", internal=\\"1\\""
"""
    stdin, stdout, stderr = client.exec_command(api_cmd)
    print(stdout.read().decode('utf-8').strip())

    client.close()

if __name__ == "__main__":
    main()
