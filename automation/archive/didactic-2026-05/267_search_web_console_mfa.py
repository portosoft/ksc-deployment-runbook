import paramiko
import os
from dotenv import load_dotenv


def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Grep inside the web console folder
        cmd = "grep -rnI -E 'totp|totpreg|mfa' /var/opt/kaspersky/ksc-web-console/server/ /var/opt/kaspersky/ksc-web-console/web-server.js /var/opt/kaspersky/ksc-web-console/index.js 2>/dev/null | head -n 50"
        stdin, stdout, stderr = client.exec_command(cmd)

        print("--- Grep Matches ---")
        print(stdout.read().decode("utf-8", errors="replace"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
