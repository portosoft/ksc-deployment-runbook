import paramiko
import os
import sys


def find_root_ca(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Check specific certificate directory
        print("--- Checking /opt/kaspersky/ksc64/var/cert/ ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -l /opt/kaspersky/ksc64/var/cert/ 2>/dev/null"
        )
        print(stdout.read().decode("utf-8"))

        # Check etc/kaspersky/
        print("--- Checking /etc/kaspersky/ ---")
        stdin, stdout, stderr = client.exec_command("ls -R /etc/kaspersky/ 2>/dev/null")
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    find_root_ca(host, user, password)
