import paramiko
import os
import sys


def check_logs_and_lsof(host, user, password, pid):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # List logs
        print("--- Logs directory ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S ls -la /var/opt/kaspersky/ksc-web-console/logs/"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        # Lsof
        print(f"--- Lsof for PID {pid} ---")
        stdin, stdout, stderr = client.exec_command(f"sudo -S lsof -p {pid} | grep log")
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
    pid = "222832"

    check_logs_and_lsof(host, user, password, pid)
