import paramiko
import os
import sys

def check_init_log(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        # Check for init log
        print("--- Init Log Check ---")
        cmd = "sudo -S grep 'Start to init server' /var/opt/kaspersky/ksc-web-console/logs/KSC-Web-Console-server.***REMOVED***.2026-05-09.log | tail -n 10"
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
    
    check_init_log(host, user, password)
