import paramiko
import os
import sys

def search_listen_in_logs(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Search for listen or server in logs
        print("--- Searching for 'listen' or 'server' in logs ---")
        cmd = "sudo -S grep -riE 'listen|server' /var/opt/kaspersky/ksc-web-console/logs/ | grep -v 'NATS' | tail -n 50"
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

    search_listen_in_logs(host, user, password)
