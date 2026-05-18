import paramiko
import os
import sys


def list_rpm_files(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # RPM list files
        print("--- RPM Files (First 50) ---")
        stdin, stdout, stderr = client.exec_command(
            "rpm -ql ksc-web-console | head -n 50"
        )
        print(stdout.read().decode("utf-8"))

        print("--- Checking for index.js in RPM ---")
        stdin, stdout, stderr = client.exec_command(
            'rpm -ql ksc-web-console | grep "server/index.js"'
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    list_rpm_files(host, user, password)
