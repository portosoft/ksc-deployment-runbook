import paramiko
import os
import sys

def check_ksc_setup_pl(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        # Check for Web Console references in ksc_setup.pl
        print("--- Reading ksc_setup.pl ---")
        stdin, stdout, stderr = client.exec_command("grep -i 'web' /opt/kaspersky/ksc64/lib/bin/setup/ksc_setup.pl")
        print(stdout.read().decode('utf-8'))
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    
    check_ksc_setup_pl(host, user, password)
