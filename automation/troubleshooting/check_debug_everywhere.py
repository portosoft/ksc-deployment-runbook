import paramiko
import os
import sys

def check_debug_everywhere(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        # Check files
        print("--- Checking web-server.js modification ---")
        stdin, stdout, stderr = client.exec_command("sudo -S grep 'DEBUG' /var/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js")
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8'))

        # Check logs
        print("--- Searching for DEBUG in ALL logs ---")
        stdin, stdout, stderr = client.exec_command("sudo -S grep -r 'DEBUG' /var/opt/kaspersky/ksc-web-console/logs/")
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
    
    check_debug_everywhere(host, user, password)
