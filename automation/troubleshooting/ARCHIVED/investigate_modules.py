import paramiko
import os
import sys


def investigate_modules(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Check node_modules
        print("--- node_modules/@kl/ content ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -F /var/opt/kaspersky/ksc-web-console/node_modules/@kl/"
        )
        print(stdout.read().decode("utf-8"))

        # Check pm.js content around line 15
        print("--- pm.js lines 10-30 ---")
        stdin, stdout, stderr = client.exec_command(
            'sed -n "10,30p" /var/opt/kaspersky/ksc-web-console/pm.js'
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    investigate_modules(host, user, password)
