import paramiko
import os
import sys

def check_web_console_connectivity(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        # Check ports and curl
        print("--- Checking Web Console Connectivity ---")
        cmds = [
            "sudo -S ss -tulpn | grep node",
            "curl -Ik https://localhost:8080",
            "curl -Ik https://127.0.0.1:8080"
        ]
        
        for cmd in cmds:
            print(f"--- {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            if "sudo" in cmd:
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
    
    check_web_console_connectivity(host, user, password)
