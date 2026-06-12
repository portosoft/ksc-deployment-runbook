import paramiko
import os
import sys


def search_web_port_deep(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search for port in server/
        print("--- Searching for 'port' in server/ ---")
        cmd = "grep -r 'port' /var/opt/kaspersky/ksc-web-console/server/ | grep -v 'node_modules' | head -n 50"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode("utf-8"))

        # Check pm.service-console.js existence
        print("--- Checking pm.service-console.js ---")
        stdin, stdout, stderr = client.exec_command(
            "ls -l /var/opt/kaspersky/ksc-web-console/pm.service-console.js"
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    search_web_port_deep(host, user, password)
