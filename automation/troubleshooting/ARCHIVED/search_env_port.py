import paramiko
import os
import sys

def search_env_port(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search for process.env.PORT or similar
        print("--- Searching for port variables in server/ ---")
        cmds = [
            "grep -r 'process.env.PORT' /var/opt/kaspersky/ksc-web-console/server/ | grep -v 'node_modules'",
            "grep -r 'port' /var/opt/kaspersky/ksc-web-console/server/ | grep -v 'node_modules' | head -n 50"
        ]

        for cmd in cmds:
            print(f"--- {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    search_env_port(host, user, password)
