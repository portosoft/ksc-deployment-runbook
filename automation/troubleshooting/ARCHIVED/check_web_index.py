import paramiko
import os
import sys


def check_web_index(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Read the first few lines of index.js
        print("--- Reading index.js ---")
        stdin, stdout, stderr = client.exec_command(
            "head -n 50 /var/opt/kaspersky/ksc-web-console/index.js"
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    check_web_index(host, user, password)
