import paramiko
import os
import sys


def find_nats(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        print("--- Searching for nats-server ---")
        cmd = 'find /var/opt/kaspersky/ksc-web-console -name "nats-server" -type f'
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode("utf-8"))

        print("--- Checking systemd for nats ---")
        cmd = "sudo -S systemctl list-units --all | grep nats"
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

    find_nats(host, user, password)
