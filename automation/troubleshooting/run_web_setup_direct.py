import paramiko
import os
import sys

def run_web_setup_direct(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        # Run setup.js with node
        print("--- Running Web Console setup.js --help ---")
        cmd = "sudo -S /var/opt/kaspersky/ksc-web-console/node /var/opt/kaspersky/ksc-web-console/setup.js --help"
        stdin, stdout, stderr = client.exec_command(cmd)
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")
    
    run_web_setup_direct(host, user, password)
