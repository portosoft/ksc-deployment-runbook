import paramiko
import os
import sys

def analyze_setup_split_logic(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        # Search for split calls in setup.js with context
        print("--- Searching for 'split' logic in setup.js ---")
        cmd = "grep -oE '.{0,100}split.{0,100}' /var/opt/kaspersky/ksc-web-console/setup.js | head -n 100"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode('utf-8'))
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    
    analyze_setup_split_logic(host, user, password)
