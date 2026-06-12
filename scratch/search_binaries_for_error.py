import paramiko
import os
from dotenv import load_dotenv

def main():
    load_dotenv("configs/env/ksc_vars.env")
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())

    try:
        client.connect(host, username=user, password=password)
        print("Connected.")

        # Search for error text or 1459 recursively in /opt/kaspersky/
        cmd = "grep -rnI -E '1459|Two factor' /opt/kaspersky/ 2>/dev/null | head -n 40"
        stdin, stdout, stderr = client.exec_command(cmd)

        print("--- Grep /opt/kaspersky/ ---")
        print(stdout.read().decode("utf-8", errors="replace"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
