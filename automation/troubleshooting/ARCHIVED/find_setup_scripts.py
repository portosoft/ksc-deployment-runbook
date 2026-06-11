import paramiko
import os
import sys


def find_setup_scripts(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Find setup scripts
        print("--- Potential Setup Scripts ---")
        stdin, stdout, stderr = client.exec_command(
            'find /opt /var/opt -name "*setup*" -executable -type f 2>/dev/null'
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    find_setup_scripts(host, user, password)
