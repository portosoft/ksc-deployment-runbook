import paramiko
import os
import sys

def check_ksc_users(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        # List users related to KSC
        print("--- Listing KSC related users ---")
        stdin, stdout, stderr = client.exec_command("grep -iE 'ksc|kl|kaspersky' /etc/passwd")
        print(stdout.read().decode('utf-8'))
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    
    check_ksc_users(host, user, password)
