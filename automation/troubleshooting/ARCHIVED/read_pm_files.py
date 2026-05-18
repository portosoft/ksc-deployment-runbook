import paramiko
import os
import sys


def read_pm_files(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Read pm.js
        print("--- pm.js ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cat /var/opt/kaspersky/ksc-web-console/pm.js"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        # Read pm.service-console.js
        print("--- pm.service-console.js ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cat /var/opt/kaspersky/ksc-web-console/pm.service-console.js"
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

    read_pm_files(host, user, password)
