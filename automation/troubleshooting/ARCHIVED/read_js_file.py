import paramiko
import os
import sys


def read_file_utf8(host, user, password, filepath):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        cmd = f"cat {filepath}"
        stdin, stdout, stderr = client.exec_command(cmd)

        # Read as bytes and decode as utf-8, ignoring errors
        content = stdout.read().decode("utf-8", errors="ignore")
        print(content)
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    filepath = "/var/opt/kaspersky/ksc-web-console/node_modules/@kl/app-components-connector/lib/nats/connection-creator.js"
    read_file_utf8(host, user, password, filepath)
