import paramiko
import os
import sys


def get_full_logs(host, user, password, since):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        cmd = f'sudo -S journalctl -u ksc-web-console.service --since "{since}" --no-pager'
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

    get_full_logs(host, user, password, "14:14:00")
