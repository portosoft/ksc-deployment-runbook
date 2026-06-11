import paramiko
import os
import sys


def check_web_server_core_sudo(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # List files
        print("--- Listing server/core/web-server/ ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S ls -la /var/opt/kaspersky/ksc-web-console/server/core/web-server/"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        # Read index.js or web-server.js
        print("--- Reading server/core/web-server/index.js ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cat /var/opt/kaspersky/ksc-web-console/server/core/web-server/index.js"
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

    check_web_server_core_sudo(host, user, password)
