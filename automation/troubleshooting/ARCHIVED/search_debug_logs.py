import paramiko
import os
import sys


def search_debug_logs(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search for DEBUG in today's log
        print("--- Searching for DEBUG in today's log ---")
        cmd = "sudo -S grep 'DEBUG' /var/opt/kaspersky/ksc-web-console/logs/KSC-Web-Console-server.***REMOVED***.2026-05-11.log | tail -n 20"
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

    search_debug_logs(host, user, password)
