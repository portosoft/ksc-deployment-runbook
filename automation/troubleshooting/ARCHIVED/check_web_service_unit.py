import paramiko
import os
import sys


def check_web_service_unit_fixed(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Read the systemd service unit
        print("--- Reading ksc-web-console.service ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cat /etc/systemd/system/ksc-web-console.service"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        # Check for setup scripts in the binary path
        print("--- Checking for setup scripts ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -la /var/opt/kaspersky/ksc-web-console/setup.js"
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    check_web_service_unit_fixed(host, user, password)
