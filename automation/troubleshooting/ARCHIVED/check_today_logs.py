import paramiko
import os
import sys

def check_today_logs(host, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, timeout=30)

        # Today's logs
        print("--- Today's Logs ---")
        stdin, stdout, stderr = client.exec_command("sudo -S ls -la /var/opt/kaspersky/ksc-web-console/logs/")
        stdin.write(password + '\n')
        stdin.flush()
        print(stdout.read().decode('utf-8'))

        # Journal
        print("--- Journal KSCWebConsole (Today) ---")
        stdin, stdout, stderr = client.exec_command("sudo -S journalctl -u KSCWebConsole.service -n 100 --no-pager")
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

    check_today_logs(host, user, password)
