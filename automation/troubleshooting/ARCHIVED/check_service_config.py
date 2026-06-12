import paramiko
import os
import sys


def check_service_config(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # List files
        print("--- /var/opt/kaspersky/ksc-web-console Content ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -F /var/opt/kaspersky/ksc-web-console/"
        )
        print(stdout.read().decode("utf-8"))

        # Read unit file
        print("--- /etc/systemd/system/ksc-web-console.service ---")
        stdin, stdout, stderr = client.exec_command(
            "cat /etc/systemd/system/ksc-web-console.service"
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    check_service_config(host, user, password)
