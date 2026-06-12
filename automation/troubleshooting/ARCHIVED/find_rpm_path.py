import paramiko
import os
import sys


def find_rpm_path(host, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Find RPM
        print("--- Searching for ksc-web-console RPM ---")
        # Search in common download/home dirs first to be faster
        stdin, stdout, stderr = client.exec_command(
            'find /home /tmp /var/cache -name "ksc-web-console*.rpm" 2>/dev/null'
        )
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    find_rpm_path(host, user, password)
