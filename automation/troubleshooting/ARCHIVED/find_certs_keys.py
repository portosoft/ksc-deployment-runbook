import paramiko
import os
import sys


def find_certificates(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Find certificates
        print("--- Certificates found ---")
        cmd = 'find /etc/kaspersky /var/opt/kaspersky -name "*.crt" 2>/dev/null'
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode("utf-8"))

        print("--- Keys found ---")
        cmd = 'find /etc/kaspersky /var/opt/kaspersky -name "*.key" 2>/dev/null'
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode("utf-8"))

        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    find_certificates(host, user, password)
