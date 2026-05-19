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

        # List files in /var/opt/kaspersky/ksc-web-console/server/
        stdin, stdout, stderr = client.exec_command(
            "ls -la /var/opt/kaspersky/ksc-web-console/server/"
        )
        print("--- /var/opt/kaspersky/ksc-web-console/server/ ---")
        print(stdout.read().decode("utf-8"))

        # List files in /var/opt/kaspersky/ksc-web-console/
        stdin, stdout, stderr = client.exec_command(
            "ls -la /var/opt/kaspersky/ksc-web-console/"
        )
        print("--- /var/opt/kaspersky/ksc-web-console/ ---")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
