import paramiko
import os
import sys
import time

def phase_4_real_start(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Start
        print("--- 4.1 Starting ksc-web-console.service ---")
        stdin, stdout, stderr = client.exec_command('sudo -S systemctl start ksc-web-console.service')
        stdin.write(password + '\n')
        stdin.flush()

        print("Waiting 15 seconds...")
        time.sleep(15)

        # Status
        print("--- 4.1 Status ---")
        stdin, stdout, stderr = client.exec_command('sudo -S systemctl status ksc-web-console.service')
        stdin.write(password + '\n')
        stdin.flush()
        out = stdout.read().decode('utf-8', errors='ignore')
        print(out.encode('ascii', 'ignore').decode('ascii'))

        # Journal
        print("--- 4.2 Journal ---")
        stdin, stdout, stderr = client.exec_command('sudo -S journalctl -u ksc-web-console.service --no-pager -n 50')
        stdin.write(password + '\n')
        stdin.flush()
        out = stdout.read().decode('utf-8', errors='ignore')
        print(out.encode('ascii', 'ignore').decode('ascii'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    phase_4_real_start(host, user, password)
