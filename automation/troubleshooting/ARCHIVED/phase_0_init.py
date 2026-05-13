import paramiko
import os
import sys

def phase_0_init(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 0.1 Sync clock
        print("--- 0.1 Timedatectl Status ---")
        stdin, stdout, stderr = client.exec_command('sudo -S timedatectl set-ntp true; timedatectl status')
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8'))

        # 0.2 Check logs
        print("--- 0.2 Log Files (Internal) ---")
        stdin, stdout, stderr = client.exec_command('find /var/opt/kaspersky/ksc-web-console -name "*.log" -type f 2>/dev/null | head -20')
        print(stdout.read().decode('utf-8'))

        print("--- 0.2 Log Files (System) ---")
        stdin, stdout, stderr = client.exec_command('ls -lh /var/log/kaspersky/ 2>/dev/null')
        print(stdout.read().decode('utf-8'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    phase_0_init(host, user, password)
