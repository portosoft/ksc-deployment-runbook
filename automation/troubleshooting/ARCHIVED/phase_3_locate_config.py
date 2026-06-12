import paramiko
import os
import sys


def phase_3_locate_config(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Locate config.json
        print("--- 3.1 Locating config.json ---")
        stdin, stdout, stderr = client.exec_command(
            'sudo -S find /etc/kaspersky /var/opt/kaspersky -name "config.json"'
        )
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    phase_3_locate_config(host, user, password)
