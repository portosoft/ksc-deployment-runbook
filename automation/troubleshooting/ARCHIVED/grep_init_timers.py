import paramiko
import os
import sys


def grep_init_timers(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Grep
        print("--- Searching for initClientIdleTimersCheck ---")
        cmd = "sudo -S grep -r 'initClientIdleTimersCheck' /var/opt/kaspersky/ksc-web-console/"
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

    grep_init_timers(host, user, password)
