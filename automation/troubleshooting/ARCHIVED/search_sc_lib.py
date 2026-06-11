import paramiko
import os
import sys


def search_sc_lib(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        cmd = "grep -r 'serviceConsole' /var/opt/kaspersky/ksc-web-console/node_modules/@kl/openapi-module/lib/local/ | head -n 20"
        stdin, stdout, stderr = client.exec_command(cmd)

        print(stdout.read().decode("utf-8"))
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    search_sc_lib(host, user, password)
