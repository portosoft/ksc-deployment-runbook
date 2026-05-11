import paramiko
import os
import sys

def find_servers_count_loc(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        # Check core/web-server.js
        print("--- Searching in core/web-server.js ---")
        stdin, stdout, stderr = client.exec_command("sudo -S grep -n 'serversCount' /var/opt/kaspersky/ksc-web-console/server/core/web-server.js")
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8'))

        # Check core/env-local/web-server.js
        print("--- Searching in core/env-local/web-server.js ---")
        stdin, stdout, stderr = client.exec_command("sudo -S grep -n 'serversCount' /var/opt/kaspersky/ksc-web-console/server/core/env-local/web-server.js")
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
    
    find_servers_count_loc(host, user, password)
