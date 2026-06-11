import paramiko
import os
import sys


def read_server_js(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        print("--- server/core/server.js (190-220) ---")
        cmd = (
            'sed -n "190,220p" /var/opt/kaspersky/ksc-web-console/server/core/server.js'
        )
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    read_server_js(host, user, password)
