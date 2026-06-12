import paramiko
import os
import sys


def check_recent_journal(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Journal since 5 minutes ago
        print("--- Journal KSCWebConsole (Last 5m) ---")
        cmd = "sudo -S journalctl -u KSCWebConsole.service --since '5 minutes ago' --no-pager"
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

    check_recent_journal(host, user, password)
