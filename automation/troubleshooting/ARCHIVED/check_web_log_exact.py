import paramiko
import os
import sys


def check_web_log_exact(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Read the exact log file
        log_file = "/var/opt/kaspersky/ksc-web-console/logs/KSC-Web-Console-server.***REMOVED***.2026-05-09.log"
        print(f"--- Reading {log_file} ---")
        stdin, stdout, stderr = client.exec_command(f"sudo -S tail -n 100 {log_file}")
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

    check_web_log_exact(host, user, password)
