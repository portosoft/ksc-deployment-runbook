import paramiko
import os
import sys


def find_executable_rpm_files(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Find executable files in the RPM
        print("--- Finding executable files in ksc-web-console RPM ---")
        cmd = "rpm -ql ksc-web-console | xargs sudo ls -Fd | grep '*'"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    find_executable_rpm_files(host, user, password)
