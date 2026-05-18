import paramiko
import os
import sys


def list_rpm_binaries(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # RPM binaries
        print("--- Binaries in RPM ---")
        cmd = 'rpm -ql ksc-web-console | grep -E "/bin/|/sbin/"'
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    list_rpm_binaries(host, user, password)
