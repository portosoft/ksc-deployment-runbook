import paramiko
import os
import sys


def read_session_manager_more(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Read lines 50-150
        print("--- core-session-manager.js lines 50-150 ---")
        cmd = "sudo -S sed -n '50,150p' /var/opt/kaspersky/ksc-web-console/node_modules/@kl/openapi-module/lib/local/domains/session-manager/core-session-manager.js"
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

    read_session_manager_more(host, user, password)
