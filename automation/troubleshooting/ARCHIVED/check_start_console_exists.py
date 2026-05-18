import paramiko
import os
import sys


def check_start_console_exists(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Check start-console.sh size and existence
        print("--- Checking start-console.sh ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -l /var/opt/kaspersky/ksc-web-console/start-console.sh"
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    check_start_console_exists(host, user, password)
