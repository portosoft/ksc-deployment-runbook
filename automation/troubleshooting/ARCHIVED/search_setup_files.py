import paramiko
import os
import sys

def search_setup_files(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search for any setup files
        print("--- Searching for setup files ---")
        cmd = "sudo find /opt/kaspersky /var/opt/kaspersky /usr/bin /usr/sbin -iname '*setup*' -o -iname '*postinstall*'"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    search_setup_files(host, user, password)
