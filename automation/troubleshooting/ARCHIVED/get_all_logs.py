import paramiko
import os
import sys


def get_logs(host, user, password, since):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        print(f"--- NATS Logs since {since} ---")
        cmd_nats = (
            f'sudo -S journalctl -u ksc-nats.service --since "{since}" --no-pager'
        )
        stdin, stdout, stderr = client.exec_command(cmd_nats)
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        print(f"--- Web Console Logs since {since} ---")
        cmd_web = f'sudo -S journalctl -u ksc-web-console.service --since "{since}" --no-pager'
        stdin, stdout, stderr = client.exec_command(cmd_web)
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

    get_logs(host, user, password, "14:14:00")
