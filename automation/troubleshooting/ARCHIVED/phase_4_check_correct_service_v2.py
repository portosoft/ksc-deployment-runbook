import paramiko
import os
import sys

def phase_4_check_correct_service_v2(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 4.1 Status
        print("--- 4.1 ksc-web-console.service Status ---")
        stdin, stdout, stderr = client.exec_command('sudo -S systemctl status ksc-web-console.service')
        stdin.write(password + '\n')
        stdin.flush()
        # Use stdout.read() directly to avoid decoding issues if possible, or decode with ignore
        print(stdout.read().decode('utf-8', errors='ignore'))

        # 4.2 Journal
        print("--- 4.2 Journal Logs (Last 50) ---")
        stdin, stdout, stderr = client.exec_command('sudo -S journalctl -u ksc-web-console.service --no-pager -n 50')
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8', errors='ignore'))

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    host = os.getenv("KSC_HOST")
    user = os.getenv("KSC_USER")
    password = os.getenv("KSC_PASS")

    phase_4_check_correct_service_v2(host, user, password)
