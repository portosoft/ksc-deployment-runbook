import paramiko
import os
import sys

def check_ksc_systemd_units(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        # Check systemd units
        print("--- Checking KSC Systemd Units ---")
        cmds = [
            "ls /etc/systemd/system/KSC*",
            "ls /usr/lib/systemd/system/KSC*",
            "sudo -S cat /etc/systemd/system/ksc-web-console.service"
        ]
        
        for cmd in cmds:
            print(f"--- {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            if "sudo" in cmd:
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
    
    check_ksc_systemd_units(host, user, password)
