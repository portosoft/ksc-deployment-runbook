import paramiko
import os
import sys


def find_node_binary(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Find node
        print("--- Node binary location ---")
        stdin, stdout, stderr = client.exec_command(
            'find /var/opt/kaspersky/ksc-web-console -name "node" -type f'
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    find_node_binary(host, user, password)
