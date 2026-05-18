import paramiko
import os
import sys


def search_code(host, user, password, query):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search in the whole project directory
        cmd = f"grep -r '{query}' /var/opt/kaspersky/ksc-web-console/ 2>/dev/null | head -n 20"
        stdin, stdout, stderr = client.exec_command(cmd)

        print(stdout.read().decode("utf-8"))
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    search_code(host, user, password, "NATS_CONNECTION_CREATOR")
