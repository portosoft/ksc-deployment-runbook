import paramiko
import os
import sys


def read_service_files(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Read KSCWebConsole.service
        print("--- KSCWebConsole.service ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cat /etc/systemd/system/KSCWebConsole.service"
        )
        stdin.write(password + "\n")
        stdin.flush()
        print(stdout.read().decode("utf-8"))

        # Read KSCSvcWebConsole.service
        print("--- KSCSvcWebConsole.service ---")
        stdin, stdout, stderr = client.exec_command(
            "sudo -S cat /etc/systemd/system/KSCSvcWebConsole.service"
        )
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

    read_service_files(host, user, password)
