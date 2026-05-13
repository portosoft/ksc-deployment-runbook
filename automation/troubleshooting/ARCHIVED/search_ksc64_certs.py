import paramiko
import os
import sys

def search_klserver_certs(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search for certificates in var/opt/kaspersky/ksc64
        print("--- Searching /var/opt/kaspersky/ksc64/ ---")
        # Use find with sudo
        cmd = 'sudo -S find /var/opt/kaspersky/ksc64/ -name "*.crt" -o -name "*.key" 2>/dev/null'
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + '\n')
        stdin.flush()

        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    search_klserver_certs(host, user, password)
