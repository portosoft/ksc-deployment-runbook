import paramiko
import os
import sys


def check_rpm_integrity(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # RPM Verify
        stdin, stdout, stderr = client.exec_command(
            'rpm -V ksc-web-console | grep -E "^[SM5]{1,8}"'
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    check_rpm_integrity(host, user, password)
