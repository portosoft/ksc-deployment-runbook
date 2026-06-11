import paramiko
import os
import sys


def check_latest_log_and_ports_sudo(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 1. Get latest log
        print("--- Latest Web Console Log ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S ls -t /var/opt/kaspersky/ksc-web-console/logs/KSC-Web-Console-server* | head -n 1"
        )
        stdin.write(password + "\n")
        stdin.flush()
        latest_log = stdout.read().decode("utf-8").strip()

        if latest_log:
            print(f"Reading: {latest_log}")
            stdin, stdout, stderr = client.exec_command(
                f"sudo -S tail -n 50 {latest_log}"
            )
            stdin.write(password + "\n")
            stdin.flush()
            print(stdout.read().decode("utf-8"))

        # 2. Check all ports
        print("--- All Listening Ports ---")
        stdin, stdout, stderr = client.exec_command("sudo -S ss -tulpn")
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

    check_latest_log_and_ports_sudo(host, user, password)
