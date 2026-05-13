import paramiko
import os
import sys

def phase_3_infra_test(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # 3.3 Connectivity
        print("--- 3.3 Connectivity Test (Port 13299) ---")
        stdin, stdout, stderr = client.exec_command('curl -k https://127.0.0.1:13299 -o /dev/null -w "%{http_code}" 2>/dev/null')
        print(f"HTTP Code: {stdout.read().decode('utf-8')}")

        # 3.4 Admin Server Status
        print("\n--- 3.4 kladminserver Status ---")
        stdin, stdout, stderr = client.exec_command('sudo -S systemctl status kladminserver')
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8'))

        print("\n--- 3.4 Listening Ports ---")
        stdin, stdout, stderr = client.exec_command('sudo -S ss -tlnp | grep -E "13000|13299"')
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

    phase_3_infra_test(host, user, password)
