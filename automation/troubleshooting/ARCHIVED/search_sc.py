import paramiko
import os
import sys


def search_service_console(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search for where serviceConsole module is defined
        cmd = "grep -r 'serviceConsole' /var/opt/kaspersky/ksc-web-console/server/ | head -n 50"
        stdin, stdout, stderr = client.exec_command(cmd)

        print(stdout.read().decode("utf-8"))
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    search_service_console(host, user, password)
