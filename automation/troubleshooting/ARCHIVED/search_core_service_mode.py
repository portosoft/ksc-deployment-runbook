import paramiko
import os
import sys


def search_core_service_mode(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search for serviceMode in core/server.js
        print("--- Searching for serviceMode in core/server.js ---")
        cmd = "sudo -S grep -n 'serviceMode' /var/opt/kaspersky/ksc-web-console/server/core/server.js"
        stdin, stdout, stderr = client.exec_command(cmd)
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

    search_core_service_mode(host, user, password)
